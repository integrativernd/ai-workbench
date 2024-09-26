import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from discord_server.chatbot_manager import run_chatbot_manager

if __name__ == "__main__":
    run_chatbot_manager()