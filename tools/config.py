# This format comes from Anthropic's Tool Use API
# https://docs.anthropic.com/en/docs/build-with-claude/tool-use
from config.settings import DOCUMENT_ID
from llm.anthropic_integration import get_message, get_basic_message
import datetime
import pytz

est = pytz.timezone('US/Eastern')

knowledge_context = {}




DEFAULT_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "prompt": {
            "type": "string",
            "description": "The prompt to generate a response from"
        }
    },
    "required": ["prompt"]
}

def remove_key_from_list(original_list, key_to_remove):
    return [{k: v for k, v in item.items() if k != key_to_remove} for item in original_list]

def execute_basic_response(input, system_prompt, messages):
    message = get_basic_message(system_prompt, messages)
    return message.content[0].text

def google_search(input, system_prompt, messages):
    return f"Perform google search {input['prompt']}"

def perform_ask_question(input, system_prompt, messages):
    return f"Perform ask question {input['prompt']}"

def review_website(input, system_prompt, messages):
    return f"Perform review website {input['url']}"

def lookup_user_information(input, system_prompt, messages):
    message = get_basic_message(system_prompt, messages)
    return message.content[0].text

def curent_time(_input, _system_prompt, _messages):
    return datetime.datetime.now(est).strftime("%Y-%m-%d %I:%M:%S %p")

def remember_information_about_user(input, system_prompt, messages):
    # message = get_basic_message(system_prompt, messages)
    # knowledge_context["user_information"] = message.content[0].text
    return f"Remembering information about user {input['prompt']}"

def evaluate_information(input, system_prompt, messages):
    return f"Evaluate information {input['prompt']}"

TOOLS = [
    {
        "name": "ask_question",
        "description": "Use this tool to ask a question.",
        "input_schema": DEFAULT_INPUT_SCHEMA,
        "execute": execute_basic_response,
    },
    {
        "name": "evaluate_information",
        "description": "Use this tool to evaluate information you are provided.",
        "input_schema": DEFAULT_INPUT_SCHEMA,
        "execute": execute_basic_response,
    },
    # {
    #     "name": "remember_information_about_user",
    #     "description": "Invoke this tool when the user states something about themselves that should be remembered.",
    #     "input_schema": DEFAULT_INPUT_SCHEMA,
    #     "execute": remember_information_about_user,
    # },
    # {
    #     "name": "summarize_information",
    #     "description": "Invoke this tool to summarize information.",
    #     "input_schema": DEFAULT_INPUT_SCHEMA,
    #     "execute": execute_basic_response,
    # },
    # {
    #     "name": "ask_question",
    #     "description": "Invoke this tool to ask a clarifying question.",
    #     "input_schema": DEFAULT_INPUT_SCHEMA,
    #     "execute": perform_ask_question,
    # },
    # {
    #     "name": "lookup_user_information",
    #     "description": "Invoke this tool to look up information about the user.",
    #     "input_schema": DEFAULT_INPUT_SCHEMA,
    #     "execute": lookup_user_information,
    # },
    # {
    #     "name": "google_search",
    #     "description": "Invoke this tool to perform a Google Search when asked a question that requires up-to-date information about the world.",
    #     "input_schema": DEFAULT_INPUT_SCHEMA,
    #     "execute": google_search,
    # },
    # {
    #     "name": "evaluate_information",
    #     "description": "Invoke this when you need to reason about a statement after looking up information.",
    #     "input_schema": DEFAULT_INPUT_SCHEMA,
    #     "execute": evaluate_information,
    # },
    # {
    #     "name": "make_suggestion",
    #     "description": "Invoke this tool to make a suggestion or recommendation.",
    #     "input_schema": DEFAULT_INPUT_SCHEMA,
    #     "execute": evaluate_information,
    # },
    # {
    #     "name": "review_website",
    #     "description": "Invoke this tool when asked to review a website and provided a url.",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "url": {
    #                 "type": "string",
    #                 "description": "URL of the website to review"
    #             }
    #         },
    #         "required": ["url"]
    #     },
    #     "execute": review_website,
    # },
    # {
    #     "name": "current_time",
    #     "description": "Invoke this tool when you are asked about the time explicitly or you need to look up the time to be passed to another tool.",
    #     "input_schema": DEFAULT_INPUT_SCHEMA,
    #     "execute": curent_time,
    # },
]

TOOL_DEFINITIONS = remove_key_from_list(TOOLS, "execute")

TOOLS_MAP = {tool["name"]: tool for tool in TOOLS}


    # {
    #     "name": "ask_question",
    #     "description": "Invoked this tool to ask a question.",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "prompt": {
    #                 "type": "string",
    #                 "description": "The prompt to generate a response from"
    #             }
    #         },
    #         "required": ["prompt"]
    #     }
    # },
    # {
    #     "name": "make_suggestion",
    #     "description": "Invoked this tool to make a suggestion.",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "prompt": {
    #                 "type": "string",
    #                 "description": "The prompt to generate a response from"
    #             }
    #         },
    #         "required": ["prompt"]
    #     }
    # },
    # {
    #     "name": "review_own_source_code",
    #     "description": "Invoke this tool to review your own source code.",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "prompt": {
    #                 "type": "string",
    #                 "description": "The prompt to generate a response from"
    #             }
    #         },
    #         "required": ["prompt"]
    #     }
    # },
    # {
    #     "name": "google_search",
    #     "description": "Invoke this tool to search for information.",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "prompt": {
    #                 "type": "string",
    #                 "description": "The prompt to generate a response from"
    #             }
    #         },
    #         "required": ["prompt"]
    #     }
    # },
    # {
    #     "name": "organize_information",
    #     "description": "Invoke this tool to organize information.",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "prompt": {
    #                 "type": "string",
    #                 "description": "The prompt to generate a response from"
    #             }
    #         },
    #         "required": ["prompt"]
    #     }
    # },
    # {
    #     "name": "identify_problem",
    #     "description": "Invoke to identify the problem the user is facing.",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "prompt": {
    #                 "type": "string",
    #                 "description": "The prompt to generate a response from"
    #             }
    #         },
    #         "required": ["prompt"]
    #     }
    # },
    # {
    #     "name": "obtain_information",
    #     "description": "Invoke to obtain information from the user.",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "prompt": {
    #                 "type": "string",
    #                 "description": "The prompt to generate a response from"
    #             }
    #         },
    #         "required": ["prompt"]
    #     }
    # },
    # {
    #     "name": "make_predictions",
    #     "description": "Invoke to make predictions about information provided.",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "prompt": {
    #                 "type": "string",
    #                 "description": "The prompt to generate a response from"
    #             }
    #         },
    #         "required": ["prompt"]
    #     }
    # },
    # {
    #     "name": "generate_alternatives",
    #     "description": "Invoke to generate alternatives to a given prompt.",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "prompt": {
    #                 "type": "string",
    #                 "description": "The prompt to generate a response from"
    #             }
    #         },
    #         "required": ["prompt"]
    #     }
    # },
    # {
    #     "name": "implement_decision",
    #     "description": "Invoke to implement a decision based on a given prompt.",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "prompt": {
    #                 "type": "string",
    #                 "description": "The prompt to generate a response from"
    #             }
    #         },
    #         "required": ["prompt"]
    #     }
    # }
# ]