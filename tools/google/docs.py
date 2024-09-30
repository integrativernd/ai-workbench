from typing import Dict, Any, Callable
from googleapiclient.discovery import build
from config.settings import SYSTEM_PROMPT
import json
from llm.anthropic_integration import get_basic_message
from tools.google.auth import get_credentials
from googleapiclient.errors import HttpError

ToolFunction = Callable[[Dict[str, Any]], Any]

TOOL_DEFINITIONS = [
    {
        "name": "insert_text",
        "description": "Insert text at a specific index in the document.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "index": {"type": "integer"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "delete_content",
        "description": "Delete content between start and end indices.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_index": {"type": "integer"},
                "end_index": {"type": "integer"}
            },
            "required": ["start_index", "end_index"]
        }
    },
    {
        "name": "replace_text",
        "description": "Replace all instances of a text with new text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "old_text": {"type": "string"},
                "new_text": {"type": "string"}
            },
            "required": ["old_text", "new_text"]
        }
    },
    {
        "name": "add_section",
        "description": "Add a new section (Heading 2) with content under a specified existing title.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"},
                "under_title": {"type": "string"}
            },
            "required": ["title", "content", "under_title"]
        }
    },
]

class GoogleDocsAIAgent:
    def __init__(self, document_id, docs_service):
        self.document_id = document_id
        self.docs_service = docs_service

    def set_document(self, doc_id):
        self.document_id = doc_id

    def get_document_end_index(self):
        document = self.docs_service.documents().get(documentId=self.document_id).execute()
        return document['body']['content'][-1]['endIndex'] - 1

    def get_document_structure(self):
        document = self.docs_service.documents().get(documentId=self.document_id).execute()
        structure = []
        for elem in document['body']['content']:
            if 'paragraph' in elem:
                para = elem['paragraph']
                if 'paragraphStyle' in para and para['paragraphStyle'].get('namedStyleType', '').startswith('HEADING'):
                    structure.append({
                        'type': 'heading',
                        'level': int(para['paragraphStyle']['namedStyleType'][-1]),
                        'text': para['elements'][0]['textRun']['content'].strip(),
                        'startIndex': elem['startIndex'],
                        'endIndex': elem['endIndex']
                    })
        return structure

    # def insert_text(self, data):
    #     text = data.get('text', '')
    #     index = data.get('index', self.get_document_end_index())
    #     print(f"Inserting text: {text} at index: {index}")
    #     request = [{"insertText": {"location": {"index": 1}, "text": text}}]
    #     self.docs_service.documents().batchUpdate(documentId=self.document_id, body={'requests': request}).execute()
    #     return f"Inserted text at index {index}"

    # def delete_content(self, data):
    #     start_index = data.get('start_index', 1)
    #     end_index = data.get('end_index', self.get_document_end_index())
    #     request = [{"deleteContentRange": {"range": {"startIndex": start_index, "endIndex": end_index}}}]
    #     self.docs_service.documents().batchUpdate(documentId=self.document_id, body={'requests': request}).execute()
    #     return f"Deleted content from index {start_index} to {end_index}"

    # def replace_text(self, data):
    #     old_text = data.get('old_text', '')
    #     new_text = data.get('new_text', '')
    #     request = [{"replaceAllText": {"containsText": {"text": old_text}, "replaceText": new_text}}]
    #     self.docs_service.documents().batchUpdate(documentId=self.document_id, body={'requests': request}).execute()
    #     return f"Replaced all instances of '{old_text}' with '{new_text}'"

    # def create_title(self, data):
    #     title = data.get('title', '')
    #     # index = data.get('index', 1)
    #     index = 1
    #     request = [
    #         {"insertText": {"location": {"index": index}, "text": title + "\n"}},
    #         {"updateParagraphStyle": {
    #             "range": {"startIndex": index, "endIndex": index + len(title)},
    #             "paragraphStyle": {"namedStyleType": "HEADING_1"},
    #             "fields": "namedStyleType"
    #         }}
    #     ]
    #     self.docs_service.documents().batchUpdate(documentId=self.document_id, body={'requests': request}).execute()
    #     return f"Created title '{title}' at index {index}"

    def add_section(self, data):
        title = data.get('title', '')
        content = data.get('content', '')
        under_title = data.get('under_title', '')
        
        structure = self.get_document_structure()
        insert_index = self.get_document_end_index()
        
        for heading in structure:
            if heading['text'].lower() == under_title.lower():
                insert_index = heading['endIndex']
                break
        
        request = [
            {"insertText": {"location": {"index": insert_index}, "text": "\n" + title + "\n" + content + "\n"}},
            {"updateParagraphStyle": {
                "range": {"startIndex": insert_index + 1, "endIndex": insert_index + 1 + len(title)},
                "paragraphStyle": {"namedStyleType": "HEADING_2"},
                "fields": "namedStyleType"
            }}
        ]
        self.docs_service.documents().batchUpdate(documentId=self.document_id, body={'requests': request}).execute()
        return f"Added section '{title}' under '{under_title}'"
    
    def delete_section(self, header_text, header_level):
        try:
            # 1. Get the document content
            document = self.docs_service.documents().get(documentId=self.document_id).execute()
            
            # 2. Find the start index of the header
            start_index = None
            end_index = None
            content = document.get('body').get('content')
            
            for element in content:
                if 'paragraph' in element:
                    paragraph = element.get('paragraph')
                    print(paragraph.get('paragraphStyle', {}).get('namedStyleType'))
                    if paragraph.get('paragraphStyle', {}).get('namedStyleType') == f'HEADING_{header_level}':
                        for run in paragraph.get('elements', []):
                            if run.get('textRun', {}).get('content', '').strip() == header_text:
                                start_index = element.get('startIndex')
                                break
            
            if start_index is None:
                print(f"Header '{header_text}' not found.")
                return
            
            # 3. Find the end index (next header of the same level or document end)
            for element in content:
                if 'paragraph' in element and element.get('startIndex') > start_index:
                    paragraph = element.get('paragraph')
                    if paragraph.get('paragraphStyle', {}).get('namedStyleType') == f'HEADING_{header_level}':
                        end_index = element.get('startIndex')
                        break
            
            if end_index is None:
                end_index = document.get('body').get('content')[-1].get('endIndex')
            
            # 4. Create the delete request
            requests = [
                {
                    'deleteContentRange': {
                        'range': {
                            'startIndex': start_index,
                            'endIndex': end_index
                        }
                    }
                }
            ]
            
            # 5. Execute the request
            result = self.docs_service.documents().batchUpdate(
                documentId=self.document_id, body={'requests': requests}).execute()
            
            print(f"Deleted content from index {start_index} to {end_index}")
            return result
        
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None


    # TOOL_MAP: Dict[str, ToolFunction] = {
    #     "insert_text": insert_text,
    #     "delete_content": delete_content,
    #     "replace_text": replace_text,
    #     "create_title": create_title,
    #     "add_section": add_section,
    # }

    # TOOL_INPUT_MAP: Dict[str, List[str]] = {
    #     "insert_text": ["text", "index"],
    #     "delete_content": ["start_index", "end_index"],
    #     "replace_text": ["old_text", "new_text"],
    #     "create_title": ["title", "index"],
    #     "add_section": ["title", "content", "under_title"],
    # }

    def handle_tool_use(self, tool_call):
        print(f"Handling tool use: {tool_call.name}")
        
        tool_function = self.TOOL_MAP.get(tool_call.name)
        if not tool_function:
            return f"Unknown tool: {tool_call.name}"
        
        request_data = {}
        input_keys = self.TOOL_INPUT_MAP.get(tool_call.name, [])
        for key in input_keys:
            if key in tool_call.input:
                request_data[key] = tool_call.input[key]

        result = tool_function(self, request_data)
        return result
    
    def process_user_command(self, user_command):
        # return self.delete_section("About Delete", 2)
        return self.add_section({
            "title": "Test Section",
            "content": user_command,
            "under_title": "Test Title"
        })
        # response = anthropic_client.messages.create(
        #     model="claude-3-sonnet-20240229",
        #     max_tokens=4000,
        #     temperature=0,
        #     system=prompt,
        #     messages=[{
        #         "role": "user",
        #         "content": user_command,
        #     }],
        #     tools=TOOL_DEFINITIONS,
        # )
        # full_response = ""
        # for content in response.content:
        #     if content.type == "text":
        #         full_response += content.text
        #     elif content.type == "tool_use":
        #         tool_result = self.handle_tool_use(content)
        #         full_response += tool_result
        # return full_response
        

def append_text(document_id, content):
    creds = get_credentials()
    service = build("docs", "v1", credentials=creds)
    google_update_agent = GoogleDocsAIAgent(document_id, service)
    google_update_agent.process_user_command(content)

def read_document(document_id):
    creds = get_credentials()
    service = build("docs", "v1", credentials=creds)
    document = service.documents().get(documentId=document_id).execute()
    doc_content = document.get('body').get('content')
    return json.dumps(doc_content)

def update_doc_with_anthropic(document_id, instructions):
    # Setup for Google Docs and Anthropic APIs
    creds = get_credentials()
    service = build("docs", "v1", credentials=creds)
    # Fetch the current document content
    document = service.documents().get(documentId=document_id).execute()
    doc_content = document.get('body').get('content')
    # Prepare the prompt for Anthropic
    prompt = f"""
    Here's the current structure of a Google Doc:
    {json.dumps(doc_content, indent=2)}

    I need you to generate Google Docs API requests to make the following changes:
    {instructions}

    Please provide the requests in the following JSON format:
    {{
        "requests": [
            {{
                "updateParagraphStyle": {{
                    "range": {{
                        "startIndex": <start_index>,
                        "endIndex": <end_index>
                    }},
                    "paragraphStyle": {{
                        "namedStyleType": "HEADING_1"
                    }},
                    "fields": "namedStyleType"
                }}
            }},
            {{
                "insertText": {{
                    "location": {{
                        "index": <insert_index>
                    }},
                    "text": "<text_to_insert>"
                }}
            }}
            // Add more request types as needed
        ]
    }}

    Only include the JSON output, no additional explanations.
    """

    # Get the response from Anthropic
    response = get_basic_message(
        SYSTEM_PROMPT,
        [
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    # Parse the response
    try:
        requests = json.loads(response.completion)
    except json.JSONDecodeError:
        raise ValueError("Failed to parse Anthropic response as JSON")

    # Execute the requests
    result = service.documents().batchUpdate(
        documentId=document_id, body=requests).execute()

    return result

