from temporalio import activity
from channels.models import Message
import threading
import time
from llm.anthropic_integration import get_basic_message


@activity.defn
async def say_hello(message: str) -> str:
    activity.logger.info(f"Making Anthropic Request {message}")
    print(f"Making Anthropic Request {message}")
    time.sleep(10)
    activity.heartbeat()
    time.sleep(10)
    activity.heartbeat()
    time.sleep(10)
    return "Hello world!"


@activity.defn
async def review_message_history(channel_id: str) -> str:
    response_text = ""
    messages = Message.objects.limit(10)
    for message in messages:
        response_text += f"{message.author}: {message.content}\n"
    return response_text