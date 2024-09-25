import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Now you can import your Discord bot code
from tools.google.setup import update_doc

if __name__ == "__main__":
    update_doc()