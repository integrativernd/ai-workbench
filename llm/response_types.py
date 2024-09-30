import os
import instructor
from anthropic import Anthropic
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from tools.config import TOOL_DEFINITIONS



class ResponseType(Enum):
    MESSAGE = "message"
    TOOL = "tool"


class ResponseModel(BaseModel):
    type: ResponseType


def get_response_type_for_message(ai_agent, message_content):
    client = instructor.from_anthropic(Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")))
    tool_names = ",".join([tool["name"] for tool in TOOL_DEFINITIONS])
    response = client.messages.create(
        model="claude-3-opus-20240229",
        system=ai_agent.description,
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