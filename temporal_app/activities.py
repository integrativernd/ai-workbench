import asyncio
from dataclasses import dataclass
from asgiref.sync import sync_to_async

from temporalio import activity
from temporalio.client import Client
from llm.anthropic_integration import get_message
from ai_agents.models import AIAgent
from tools.config import TOOL_DEFINITIONS, TOOL_MAP
from config.settings import SYSTEM_PROMPT
import json


@sync_to_async
def get_ai_agent_by_token(token):
    return AIAgent.objects.get(token=token)
@dataclass
class AIAgentActivityInput:
    ai_agent_token: str
    message_content: str
    message_author: str
    message_channel_id: str

@dataclass
class AIAgentToolInput:
    tool_name: str
    tool_input: dict

class AIAgentActivityManager:
    def __init__(self, client: Client) -> None:
        self.client = client
    
    @activity.defn
    async def ping(self, input: AIAgentActivityInput) -> str:
        return "pong"
    
    @activity.defn
    async def perform_activity(self, input: AIAgentActivityInput) -> str:
        # Schedule a task to complete this asynchronously. This could be done in
        # a completely different process or system.
        print("Completing activity asynchronously")
        # Tasks stored by asyncio are weak references and therefore can get GC'd
        # which can cause warnings like "Task was destroyed but it is pending!".
        # So we store the tasks ourselves.
        # See https://docs.python.org/3/library/asyncio-task.html#creating-tasks,
        # https://bugs.python.org/issue21163 and others.
        _ = asyncio.create_task(
            self.handle_request(activity.info().task_token, input)
        )
        # Raise the complete-async error which will complete this function but
        # does not consider the activity complete from the workflow perspective
        activity.raise_complete_async()

    @activity.defn
    async def get_ai_agent_name(self, input: AIAgentActivityInput) -> str:
        ai_agent = await get_ai_agent_by_token(input.ai_agent_token)
        return ai_agent.name

    @activity.defn
    async def get_tools(self, input: AIAgentActivityInput) -> str:
        ai_agent = await get_ai_agent_by_token(input.ai_agent_token)
        tool_contents = []
        text_contents = []
        message = get_message(
            ai_agent.description,
            TOOL_DEFINITIONS,
            [{"role": "user", "content": input.message_content}],
        )
        for content in message.content:
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
        return json.dumps(tool_contents)
    
    @activity.defn
    async def call_tool(self, input: AIAgentToolInput) -> str:
        tool_definition = TOOL_MAP[input.tool_name]
        if tool_definition.get('execute'):
            return tool_definition.get('execute')(
                input.tool_input,
                SYSTEM_PROMPT,
                [],
            )
        else:
            return "No tool definition found"

    async def handle_request(self, task_token: bytes, input: AIAgentActivityInput) -> None:
        handle = self.client.get_async_activity_handle(task_token=task_token)
        await asyncio.sleep(1)
        await handle.heartbeat()
        try:
            ai_agent = await get_ai_agent_by_token(input.ai_agent_token)
            response_text = await self.get_tools(
                ai_agent.description,
                input.message_content
            )
            await handle.heartbeat()
            response_data = {
                "ai_agent_name": ai_agent.name,
                "content": response_text,
                "channel_id": input.message_channel_id,
            }
            await handle.complete(json.dumps(response_data))
        except Exception as e:
            await handle.fail(e)


        

       



# import asyncio
# from temporalio import activity
# from channels.models import Message
# import threading
# import time
# from llm.anthropic_integration import get_basic_message


# @activity.defn
# async def say_hello(message: str) -> str:
#     activity.logger.info(f"Making Anthropic Request {message}")
#     print(f"Making Anthropic Request {message}")
#     time.sleep(10)
#     activity.heartbeat()
#     time.sleep(10)
#     activity.heartbeat()
#     time.sleep(10)
#     return "Hello world!"


# @activity.defn
# async def review_message_history(channel_id: str) -> str:
#     response_text = ""
#     messages = Message.objects.limit(10)
#     for message in messages:
#         response_text += f"{message.author}: {message.content}\n"
#     return response_text