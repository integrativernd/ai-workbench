import os
from tools.file_navigation import fetch_project_file_paths
from config.settings import BASE_DIR

def create_ai_file_path(python_file_path):
    directory, filename = os.path.split(python_file_path)
    name, ext = os.path.splitext(filename)
    ai_filename = f"{name}.ai"
    return os.path.join(directory, ai_filename)

def summary_for_file(file_path, file_content):
    if not file_content or len(file_content) == 0:
        return None

def create_project_overview():
    project_files = fetch_project_file_paths()
    # project_files = project_files[:5]  # Limit to 2 files for testing
    for file_path in project_files:
        print(f"Processing: {file_path}")
        ai_file_path = create_ai_file_path(file_path)
        if os.path.exists(ai_file_path):
            with open(ai_file_path, 'r') as file:
                file_content = file.read()

            overview_file_path = f"{BASE_DIR}/project_overview.ai"
            with open(overview_file_path, 'a') as ai_file:
                ai_file.write(file_content)
                ai_file.write("\n-------------------------------------------\n")