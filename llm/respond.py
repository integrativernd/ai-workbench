from datetime import datetime
from redis import Redis
from rq import Queue
import pytz
# from app.brain.messages import message_queue
# from app.brain.analyze import (
#   analyze_request,
#   get_response,
#   get_search_results,
#   get_web_page_summary,
# )
from llm.anthropic_integration import get_message
from config.settings import SYSTEM_PROMPT, TOOL_DEFINITIONS, IS_HEROKU_APP

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

def handle_tool_use(tool_call, user_input):
    print(f"Handling tool use: {tool_call.name}")
    if tool_call.name == "get_time":
        return get_current_time()
    elif tool_call.name == "get_runtime_environment":
        return get_runtime_environment()
    # elif tool_call.name == "start_background_processing":
    #     message_queue.enqueue(analyze_request, tool_call.input.get("task"))
    #     return "Background processing started"
    # elif tool_call.name == "get_background_processing_info":
    #     return message_queue.job_ids
    # elif tool_call.name == "get_search_results":
    #     print(f"query: {tool_call.input.get("query")}")
    #     message_queue.enqueue(get_search_results, tool_call.input.get("query"))
    #     # return get_search_results(tool_call.input.get("query"))
    #     return "Searching the web."
    # elif tool_call.name == "get_web_page_summary":
    #     message_queue.enqueue(get_web_page_summary, tool_call.input.get("url"))
    #     return "Visting web page."
    else:
        return f"Unknown tool: {tool_call.name}"

def get_response(user_input):
    message_history = []
    message_history.append({ "role": "user", "content": user_input })
    response_message = get_message(SYSTEM_PROMPT, TOOL_DEFINITIONS, message_history)
    full_response = ""
    for content in response_message.content:
        if content.type == "text":
            full_response += content.text
        elif content.type == "tool_use":
            tool_result = handle_tool_use(content, user_input)
            full_response += tool_result
    # message_history.append({ "role": "assistant", "content": full_response })
    message_history = []
    return full_response