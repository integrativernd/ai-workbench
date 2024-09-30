import os
from tools.code.file_navigation import list_files
from llm.anthropic_integration import get_basic_message
from config.settings import BASE_DIR

def summary_for_file(file_path, file_content):
    if not file_content or len(file_content) == 0:
        return None

def list_files_to_change(query):
    files_as_text = "\n".join(list_files())
    message = get_basic_message(
        f"""
        You are an AI agent with the purpose of finding files to change based on a user request.
        This is the user's requery {query}. When provided with a list of files,
        please return the files that need to be changed.
        """,
        [
            {
                "role": "user",
                "content": files_as_text
            }
        ]
    )
    return message.content[0].text