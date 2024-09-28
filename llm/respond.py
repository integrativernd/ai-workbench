from functools import wraps
from typing import Dict, Callable, Any, List
import django_rq
from channels.models import Message, Channel
from llm.anthropic_integration import get_message, get_basic_message
from config.settings import TOOL_DEFINITIONS, SYSTEM_PROMPT, PRODUCTION, BASE_DIR
from tools.search import get_search_data
from tools.browse import get_web_page_content
from tools.google.docs import append_text, read_document
import time
import pytz
from datetime import datetime
from rq.job import Job

# Config
# RESPONSE_KEYS = ['channel_id', 'ai_agent_name']

def get_current_time():
    est = pytz.timezone('US/Eastern')
    est_time = datetime.now(est)
    return est_time.strftime('%B %d, %Y, %I:%M %p')


def get_runtime_environment():
    return 'PRODUCTION' if PRODUCTION else 'DEVELOPMENT'


def approximate_token_count(text):
    return int(len(text.split()) / 0.75)


def summarize_content(content):
    message = get_basic_message(
        SYSTEM_PROMPT,
        [{"role": "user", "content": f"Summarize all content from the user as a short list of bullets.\n{content}"}]
    )
    return message.content[0].text


def create_system_prompt(base_prompt, additional_context=""):
    return f"""
    BASE_PROMPT
    {base_prompt}
    BACKGROUND_PROCESS
    You are at the point in the response cycle where you need to generate the content
    to address the user's request. You are in a running background process and 
    you can respond in a single response in the slack thread with a maximum of 2000 characters.
    {additional_context}
    """

class BaseTool:
    def __init__(self, input_keys: List[str] = None):
        self.input_keys = input_keys or []

    def execute(self, request_data):
        raise NotImplementedError("Subclasses must implement execute method")

class DataTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.immediate = True

    def execute(self, _):
        return get_current_time()

class RunTimeEnvironmentTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.immediate = True

    def execute(self, request_data):
        return get_runtime_environment()

class SearchTool(BaseTool):
    def __init__(self):
        super().__init__(["query"])

    def execute(self, request_data):
        request_data['content'] = summarize_content(get_search_data(request_data['query']))
        return request_data

class BrowseTool(BaseTool):
    def __init__(self):
        super().__init__(["url"])

    def execute(self, request_data):
        request_data['content'] = summarize_content(get_web_page_content(request_data['url']))
        return request_data

class ReadGoogleDocTool(BaseTool):
    def __init__(self):
        super().__init__(["google_doc_id"])

    def execute(self, request_data):
        prompt = create_system_prompt(request_data['ai_agent_system_prompt'])
        message = get_basic_message(
            prompt,
            [{ "role": "user", "content": read_document(request_data['google_doc_id']) }]
        )
        request_data['content'] = message.content[0].text
        return request_data

class ReadProjectOverviewTool(BaseTool):
    def __init__(self):
        super().__init__(["query"])

    def execute(self, request_data):
        with open(f'{BASE_DIR}/project_overview.ai', 'r') as file:
            project_overview = file.read()
        prompt = create_system_prompt(
            request_data['ai_agent_system_prompt'],
            f"This is what the user requested {request_data['query']}"
        )
        message = get_basic_message(
            prompt,
            [{ "role": "user", "content": project_overview }]
        )
        request_data['content'] = message.content[0].text
        return request_data

class UpdateGoogleDocTool(BaseTool):
    def __init__(self):
        super().__init__(["google_doc_id", "content"])

    def execute(self, request_data):
        document_content_data = read_document(request_data['google_doc_id'])
        prompt = create_system_prompt(
            request_data['ai_agent_system_prompt'],
            f"CURRENT DOCUMENT CONTENT JSON DATA\n{document_content_data}"
        )
        message = get_basic_message(prompt, request_data['content'])
        append_text(request_data['google_doc_id'], message.content[0].text)
        request_data['content'] = "Document updated."
        return request_data

class AnalyzeUserInputTool(BaseTool):
    def __init__(self):
        super().__init__(["task"])

    def execute(self, request_data):
        print(f"Analyzing request: {request_data}")
        time.sleep(20)
        request_data['content'] = "Background job finished"
        return request_data

class BasicResponseTool(BaseTool):
    def __init__(self):
        super().__init__(["prompt", "max_tokens"])

    def execute(self, request_data):
        message = get_basic_message(SYSTEM_PROMPT, [{"role": "user", "content": request_data["prompt"]}])
        request_data['content'] = message.content[0].text
        return request_data

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def register(self, name: str, tool: BaseTool):
        self.tools[name] = tool

    def get(self, name: str) -> BaseTool:
        return self.tools.get(name)

    def handle_tool_use(self, ai_agent, tool_call, request_data):
        print(f"Handling tool use: {tool_call.name}")

        tool = self.get(tool_call.name)
        if not tool:
            return f"Unknown tool: {tool_call.name}"
        
        for key in tool.input_keys:
            if key in tool_call.input:
                request_data[key] = tool_call.input[key]

        if hasattr(tool, 'immediate') and tool.immediate:
            return tool.execute(request_data)
        
        result = django_rq.enqueue(tool.execute, request_data)
        print(f"Background job started: {result.id}")
        if isinstance(result, str):
            return result
        elif hasattr(result, 'id'):
            ai_agent.add_job(result.id)
            ai_agent.save()
            response = ai_agent.respond_to_user(f"""
                State that you are using the {tool_call.name} in a concise and natural way.
            """)
            return f"{response}: {result.id}"
        else:
            return "Processing started"

# Initialize the tool registry
tool_registry = ToolRegistry()

# Register tools
tool_registry.register("get_time", DataTool())
tool_registry.register("get_runtime_environment", RunTimeEnvironmentTool())
tool_registry.register("create_background_job", AnalyzeUserInputTool())
tool_registry.register("get_search_results", SearchTool())
tool_registry.register("get_web_page_summary", BrowseTool())
tool_registry.register("update_google_document", UpdateGoogleDocTool())
tool_registry.register("get_basic_response", BasicResponseTool())
tool_registry.register("read_google_document", ReadGoogleDocTool())
tool_registry.register("read_project_overview", ReadProjectOverviewTool())

def get_background_jobs():
    message_queue = django_rq.get_queue("default")
    job_ids = message_queue.started_job_registry.get_job_ids()
    if len(job_ids) == 0:
        return "Nothing"
    else:
        summary = ""
        for job_id in job_ids:
            job = Job.fetch(job_id, connection=message_queue.connection)
            summary += f"Job ID: {job.id}, Status: {job.args[0]}"
    return summary

tool_registry.register("get_background_jobs", BaseTool())

def persist_message(channel, request_data):
    try:
        Message.objects.create(
            channel=channel,
            author=request_data['author'],
            content=request_data['content'],
        )
    except Exception as e:
        print(f"Error saving message: {e}")

def respond(ai_agent, channel, request_data):
    persist_message(channel, request_data)

    response_message = get_message(
        ai_agent.description,
        TOOL_DEFINITIONS,
        [{ "role": "user", "content": request_data['content'] }],
    )
    
    full_response = ""
    for content in response_message.content:
        if content.type == "text":
            full_response += content.text
        elif content.type == "tool_use":
            tool_result = tool_registry.handle_tool_use(ai_agent, content, request_data)
            full_response += tool_result

    persist_message(channel, { "author": ai_agent.name, "content": full_response })
    return full_response
