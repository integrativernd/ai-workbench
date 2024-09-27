from datetime import datetime
from redis import Redis
from rq import Queue
import pytz
import json
from rq.job import Job
from typing import Dict, Callable, Any, List
from llm.analyze import (
  analyze_user_input,
  get_search_results,
  get_browse_results,
  get_basic_response,
  get_current_time,
  get_runtime_environment,
  update_google_document,
  read_google_document,
)
from channels.models import Message, Channel
# from tools.browse import get_web_page_summary
import django_rq
from llm.anthropic_integration import get_message
from config.settings import SYSTEM_PROMPT, TOOL_DEFINITIONS, IS_HEROKU_APP, AI_CHANNEL_ID


# Define a type for our tool functions
ToolFunction = Callable[[Dict[str, Any]], Any]

def ping():
    return 'Pong!'

def get_background_jobs():
    """
    Handles summarizing the background jobs that are currently running.
    """
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

# Mapping of tool names to their respective functions
TOOL_MAP: Dict[str, ToolFunction] = {
    "get_time": lambda _: get_current_time(),
    "get_runtime_environment": lambda _: get_runtime_environment(),
    "create_background_job": lambda data: django_rq.enqueue(analyze_user_input, data),
    "get_background_jobs": lambda _: get_background_jobs(),
    "get_search_results": lambda data: django_rq.enqueue(get_search_results, data),
    "get_web_page_summary": lambda data: django_rq.enqueue(get_browse_results, data),
    "update_google_document": lambda data: django_rq.enqueue(update_google_document, data),
    "get_basic_response": lambda data: django_rq.enqueue(get_basic_response, data),
    "read_google_document": lambda data: django_rq.enqueue(read_google_document, data),
}

# Mapping of tool names to their input keys
TOOL_INPUT_MAP: Dict[str, List[str]] = {
    "create_background_job": ["task"],
    "get_search_results": ["query"],
    "get_web_page_summary": ["url"],
    "update_google_document": ["google_doc_id"],
    "get_basic_response": ["prompt", "max_tokens"],
    "read_google_document": ["google_doc_id"],
}

def handle_tool_use(tool_call, request_data):
    print(f"Handling tool use: {tool_call.name}")
    
    tool_function = TOOL_MAP.get(tool_call.name)
    if not tool_function:
        return f"Unknown tool: {tool_call.name}"
    
    input_keys = TOOL_INPUT_MAP.get(tool_call.name, [])
    for key in input_keys:
        if key in tool_call.input:
            request_data[key] = tool_call.input[key]

    result = tool_function(request_data)
    if isinstance(result, str):
        return result
    elif hasattr(result, 'id'):  # Check if it's a job object
        return f"Starting background process: {result.id}"
    else:
        return "Processing started"

def persist_message(request_data):
    try:
        channel = Channel.objects.get(channel_id=request_data['channel_id'])
        request_message = Message.objects.create(
            channel=channel,
            author=request_data['author'],
            content=request_data['content'],
        )
    except Exception as e:
        print(f"Error saving message: {e}")

def respond_to_channel(request_data):
    persist_message(request_data)

    response_message = get_message(
        request_data['ai_agent_system_prompt'],
        TOOL_DEFINITIONS,
        [{ "role": "user", "content": request_data['content'] }],
    )
    
    full_response = ""
    for content in response_message.content:
        if content.type == "text":
            full_response += content.text
        elif content.type == "tool_use":
            tool_result = handle_tool_use(content, request_data)
            full_response += tool_result

    persist_message({
        "channel_id": request_data['channel_id'],
        "author": request_data["ai_agent_name"],
        "content": full_response,
    })
    
    return full_response