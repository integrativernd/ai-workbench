import os
from anthropic import Anthropic


client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

def get_message(system_prompt, messages, tools=[]):
    return client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4000,
        temperature=0,
        system=system_prompt,
        messages=messages,
        # tools=tools,
    )

def get_basic_message(messages):
    return client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4000,
        temperature=0,
        # system=system_prompt,
        messages=messages,
    )