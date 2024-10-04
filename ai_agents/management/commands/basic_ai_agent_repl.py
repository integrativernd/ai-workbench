import os
from django.core.management.base import BaseCommand, CommandError
from config.settings import SYSTEM_PROMPT
from llm.anthropic_integration import anthropic_client
import json

# CURRENT_FILE_PATH = os.path.abspath(os.path.dirname(__file__))
# with open(os.path.join(CURRENT_FILE_PATH, 'ai_agent.py'), 'r') as f:
#     SOURCE_CODE = f.read()

def get_message_history():
    with open('ai_agents/management/commands/message_history.json', 'r') as f:
        existing_messages = json.loads(f.read())
    return existing_messages


def save_message_history(messages):
    with open('ai_agents/management/commands/message_history.json', 'w') as f:
        f.write(json.dumps(messages, indent=4))


# This command starts a basic AI agent REPL. It uses
# the anthropic_client to interact with the AI model and a JSON file
# to store the message history.
class Command(BaseCommand):
    help = 'Basic AI Agent REPL'
    
    def handle(self, *args, **options):
        messages = get_message_history()
        try:            
            while True:
                user_content = input('user> ')
                if user_content == 'exit':
                    break
                messages.append({"role": 'user', "content": user_content})
                save_message_history(messages)
                text_contents = []
                with anthropic_client.messages.stream(
                    model="claude-3-sonnet-20240229",
                    max_tokens=4000,
                    system=SYSTEM_PROMPT,
                    messages=messages,
                ) as stream:
                    for text in stream.text_stream:
                        print(text, end="", flush=True)
                        text_contents.append(text)
                print('\n')
                assistant_content = "".join(text_contents).strip()
                messages.append({"role": "assistant", "content": assistant_content})
                save_message_history(messages)
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))
        