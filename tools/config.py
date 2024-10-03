# This format comes from Anthropic's Tool Use API
# https://docs.anthropic.com/en/docs/build-with-claude/tool-use
from config.settings import DOCUMENT_ID

TOOL_DEFINITIONS = [
    {
        "name": "get_current_time",
        "description": "Retrieve the current time when explicitly requested by the user.",
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "Optional timezone for the time request (e.g., 'UTC', 'America/New_York')"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_runtime_environment",
        "description": "Retrieve the current runtime environment (e.g., production, staging, development) when explicitly requested.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "summarize_web_page",
        "description": "Browse a web page for a given URL and provide a concise summary of its content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the web page to be summarized"
                },
                "focus_area": {
                    "type": "string",
                    "description": "Optional specific area or topic to focus on in the summary"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "perform_web_search",
        "description": "Conduct a web search using a specified search engine API for a given query.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The exact search query provided by the user"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of search results to return (default: 5)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "check_background_tasks",
        "description": "Retrieve information about ongoing background tasks or processes.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "update_document",
        "description": "Update a document in a specified cloud storage service (e.g., Google Docs, Dropbox Paper).",
        "input_schema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "ID of the document to be updated"
                },
                "content": {
                    "type": "string",
                    "description": "The content to be added or modified in the document"
                },
                "service": {
                    "type": "string",
                    "description": "The cloud service where the document is stored (e.g., 'google_docs', 'dropbox_paper')"
                }
            },
            "required": ["document_id", "content", "service"]
        }
    },
    {
        "name": "read_document",
        "description": "Read the contents of a document from a specified cloud storage service.",
        "input_schema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "ID of the document to be read"
                },
                "service": {
                    "type": "string",
                    "description": "The cloud service where the document is stored (e.g., 'google_docs', 'dropbox_paper')"
                }
            },
            "required": ["document_id", "service"]
        }
    },
    {
        "name": "analyze_system_architecture",
        "description": "Analyze and provide information about the system architecture based on a specific query.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The specific query about the system architecture"
                },
                "component": {
                    "type": "string",
                    "description": "Optional specific component to focus on in the analysis"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "create_pull_request",
        "description": "Create a pull request in a specified version control system (e.g., GitHub, GitLab).",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the pull request"
                },
                "description": {
                    "type": "string",
                    "description": "Detailed description of the changes in the pull request"
                },
                "base_branch": {
                    "type": "string",
                    "description": "The branch to merge changes into"
                },
                "head_branch": {
                    "type": "string",
                    "description": "The branch containing the changes"
                }
            },
            "required": ["title", "description", "base_branch", "head_branch"]
        }
    },
    {
        "name": "create_issue",
        "description": "Create an issue in a project management system (e.g., GitHub Issues, Jira).",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the issue"
                },
                "description": {
                    "type": "string",
                    "description": "Detailed description of the issue"
                },
                "labels": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Labels to categorize the issue"
                },
                "assignee": {
                    "type": "string",
                    "description": "Optional username of the person to assign the issue to"
                }
            },
            "required": ["title", "description"]
        }
    },
    {
        "name": "analyze_issue",
        "description": "Analyze and provide insights on a specific issue in a project management system.",
        "input_schema": {
            "type": "object",
            "properties": {
                "issue_url": {
                    "type": "string",
                    "description": "URL of the issue"
                },
                "issue_number": {
                    "type": "integer",
                    "description": "The issue number"
                },
                "analysis_focus": {
                    "type": "string",
                    "description": "Specific aspect of the issue to focus on in the analysis"
                }
            },
            "required": ["issue_url", "issue_number"]
        }
    },
    {
        "name": "ask_clarifying_question",
        "description": "Generate a clarifying question when the user's request is ambiguous or requires more information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "original_request": {
                    "type": "string",
                    "description": "The original request from the user"
                },
                "unclear_aspect": {
                    "type": "string",
                    "description": "The specific aspect of the request that needs clarification"
                }
            },
            "required": ["original_request", "unclear_aspect"]
        }
    },
    {
        "name": "review_conversation_history",
        "description": "Analyze previous messages in the conversation to provide context-aware responses.",
        "input_schema": {
            "type": "object",
            "properties": {
                "current_request": {
                    "type": "string",
                    "description": "The current request from the user"
                },
                "num_messages": {
                    "type": "integer",
                    "description": "Number of previous messages to review (default: 5)"
                }
            },
            "required": ["current_request"]
        }
    },
    {
        "name": "perform_mathematical_analysis",
        "description": "Conduct mathematical calculations and analysis on given data or problems.",
        "input_schema": {
            "type": "object",
            "properties": {
                "problem_statement": {
                    "type": "string",
                    "description": "Description of the mathematical problem or analysis required"
                },
                "data": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    },
                    "description": "Numerical data for analysis, if applicable"
                },
                "operation": {
                    "type": "string",
                    "description": "Specific mathematical operation to perform (e.g., 'regression', 'statistics', 'optimization')"
                }
            },
            "required": ["problem_statement"]
        }
    },
    {
        "name": "generate_data_visualization",
        "description": "Create visual representations of data (e.g., charts, graphs) based on provided information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "The data to be visualized"
                },
                "chart_type": {
                    "type": "string",
                    "description": "Type of chart or graph to generate (e.g., 'bar', 'line', 'scatter', 'pie')"
                },
                "title": {
                    "type": "string",
                    "description": "Title for the visualization"
                }
            },
            "required": ["data", "chart_type"]
        }
    },
    {
        "name": "perform_sentiment_analysis",
        "description": "Analyze the sentiment of given text data.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to analyze for sentiment"
                },
                "language": {
                    "type": "string",
                    "description": "The language of the text (default: 'en' for English)"
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "schedule_meeting",
        "description": "Schedule a meeting or appointment using a calendar service.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the meeting"
                },
                "attendees": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of attendee email addresses"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time of the meeting (ISO 8601 format)"
                },
                "duration": {
                    "type": "integer",
                    "description": "Duration of the meeting in minutes"
                },
                "location": {
                    "type": "string",
                    "description": "Location or video conference link for the meeting"
                }
            },
            "required": ["title", "attendees", "start_time", "duration"]
        }
    },
    {
        "name": "send_email",
        "description": "Compose and send an email through a specified email service.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of recipient email addresses"
                },
                "subject": {
                    "type": "string",
                    "description": "Subject line of the email"
                },
                "body": {
                    "type": "string",
                    "description": "Body content of the email"
                },
                "attachments": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of file paths or URLs to attach to the email"
                }
            },
            "required": ["to", "subject", "body"]
        }
    },
    {
        "name": "translate_text",
        "description": "Translate text from one language to another using a translation service.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to be translated"
                },
                "source_language": {
                    "type": "string",
                    "description": "The language code of the source text (e.g., 'en' for English)"
                },
                "target_language": {
                    "type": "string",
                    "description": "The language code of the desired translation (e.g., 'es' for Spanish)"
                }
            },
            "required": ["text", "target_language"]
        }
    },
    {
        "name": "generate_report",
        "description": "Create a structured report based on provided data and parameters.",
        "input_schema": {
            "type": "object",
            "properties": {
                "report_type": {
                    "type": "string",
                    "description": "Type of report to generate (e.g., 'financial', 'project_status', 'analytics')"
                },
                "data": {
                    "type": "object",
                    "description": "The data to be included in the report"
                },
                "time_period": {
                    "type": "string",
                    "description": "Time period covered by the report (e.g., 'Q3 2023', 'January 2024')"
                },
                "format": {
                    "type": "string",
                    "description": "Desired output format of the report (e.g., 'pdf', 'docx', 'html')"
                }
            },
            "required": ["report_type", "data", "time_period"]
        }
    },
    # (Previous tool definitions remain the same)

# Adding new advanced capabilities:

    {
        "name": "crawl_site_map",
        "description": "Crawl and analyze a website's sitemap to gather information about its structure and content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the website's sitemap or home page"
                },
                "depth": {
                    "type": "integer",
                    "description": "The maximum depth of pages to crawl (default: 3)"
                },
                "focus_areas": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Specific areas or topics to focus on during the crawl"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "analyze_git_repository",
        "description": "Crawl and analyze a Git repository to gather information about its structure, history, and contents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "repository_url": {
                    "type": "string",
                    "description": "The URL of the Git repository"
                },
                "branch": {
                    "type": "string",
                    "description": "The specific branch to analyze (default: main or master)"
                },
                "analysis_type": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["code_structure", "commit_history", "contributors", "dependencies"]
                    },
                    "description": "Types of analysis to perform on the repository"
                }
            },
            "required": ["repository_url"]
        }
    },
    {
        "name": "comment_on_issue",
        "description": "Add a comment to an existing issue in a project management system (e.g., GitHub Issues, Jira).",
        "input_schema": {
            "type": "object",
            "properties": {
                "issue_url": {
                    "type": "string",
                    "description": "URL of the issue to comment on"
                },
                "comment_text": {
                    "type": "string",
                    "description": "The content of the comment to be added"
                },
                "visibility": {
                    "type": "string",
                    "enum": ["public", "private", "team"],
                    "description": "Visibility setting for the comment (if applicable)"
                }
            },
            "required": ["issue_url", "comment_text"]
        }
    },
    {
        "name": "respond_to_thread",
        "description": "Compose and send a response to a specific thread in a communication platform (e.g., Slack, Microsoft Teams, forum).",
        "input_schema": {
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "description": "The communication platform where the thread exists"
                },
                "thread_id": {
                    "type": "string",
                    "description": "Unique identifier for the thread"
                },
                "response_text": {
                    "type": "string",
                    "description": "The content of the response to be sent"
                },
                "attachments": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of file paths or URLs to attach to the response"
                }
            },
            "required": ["platform", "thread_id", "response_text"]
        }
    },
    {
        "name": "generate_image",
        "description": "Create an image based on a text description using an AI image generation model.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Detailed text description of the image to be generated"
                },
                "style": {
                    "type": "string",
                    "description": "Optional style or artistic direction for the image"
                },
                "dimensions": {
                    "type": "object",
                    "properties": {
                        "width": {
                            "type": "integer",
                            "description": "Width of the image in pixels"
                        },
                        "height": {
                            "type": "integer",
                            "description": "Height of the image in pixels"
                        }
                    },
                    "description": "Dimensions of the image to be generated"
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "analyze_image",
        "description": "Perform analysis on an image to extract information, detect objects, or classify content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "URL or file path of the image to be analyzed"
                },
                "analysis_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["object_detection", "facial_recognition", "text_extraction", "color_analysis", "content_moderation"]
                    },
                    "description": "Types of analysis to perform on the image"
                }
            },
            "required": ["image_url", "analysis_types"]
        }
    },

    # Tools for critical thinking:

    {
        "name": "identify_assumptions",
        "description": "Analyze a statement or argument to identify underlying assumptions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "statement": {
                    "type": "string",
                    "description": "The statement or argument to analyze"
                },
                "context": {
                    "type": "string",
                    "description": "Additional context or background information"
                }
            },
            "required": ["statement"]
        }
    },
    {
        "name": "evaluate_evidence",
        "description": "Assess the quality and relevance of evidence supporting a claim or argument.",
        "input_schema": {
            "type": "object",
            "properties": {
                "claim": {
                    "type": "string",
                    "description": "The claim or argument being evaluated"
                },
                "evidence": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of evidence points supporting the claim"
                },
                "evaluation_criteria": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Specific criteria to use in evaluating the evidence"
                }
            },
            "required": ["claim", "evidence"]
        }
    },
    {
        "name": "generate_counterarguments",
        "description": "Produce logical counterarguments to a given statement or position.",
        "input_schema": {
            "type": "object",
            "properties": {
                "original_argument": {
                    "type": "string",
                    "description": "The original argument or position"
                },
                "context": {
                    "type": "string",
                    "description": "Additional context or background information"
                },
                "num_counterarguments": {
                    "type": "integer",
                    "description": "Number of counterarguments to generate (default: 3)"
                }
            },
            "required": ["original_argument"]
        }
    },
    {
        "name": "perform_causal_analysis",
        "description": "Analyze potential cause-and-effect relationships in a given scenario or dataset.",
        "input_schema": {
            "type": "object",
            "properties": {
                "scenario": {
                    "type": "string",
                    "description": "Description of the scenario or phenomenon to analyze"
                },
                "data": {
                    "type": "object",
                    "description": "Relevant data for the analysis, if available"
                },
                "potential_causes": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of potential causes to consider"
                }
            },
            "required": ["scenario"]
        }
    },
    {
        "name": "conduct_swot_analysis",
        "description": "Perform a SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis on a given subject.",
        "input_schema": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "The subject of the SWOT analysis (e.g., company, product, strategy)"
                },
                "context": {
                    "type": "string",
                    "description": "Additional context or background information"
                },
                "focus_areas": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Specific areas to focus on in the analysis"
                }
            },
            "required": ["subject"]
        }
    },
    {
        "name": "apply_decision_matrix",
        "description": "Create and apply a decision matrix to evaluate options based on multiple criteria.",
        "input_schema": {
            "type": "object",
            "properties": {
                "decision_context": {
                    "type": "string",
                    "description": "Description of the decision to be made"
                },
                "options": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of options to evaluate"
                },
                "criteria": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of criteria for evaluating the options"
                },
                "weights": {
                    "type": "object",
                    "description": "Optional weights for each criterion"
                }
            },
            "required": ["decision_context", "options", "criteria"]
        }
    },
]