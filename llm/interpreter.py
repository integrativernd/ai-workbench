import os
import instructor
from anthropic import Anthropic
from pydantic import BaseModel
from enum import Enum


class ResponseMode(Enum):
    SIMPLE_ANSWER = "SIMPLE_ANSWER"
    SIMPLE_QUESTION = "SIMPLE_QUESTION"
    TOOL_CALL = "TOOL_CALL"
    

class ResponseModeModel(BaseModel):
    mode_value: ResponseMode


def get_response_mode_for_message(message_content):
    client = instructor.from_anthropic(Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")))
    response = client.messages.create(
        model="claude-3-opus-20240229",
        system="""
            You are an AI assistant designed to classify user queries into three categories:

            1. SIMPLE_ANSWER: The query can be answered accurately and completely using only the knowledge embedded in the base language model. No additional information or clarification is needed.

            2. SIMPLE_QUESTION: The AI agent needs to ask one or more questions to help the user refine their query, provide more context, or clarify their intent before an accurate answer can be given.

            3. TOOL_CALL: The query requires the use of external tools to fetch information or perform computations that are beyond the capabilities of the base language model.

            Your task is to analyze the user's input and determine which of these three categories it falls into. Respond ONLY with the appropriate category name: SIMPLE_ANSWER, SIMPLE_QUESTION, or TOOL_CALL.

            Examples:

            User: "What are the main differences between Python 2 and Python 3?"
            Response: SIMPLE_ANSWER

            User: "Can you help me troubleshoot my code?"
            Response: SIMPLE_QUESTION

            User: "What's the current exchange rate between USD and EUR?"
            Response: TOOL_CALL

            User: "I want to start investing. What should I do?"
            Response: SIMPLE_QUESTION

            User: "Summarize the plot of '1984' by George Orwell."
            Response: SIMPLE_ANSWER

            User: "How much would it cost to fly from New York to London next month?"
            Response: TOOL_CALL

            User: "What are the health benefits of meditation?"
            Response: SIMPLE_ANSWER

            User: "Can you explain how blockchain technology works?"
            Response: SIMPLE_QUESTION

            User: "What's the weather forecast for Tokyo this weekend?"
            Response: TOOL_CALL

            User: "I'm having trouble with my laptop. Can you help?"
            Response: SIMPLE_QUESTION

            User: "What were the major causes of World War I?"
            Response: SIMPLE_ANSWER

            User: "How do I create a budget for my small business?"
            Response: SIMPLE_QUESTION

            User: "Calculate the mortgage payments on a $300,000 loan at 3.5% interest for 30 years."
            Response: TOOL_CALL

            Remember, your response should only be one of the three category names, with no additional explanation or text. Consider carefully whether the query can be answered accurately with existing knowledge, requires clarification through questions, or needs external tools for information or computation.
        """,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": message_content,
            }
        ],
        response_model=ResponseModeModel,
    )
    return response.mode_value