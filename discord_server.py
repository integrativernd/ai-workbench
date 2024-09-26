import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Now you can import your Discord bot code
from discord_server.worker2 import run_discord_bot

if __name__ == "__main__":
    run_discord_bot()