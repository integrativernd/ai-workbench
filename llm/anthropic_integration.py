import os
from anthropic import Anthropic, AsyncAnthropic
import asyncio


anthropic_client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

async_anthropic_client = AsyncAnthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

def get_message(system_prompt, tools, messages):
    return anthropic_client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4000,
        messages=messages,
        system=system_prompt,
        temperature=0,
        tools=tools,
    )

def get_basic_message(system_prompt, messages):
    return anthropic_client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4000,
        temperature=0,
        system=system_prompt,
        messages=messages,
    )

async def send_chunked_message(channel, content):
    chunk = ""
    for line in content.split('\n'):
        if len(chunk) + len(line) + 1 > 1990:  # Leave some room for safety
            await channel.send(chunk)
            chunk = line + '\n'
        else:
            chunk += line + '\n'
    if chunk:
        await channel.send(chunk)

async def stream_to_discord(ai_agent, message):
    print("Streaming to Discord")
    buffer = ""
    last_send_time = asyncio.get_event_loop().time()

    async with async_anthropic_client.messages.stream(
        model="claude-3-sonnet-20240229",
        max_tokens=1024,
        system=ai_agent.description,
        messages=[{"role": "user", "content": message.content}],
    ) as stream:
        async for text in stream.text_stream:
            buffer += text
            current_time = asyncio.get_event_loop().time()
            
            # Send the buffer if it's been 2 seconds or if it's over 1500 characters
            if current_time - last_send_time > 2 or len(buffer) > 1500:
                await send_chunked_message(message.channel, buffer)
                buffer = ""
                last_send_time = current_time

    # Send any remaining text in the buffer
    if buffer:
        await send_chunked_message(message.channel, buffer)