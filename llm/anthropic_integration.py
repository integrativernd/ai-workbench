import os
from anthropic import Anthropic


anthropic_client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

def get_message(system_prompt, tools, messages):
    return anthropic_client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4000,
        temperature=0,
        system=system_prompt,
        messages=messages,
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

