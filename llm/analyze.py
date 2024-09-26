import os
from config.settings import SYSTEM_PROMPT, TOOL_DEFINITIONS
# from app.config import OLLAMA_MODEL, BACKGROUND_PROMPT_PATH, SYSTEM_PROMPT_PATH
# from app.tools.search import get_search_data
# from app.tools.browse import get_web_page_content
# from app.utilities import read_file_as_string
# from app.llm.anthropic_response import get_message, get_basic_message
# from app.llm.ollama_response import get_message, get_basic_message
from llm.anthropic_integration import get_message, get_basic_message
from tools.search import get_search_data
from tools.browse import get_web_page_content
from tools.google.docs import append_text, DOCUMENT_ID
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

def update_google_document(reuqest_data):
    document_content_text = document_content_for_user_input(reuqest_data['user_input'])
    append_text(reuqest_data['google_doc_id'], document_content_text)
    return "Document updated"

def analyze_user_input(user_input):
    print(f"Analyzing request: {user_input}")
    time.sleep(20)
    return 'Background processing finished'
