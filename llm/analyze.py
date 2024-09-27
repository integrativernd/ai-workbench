from config.settings import SYSTEM_PROMPT
from llm.anthropic_integration import get_basic_message
from tools.search import get_search_data
from tools.browse import get_web_page_content
from tools.google.docs import append_text
import time

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

def document_content_for_user_input(user_input):
    message = get_basic_message(
        "Respond to user's request with a useful and accurate response given your current knowledge.",
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

def update_google_document(request_data):
    document_content_text = document_content_for_user_input(request_data['user_input'])
    append_text(request_data['google_doc_id'], document_content_text)
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