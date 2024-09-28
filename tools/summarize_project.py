import os
from tools.file_navigation import fetch_project_file_paths
from llm.anthropic_integration import get_basic_message
import time

def chunk_file(file_path, chunk_size=3000):
    chunks = []

    with open(file_path, 'r') as file:
        content = file.read()
        
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            chunks.append(chunk)
  
    return chunks

def create_ai_file_path(python_file_path):
    # Get the directory and filename
    directory, filename = os.path.split(python_file_path)
    
    # Split the filename and extension
    name, ext = os.path.splitext(filename)
    
    # Create the new filename with .ai extension
    ai_filename = f"{name}.ai"
    
    # Join the directory with the new filename
    return os.path.join(directory, ai_filename)

def summary_for_file(file_path, file_content):
    if not file_content or len(file_content) == 0:
        return None

    summary_message = get_basic_message(
        f"""
        You are an AI agent designed to summarize Python files. Please return
        a summary of the given Python file content in the specified format. Only
        return the file contents with no other additional informational comments or niceties.
        The file should start with an easily human readable summary that includes a title
        file path and main purpose. The summary should include sections a condensed version
        of the file content in the following format:
        
        Python Program Summary Format
        [filename]|[main_purpose]
        I:[imports]
        F:[functions]
        C:[classes]
        G:[global_variables]
        M:[main_logic]
        D:[dependencies]
        V:[python_version]
        Format details:

        Use semicolons to separate multiple items within a section
        For functions and classes, list names followed by brief description
        Exclude built-in modules from imports
        Use abbreviations and symbols where possible
        Omit sections if not applicable
        Keep each section to one line if possible

        Example:
        script.py|Data processing
        I:pandas;numpy;custom_module
        F:load_data():read CSV;process_data():clean and transform
        C:DataProcessor:handles data operations
        G:CONFIG_DICT;GLOBAL_CONSTANT
        M:Load data>Process>Export results
        D:pandas==1.2.3;numpy==1.19.5
        V:3.8+

        File details:
        File path: {file_path}
        """,
        [{
            "role": "user",
            "content": file_content
        }]
    )
    return summary_message.content[0].text 
    

def fetch_summary():
    project_files = fetch_project_file_paths()
    # project_files = project_files[:5]  # Limit to 2 files for testing
    for file_path in project_files:
        print(f"Processing: {file_path}")
        ai_file_path = create_ai_file_path(file_path)
        if os.path.exists(ai_file_path):
            print(f"Found existing file: {ai_file_path}. Skipping.")
        else:
            with open(file_path, 'r') as file:
                file_content = file.read()
            summary = summary_for_file(file_path, file_content)
            if summary:
                with open(ai_file_path, 'w+') as ai_file:
                    ai_file.write(summary)
                print(f"Summary written to: {ai_file_path}")
            time.sleep(2)