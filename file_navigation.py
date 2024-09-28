import os
import django
import sys
from tools.file_navigation import fetch_project_file_paths

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


if __name__ == "__main__":
    fetch_project_file_paths()