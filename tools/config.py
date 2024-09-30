# This format comes from Anthropic's Tool Use API
# https://docs.anthropic.com/en/docs/build-with-claude/tool-use
from config.settings import DOCUMENT_ID

TOOL_DEFINITIONS = [
    {
        "name": "get_time",
        "description": "Get the current time when the user specifically asks for it. Only used when requesting the current time.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_runtime_environment",
        "description": """
          Return the current runtime environment (e.g production, staging, development).
          Only used when requesting explicity about the runtime environment.
        """,
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
        {
        "name": "get_web_page_summary",
        "description": "Use this tool to browse a web page for a URL provided by the user and summarize the content of the page",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The url of the web page to be summarized"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "get_search_results",
        "description": "Get search results from the serper API for a given query",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The exact query the user requested to search for."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_background_jobs",
        "description": "Call this tool if the user asks you what you are working on or doing in general. Background jobs are the only thing you could be doing besides responding synchronously in the thread.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "update_google_document",
        "description": "Call this tool if you are asked to update a google document.",
        "input_schema": {
            "type": "object",
            "properties": {
                "google_doc_id": {
                    "type": "string",
                    "description": f"ID of google document to be updated and shared by the user. If not URL is provided the default document ID will be used: {DOCUMENT_ID}"
                }
            },
            "required": ["google_doc_id"]
        }
    },
    {
        "name": "read_google_document",
        "description": "Read the contents of a Google Document to respod to the user's request.",
        "input_schema": {
            "type": "object",
            "properties": {
                "google_doc_id": {
                    "type": "string",
                    "description": f"ID of google document to be updated and shared by the user. If not URL is provided the default document ID will be used: {DOCUMENT_ID}"
                }
            },
            "required": ["google_doc_id"]
        }
    },
    {
        "name": "read_system_architecture",
        "description": "Read the system architecture document when asked about the technical details of your implementation or next context about your systems when performing another task.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The specific query the user is asking about the system architecture."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": 'open_pull_request',
        "description": 'Invoke this tool when asked to make a pull request',
        "input_schema": {
            "type": 'object',
            "properties": {
                'title': {
                    'type': 'string', 'description': 'A logical title of the pull request'
                },
                'description': {
                    'type': 'string', 'title': 'Logical description based on the request.'
                }
            },
            "required": ['title', 'description'],
        },
    },
    {
        "name": 'create_github_issue',
        "description": 'Invoke this tool to log a github issue',
        "input_schema": {
            "type": 'object',
            "properties": {
                'title': {
                    'type': 'string', 'description': 'A logic title of the issue'
                },
                'description': {
                    'type': 'string', 'title': 'Logical description of the issue based on the request.'
                }
            },
            "required": ['title', 'description'],
        },
    },
    {
        "name": 'analyze_github_issue',
        "description": 'Invoke this tool when asked to address a github issue.',
        "input_schema": {
            "type": 'object',
            "properties": {
                'issue_url': {
                    'type': 'string', 'description': 'url of the github issue'
                },
                'issue_number': {
                    'type': 'integer', 'description': 'The issue number'
                },
                'description': {
                    'type': 'string', 'description': 'Details of the user request.'
                }
            },
            "required": ['issue_url', 'issue_number', 'description'],
        },
    },
    {
        "name": 'ask_clarifying_question',
        "description": 'Invoke this tool when you are asked something that is not clear and you need to ask a clarifying question.',
        "input_schema": {
            "type": 'object',
            "properties": {
                'request': {
                    'type': 'string',
                    'description': "The request from the user that is not clear."
                },
            },
            "required": ['request'],
        },
    },
    {
        "name": 'review_previous_messages',
        "description": 'Invoke this tool if the user asks you something that requires knowledge of previous messages.',
        "input_schema": {
            "type": 'object',
            "properties": {
                'request': {
                    'type': 'string',
                    'description': "The request from the user that requires knowledge of previous messages."
                },
            },
            "required": ['request'],
        },
    },
]