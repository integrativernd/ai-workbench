import os
import instructor
from anthropic import Anthropic
from pydantic import BaseModel
from enum import Enum


class ResponseType(Enum):
    MESSAGE = "message"
    TOOL = "tool"


class ResponseModel(BaseModel):
    type: ResponseType


def get_response_type_for_message(ai_agent, message_content):
    client = instructor.from_anthropic(Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")))
    # tool_names = ",".join([tool["name"] for tool in TOOL_DEFINITIONS])
    response = client.messages.create(
        model="claude-3-opus-20240229",
        system="""
        You are an AI Agent designed to do one thing: determine if an AI Agent should
        respond to the user using a call to the base large language model (LLM) or if
        it need to call a tool or external service to be able to respond to the user.
        Based on the content provided from user consider all factors and determine
        if the base LLM should be used or a tool should be used. If the base LLM can be
        used return the response type as 'message'. If a tool should be used return the
        response type as 'tool'.
        """,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": message_content,
            }
        ],
        response_model=ResponseModel,
    )
    return response