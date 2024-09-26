from datetime import datetime
from redis import Redis
from rq import Queue
import pytz
import json
from rq.job import Job

from llm.analyze import (
  analyze_user_input,
  get_search_results,
  get_browse_results,
  update_google_document,
)
# from tools.browse import get_web_page_summary
import django_rq
from llm.anthropic_integration import get_message
from config.settings import SYSTEM_PROMPT, TOOL_DEFINITIONS, IS_HEROKU_APP, AI_CHANNEL_ID

def ping():
    return 'Pong!'

def get_current_time():
    est = pytz.timezone('US/Eastern')
    est_time = datetime.now(est)
    return est_time.strftime('%B %d, %Y, %I:%M %p')

def get_runtime_environment():
    if IS_HEROKU_APP:
        return 'PRODUCTION'
    else:
        return 'DEVELOPMENT'
    
def enqueue_update_google_document(tool_call, user_input):
    django_rq.enqueue(
        update_google_document,
        {
            "google_doc_id": tool_call.input.get("google_doc_id"),
            "user_input": user_input,
        }
    )

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

def handle_tool_use(tool_call, request_data):
    print(f"Handling tool use: {tool_call.name}")
    tool_name = tool_call.name
    if tool_name == "get_time":
        return get_current_time()
    elif tool_name == "get_runtime_environment":
        return get_runtime_environment()
    elif tool_name == "create_background_job":
        django_rq.enqueue(analyze_user_input, {
            "task": tool_call.input.get("task"),
            "channel_id": channel_id,
        })
        return "Background processing started"
    elif tool_name == "get_background_jobs":
        return get_background_jobs()
    elif tool_name == "get_search_results":
        request_data['query'] = tool_call.input.get("query")
        django_rq.enqueue(get_search_results, request_data)
        return "Searching the web..."
    elif tool_name == "get_web_page_summary":
        request_data['url'] = tool_call.input.get("url")
        django_rq.enqueue(get_browse_results, request_data)
        return "Reviewing the web page."
    elif tool_name == "update_google_document":
        request_data['google_doc_id'] = tool_call.input.get("google_doc_id")
        django_rq.enqueue(update_google_document, request_data)
        return "Updating document."
    else:
        return f"Unknown tool: {tool_name}"

def respond_to_channel(request_data):
    message_history = []
    message_history.append({ "role": "user", "content": request_data['content'] })
    response_message = get_message(SYSTEM_PROMPT, TOOL_DEFINITIONS, message_history)
    full_response = ""
    for content in response_message.content:
        if content.type == "text":
            full_response += content.text
        elif content.type == "tool_use":
            tool_result = handle_tool_use(content, request_data)
            full_response += tool_result
    # message_history.append({ "role": "assistant", "content": full_response })
    # message_history = []
    # Shorten the response to 2000 characters to avoid Discord message length limits.
    # TODO: Implement a more sophisticated way to handle long responses.
    return full_response