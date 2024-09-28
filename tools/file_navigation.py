import os
import fnmatch
from config.settings import BASE_DIR

def find_project_files(root_dir, file_patterns, exclude_dirs):
    project_files = []

    for root, dirs, files in os.walk(root_dir):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for pattern in file_patterns:
            for filename in fnmatch.filter(files, pattern):
                file_path = os.path.join(root, filename)
                project_files.append(file_path)

    return project_files

def fetch_project_file_paths():
    # root_directory = '.'  # Current directory, change if needed
    file_patterns = ['*.py', '*.md']  # Python and Markdown files
    exclude_directories = [
        '__pycache__', 
        'venv', 
        '.venv', 
        'env',
        'migrations',
        'staticfiles',
        'static',
        'media',
        'node_modules',
        '.git',
    ]

    project_files = find_project_files(BASE_DIR, file_patterns, exclude_directories)

    # print(f"Found {len(project_files)} Python and Markdown files:")
    # for file in project_files:
    #     print(file)

    return project_files