from django.core.management.base import BaseCommand, CommandError
from ai_agents.models import AIAgent
from channels.models import Channel, Message
from config.settings import SYSTEM_PROMPT
from tools.config import TOOL_DEFINITIONS
from llm.anthropic_integration import get_message


class Command(BaseCommand):
    help = 'AI Agent REPL'
    
    def handle(self, *args, **options):
        ai_agent = AIAgent.objects.get(name='beta')
        channel = Channel.objects.get(channel_name='Beta REPL')

        # Reset the messages for this channel
        Message.objects.filter(channel=channel).delete()

        message_records = Message.objects.filter(channel=channel).order_by('timestamp')

        messages = []

        for message_record in message_records:
            messages.append({
                "role": message_record.role,
                "content": message_record.content,
            })
    
        try:
            print(f'Starting REPL for AI Agent {ai_agent.name}')
                        
            # print(f'SYSTEM PROMPT: {SYSTEM_PROMPT}')
            while True:
                request_message = input('user> ')
                if request_message == 'exit':
                    break
                
                user_message_record = Message.objects.create(
                    channel=channel,
                    role='user',
                    content=request_message,
                )

                messages.append({
                    "role": user_message_record.role,
                    "content": user_message_record.content,
                })
                
                response_message = get_message(
                    SYSTEM_PROMPT,
                    TOOL_DEFINITIONS,
                    messages,
                )
                
                text_contents = []
                tool_contents = []
                for content in response_message.content:
                    if content.type == "text":
                        text_contents.append(content.text)
                    elif content.type == "tool_use":
                        tool_data = {
                            "name": content.name,
                            "input": {}
                        }
                        for key in content.input.keys():
                            tool_data['input'][key] = content.input[key]
                        tool_contents.append(tool_data)
                
                text_content = '\n'.join(text_contents)
                tool_content = ''
                tool_history = ''
                for tool in tool_contents:
                    print(f"DEBUG: {tool['name']}")
                    # tool_content += tool['name']
                    # print(f"DEBUG: {tool['name']} => {tool['input']}")
                    # tool_definition = TOOLS_MAP[tool['name']]
                    # tool_message = {
                    #     "role": "user",
                    #     "content": tool['input']['prompt'],
                    # }
                    # tool_result = tool_definition['execute'](
                    #     tool['input'],
                    #     f"""
                    #     SYSTEM PROMPT {SYSTEM_PROMPT}
                    #     TOOL RESULTS: {tool_history}
                    #     """,
                    #     messages,
                    # )

                    # tool_history += f"""
                    # Tool: {tool['name']}
                    # Input: {tool['input']}
                    # Output: {tool_result}
                    # """
                    # tool_content += tool_result

                assistant_text_content = f"""{tool_content}"""

                print(assistant_text_content)

                assistant_message_record = Message.objects.create(
                    channel=channel,
                    role='assistant',
                    content=assistant_text_content,
                )

                messages.append({
                    "role": assistant_message_record.role,
                    "content": assistant_message_record.content,
                })
        except Exception as e:
            raise CommandError('An error occurred: %s' % str(e))
        