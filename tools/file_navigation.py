import os
import fnmatch
from config.settings import BASE_DIR
import subprocess
import os

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

    return find_project_files(BASE_DIR, file_patterns, exclude_directories)

def list_changed_files(directory='.'):
    """
    List all files that have changes in the given directory.
    
    :param directory: The directory to check for changes. Defaults to current directory.
    :return: A list of changed file paths.
    """
    original_dir = os.getcwd()
    os.chdir(directory)
    
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                                capture_output=True, text=True, check=True)
        
        # Process the output
        changed_files = []
        for line in result.stdout.split('\n'):
            if line.strip():
                status, file_path = line[:2], line[3:].strip()
                changed_files.append(file_path)
        
        return changed_files
    
    except subprocess.CalledProcessError:
        print("Error: Not a git repository or git command failed.")
        return []
    
    finally:
        os.chdir(original_dir)
