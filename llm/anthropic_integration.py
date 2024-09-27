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

# def get_message_stream(system_prompt, tools, messages):
#     with client.messages.stream(
#         max_tokens=1024,
#         system_prompt=system_prompt,
#         messages=[{"role": "user", "content": "Hello"}],
#         model="claude-3-5-sonnet-20240620",
#         tools=tools,
#     ) as stream:
#         for text in stream.text_stream:
#             print(text, end="", flush=True)
