import operator
from typing import Annotated, Sequence, Literal
from typing_extensions import TypedDict
from langchain_anthropic import ChatAnthropic
import functools

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langgraph.graph import END, StateGraph, START
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from PIL import Image
import io

search_tool = TavilySearchResults(max_results=5)


def create_agent(llm, tools, system_message: str):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
                " You have access to the following tools: {tool_names}.\n{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    return prompt | llm.bind_tools(tools)


@tool
def review_tool(
    message: Annotated[str, "Information or data provided by a human or a Researcher"] = "",
):
    """Review the data provided by a human or a Researcher"""
    messages = [
        ("system", "You are a helpful reviewer, reviewing the data provided by a human or Researcher."),
        ("human", "I love programming."),
    ]
    response_message = llm.invoke(messages)
    return response_message.content

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str


def agent_node(state, agent, name):
    result = agent.invoke(state)
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        "sender": name,
    }

llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

research_agent = create_agent(
    llm,
    [search_tool],
    system_message="You should provide accurate data for the Reviewer to use.",
)
research_node = functools.partial(agent_node, agent=research_agent, name="Researcher")

# chart_generator
review_agent = create_agent(
    llm,
    [review_tool],
    system_message="You should review the Research response and provide a critique.",
)
review_node = functools.partial(agent_node, agent=review_agent, name="Reviewer")

tools = [search_tool, review_tool]
tool_node = ToolNode(tools)

def router(state):
    # This is the router
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        # The previous agent is invoking a tool
        return "call_tool"
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        return END
    return "continue"

workflow = StateGraph(AgentState)

workflow.add_node("Researcher", research_node)
workflow.add_node("Reviewer", review_node)
workflow.add_node("call_tool", tool_node)

workflow.add_conditional_edges(
    "Researcher",
    router,
    {"continue": "Reviewer", "call_tool": "call_tool", END: END},
)
workflow.add_conditional_edges(
    "Reviewer",
    router,
    {"continue": "Researcher", "call_tool": "call_tool", END: END},
)

workflow.add_conditional_edges(
    "call_tool",
    # Each agent node updates the 'sender' field
    # the tool calling node does not, meaning
    # this edge will route back to the original agent
    # who invoked the tool
    lambda x: x["sender"],
    {
        "Researcher": "Researcher",
        "Reviewer": "Reviewer",
    },
)
workflow.add_edge(START, "Researcher")
graph = workflow.compile()

def display_graph():
  try:
      # Get the PNG data as bytes
      png_data = graph.get_graph().draw_mermaid_png()
      
      # Save the PNG data to a file
      with open("mermaid_diagram.png", "wb") as f:
          f.write(png_data)
      
      print("Mermaid diagram saved as 'mermaid_diagram.png'")
      
      # Open and display the image using PIL
      img = Image.open(io.BytesIO(png_data))
      img.show()
      
      print("The image should now open in your default image viewer.")
  except Exception as e:
      print(f"Error saving or displaying the diagram: {e}")

# display_graph()

GRAPH_CONFIG = {
    "configurable": {
        "thread_id": "1"
    }
}

def stream_graph_updates(user_input: str):
    events = graph.stream(
        {"messages": [("user", user_input)]},
        GRAPH_CONFIG,
        stream_mode="values",
    )
    for event in events:
        for event in events:
            event["messages"][-1].pretty_print()
        # for value in event.values():
        #     print("Assistant:", value["messages"][-1].content)


while True:
    # try:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    if user_input.lower() in ["graph", "g"]:
        display_graph()
        continue

    stream_graph_updates(user_input)
    # except:
    #     # fallback if input() is not available
    #     user_input = "What do you know about LangGraph?"
    #     print("User: " + user_input)
    #     stream_graph_updates(user_input)
    #     break