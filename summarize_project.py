import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


if __name__ == "__main__":
    from tools.summarize_project import fetch_summary
    fetch_summary()