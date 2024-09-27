from config.settings import SYSTEM_PROMPT, IS_HEROKU_APP
from llm.anthropic_integration import get_basic_message
from tools.search import get_search_data
from tools.browse import get_web_page_content
from tools.google.docs import append_text, read_document
import time
import pytz
from datetime import datetime

def get_current_time():
    est = pytz.timezone('US/Eastern')
    est_time = datetime.now(est)
    return est_time.strftime('%B %d, %Y, %I:%M %p')

def get_runtime_environment():
    if IS_HEROKU_APP:
        return 'PRODUCTION'
    else:
        return 'DEVELOPMENT'

def approximate_token_count(text):
    words = text.split()
    return int(len(words) / 0.75)

def summarize_content(content):
    message = get_basic_message(
        SYSTEM_PROMPT,
        [
            {
                "role": "user",
                "content": f"""
                    Summarize all content from the user as a short list of bullets.
                    {content}
                """,
            },
        ],
    )
    return message.content[0].text

def document_content_for_user_input(system_prompt, user_input):
    message = get_basic_message(
        system_prompt,
        [
            {
                "role": "user",
                "content": user_input,
            },
        ],
    )
    return message.content[0].text

def get_search_results(request_data):
    search_text = summarize_content(get_search_data(request_data['query']))
    return {
        "content": search_text[:2000],
        "channel_id": request_data['channel_id'],
        "ai_agent_name": request_data['ai_agent_name'],
    }

def get_browse_results(request_data):
    browse_text = summarize_content(get_web_page_content(request_data['url']))
    return {
        "content": browse_text[:2000],
        "channel_id": request_data['channel_id'],
        "ai_agent_name": request_data['ai_agent_name'],
    }

def read_google_document(request_data):
    response_content = document_content_for_user_input(
        f"""
        BASE_PROMPT
        {request_data['ai_agent_system_prompt']}
        BACKGROUND_PROCESS
        You are at the point in the response cycle where you need to generate the content
        to address the user's request. You are in a running background process and 
        you can respond in a single response in the slack thread with a maximum of 2000 characters.
        """,
        read_document(request_data['google_doc_id'])
    )
    return {
        "content": response_content,
        "channel_id": request_data['channel_id'],
        "ai_agent_name": request_data['ai_agent_name'],
    }

def update_google_document(request_data):
    document_content_data = read_document(request_data['google_doc_id'])
    response_content = document_content_for_user_input(
        f"""
        BASE_PROMPT
        {request_data['ai_agent_system_prompt']}
        CURRENT DOCUMENT CONTENT JSON DATA
        {document_content_data}
        BACKGROUND_PROCESS
        You are at the point in the response cycle where you need to generate the content
        to address the user's request. Please return the content to be appended to the document.
        Only return the text content of your response. The final document will be updated with your response.
        """,
        request_data['content']
    )
    append_text(request_data['google_doc_id'], response_content)
    return {
        "content": 'Document updated',
        "channel_id": request_data['channel_id'],
        "ai_agent_name": request_data['ai_agent_name'],
    }

def analyze_user_input(request_data):
    print(f"Analyzing request: {request_data}")
    time.sleep(20)
    return {
        "ai_agent_name": request_data['ai_agent_name'],
        "channel_id": request_data['channel_id'],
        "content": 'Background job finished',
    }

def get_basic_response(request_data):
    message = get_basic_message(
        SYSTEM_PROMPT,
        [
            {
                "role": "user",
                "content": request_data["prompt"],
            },
        ],
    )
    response_text = message.content[0].text
    return {
        "content": response_text[:2000],
        "channel_id": request_data['channel_id'],
        "ai_agent_name": request_data['ai_agent_name'],
    }
