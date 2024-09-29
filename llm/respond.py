from typing import Dict, List, Any, Type
from abc import ABC, abstractmethod
import django_rq
from channels.models import Message
import pytz
from datetime import datetime
from rq.job import Job
import inspect

from config.settings import SYSTEM_PROMPT, PRODUCTION, BASE_DIR

from llm.anthropic_integration import get_message, get_basic_message

from tools.config import TOOL_DEFINITIONS
from tools.search import get_search_data
from tools.browse import get_web_page_content
from tools.google.docs import append_text, read_document
from tools.github.pull_requests import open_pull_request
from tools.github.issues import create_github_issue, read_github_issue



def get_current_time():
    est = pytz.timezone('US/Eastern')
    est_time = datetime.now(est)
    return est_time.strftime('%B %d, %Y, %I:%M %p')


def get_runtime_environment():
    return 'PRODUCTION' if PRODUCTION else 'DEVELOPMENT'


def approximate_token_count(text):
    return int(len(text.split()) / 0.75)


def summarize_content(system_prompt, content):
    message = get_basic_message(
        system_prompt,
        [{"role": "user", "content": content}]
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

# AI: TOOL RESPONDERS

# These classes are used to define the tools that the AI can use to respond to user requests.
# Each tool is a class that inherits from BaseTool and implements the execute method.
class BaseTool(ABC):
    def __init__(self, input_keys: List[str] = None, immediate: bool = False):
        self.input_keys = input_keys or []
        self.immediate = immediate

    @abstractmethod
    def execute(self, request_data: Dict[str, Any]) -> str:
        pass
class GetTimeTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.immediate = True

    def execute(self, _):
        return f"current time: {get_current_time()}"

class GetRuntimeEnvironmentTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.immediate = True

    def execute(self, request_data):
        return get_runtime_environment()

class GetSearchResultsTool(BaseTool):
    def __init__(self):
        super().__init__(["query"])

    def execute(self, request_data):
        request_data['content'] = summarize_content(
            f"""
            Respond to the user's query {request_data['query']} concisely and accurately.
            Based on the search results provided in the message. Limit your response
            to a maximum of 2000 characters.
            """,
            get_search_data(request_data['query'])
        )
        return request_data

class GetWebPageSummaryTool(BaseTool):
    def __init__(self):
        super().__init__(["url"])

    def execute(self, request_data):
        request_data['content'] = summarize_content(
            request_data['ai_agent_system_prompt'],
            get_web_page_content(request_data['url'])
        )
        return request_data

class ReadGoogleDocumentTool(BaseTool):
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

class ReadSystemArchitectureTool(BaseTool):
    def __init__(self):
        super().__init__(["query"])
        # self.immediate = True

    def execute(self, request_data):
        print('Reading system architecture')
        print(f"Considering user's request {request_data['query']}")
        with open(f'{BASE_DIR}/project_overview.ai', 'r') as file:
            project_overview = file.read()
        message = get_basic_message(
            request_data['query'],
            [{ "role": "user", "content": project_overview }]
        )
        tool_sequence = request_data['tool_sequence']
        new_tool_sequence = [t for t in tool_sequence if t.name != "read_system_architecture"]
        request_data['tool_sequence'] = new_tool_sequence
        if len(request_data['tool_sequence']) > 0:
            request_data['content'] = message.content[0].text
        else:
            request_data['content'] = message.content[0].text[:2000]
        return request_data

class UpdateGoogleDocumentTool(BaseTool):
    def __init__(self):
        super().__init__(["google_doc_id", "content"])

    def execute(self, request_data):
        document_content_object = read_document(request_data['google_doc_id'])
        print(f"Document content object: {document_content_object}")
        system_prompt = f"""
        AI AGENT SYSTEM PROMPT: {request_data['ai_agent_system_prompt']}
        CURRENT_DOCUMENT_CONTENT: {document_content_object}
        Respond to the user's request to update the Google document with just the 
        new content and no other information. Limit your response to a maximum of 2000 characters.
        """
        message = get_basic_message(system_prompt, [
            {
                "role": "user",
                "content": request_data['content']
            }
        ])
        response_text = message.content[0].text
        try:
            print(f"Updating document with text: google_doc_id ")
            append_text(request_data['google_doc_id'], response_text)
        except Exception as e:
            print(f"Error updating document: {e}")
            request_data['content'] = "Error updating document."

        request_data['content'] = "Document updated."
        return request_data

class OpenPullRequestTool(BaseTool):
    def __init__(self):
        super().__init__(["title", "description"])

    def execute(self, request_data):
        print(f"Opening pull request with title: {request_data['title']}")
        print(f"Opening pull request with description: {request_data['description']}")
        try:
            request_data['content'] =  open_pull_request(request_data)
        except Exception as e:
            print(f"Error opening pull request: {e}")
            request_data['content'] = "Error opening pull request."
        return request_data
    
class GetBackgroundJobsTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.immediate = True

    def execute(self, request_data):
        print("Getting background jobs")
        message_queue = django_rq.get_queue("default")
        job_ids = message_queue.started_job_registry.get_job_ids()
        if len(job_ids) == 0:
            return "Not working on anything at the moment."
        else:
            summary = f"Task count: {len(job_ids)}\n"
            jobs = Job.fetch_many(job_ids, connection=message_queue.connection)
            for job in jobs:
                summary += job.args[0]['content']
            return summary

class CreateGithubIssueTool(BaseTool):
    def __init__(self):
        super().__init__(["title", "description"])

    def execute(self, request_data):
        request_data['content'] = create_github_issue(request_data)
        return request_data
    

class AnalyzeGithubIssueTool(BaseTool):
    def __init__(self):
        super().__init__(["issue_number", "issue_url", "description"])

    def execute(self, request_data):
        title, body = read_github_issue(request_data)
        prompt = create_system_prompt(
            request_data['ai_agent_system_prompt'],
            """
            Acknowledged the user's request to address the GitHub issue.
            Respond with your current understanding of the issue.
            """
        )
        message = get_basic_message(
            prompt,
            [
                {
                    "role": "user",
                    "content": f"""
                    User request: {request_data['description']}
                    Title: {title}
                    Description: {body}
                    """
                }
            ]
        )
        request_data['content'] = message.content[0].text
        return request_data

# AI ADD CLASSES HERE

class ToolRegistry:
    """
    The ToolRegistry class is used to register and manage the tools that the AI
    can use to respond to user requests. It automatically registers all classes
    that inherit from BaseTool in the current module.
    """
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def register(self, name: str, tool: BaseTool):
        self.tools[name] = tool

    def get(self, name: str) -> BaseTool:
        return self.tools.get(name)

    def auto_register_tools(self):
        # Get all classes in the current module that inherit from BaseTool
        tool_classes = {name: cls for name, cls in globals().items() 
                        if inspect.isclass(cls) and issubclass(cls, BaseTool) and cls != BaseTool}
        
        for tool_def in TOOL_DEFINITIONS:
            tool_name = tool_def['name']
            class_name = ''.join(word.capitalize() for word in tool_name.split('_')) + 'Tool'
            
            if class_name in tool_classes:
                tool_class = tool_classes[class_name]
                tool_instance = tool_class()
                self.register(tool_name, tool_instance)
            else:
                print(f"Warning: No matching class found for tool '{tool_name}'")

    def handle_tool_use(self, ai_agent, request_data):
        tool_call = request_data['tool']
        tool = self.get(tool_call.name)
        if not tool:
            return f"Unknown tool: {tool_call.name}"

        for key in tool.input_keys:
            if key in tool_call.input:
                request_data[key] = tool_call.input[key]

        print(f"Executing tool: {tool_call.name}")
        if tool.immediate:
            print("Executing tool immediately")
            return tool.execute(request_data)

        enqueue_result = django_rq.enqueue(tool.execute, request_data)
        if isinstance(enqueue_result, str):
            return enqueue_result
        elif hasattr(enqueue_result, 'id'):
            ai_agent.add_job(enqueue_result.id)
            ai_agent.save()
            response_text = f"""
            State that you are using the {tool_call.name} in a concise and natural way.
            """
            response = ai_agent.respond_to_user(response_text)
            return f"{response}\nJOB ID: {enqueue_result.id}"
        else:
            return "Processing started"

# Initialize the tool registry
tool_registry = ToolRegistry()
tool_registry.auto_register_tools()

def generate_immediate_response(ai_agent, tool_blocks, request_data):
    tool_names = ", ".join([tool.name for tool in tool_blocks])
    tool_summary_message = get_basic_message(
        f"""
        {ai_agent.description}
        
        Acknowledge the user's request {request_data['content']} and
        indicate that you are using the tool names provided. Your response
        should sound natural and concise and not mention the tool names explicitly.
        It should convey they you will be working on this and it may take some time.
        """,
        [
            { "role": "user", "content": tool_names }
        ]
    )
    return tool_summary_message.content[0].text


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
    response_text = ""

    response_message = get_message(
        ai_agent.description,
        TOOL_DEFINITIONS,
        [{ "role": "user", "content": request_data['content'] }],
    )

    text_contents = []
    tool_contents = []
    tool_sequence = []

    for content in response_message.content:
        if content.type == "text":
            text_contents.append(content.text)
        elif content.type == "tool_use":
            tool_contents.append(content)

    if len(tool_contents) > 0:
        try:
            request_data["tool"] = tool_contents[0]
            request_data["tool_sequence"] = tool_contents[1:]
            tool_result = tool_registry.handle_tool_use(ai_agent, request_data)
            text_contents.append(tool_result)
        except Exception as e:
            print(f"Error processing tool: {e}")
            text_contents.append("Error processing tool")
  
    for content in text_contents:
        print(content)
    
    return "\n".join(text_contents)

