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
import time
import json

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

def get_search_results(query):
    search_text = summarize_content(get_search_data(query))
    return search_text[:2000]

def get_browse_results(url):
    browse_text = summarize_content(get_web_page_content(url))
    return browse_text[:2000]

def analyze_user_input(user_input):
    print(f"Analyzing request: {user_input}")
    time.sleep(20)
    # print(f"Analyzing request: {user_input}")
    # message = get_basic_message(
    #     [
    #         {
    #             "role": "user",
    #             "content": BACKGROUND_PROMPT,
    #         },
    #         {
    #             "role": "assistant",
    #             "context": "ok",
    #         },
    #         {
    #             "role": "user",
    #             "content": user_input,
    #         }
    #     ]
    # )
    # step_data = message.content[0].text
    
    # steps = json.loads(step_data)
    # # time.sleep(10)

    # for step in steps['steps']:
    #     print(step)
    return 'Background processing finished'
