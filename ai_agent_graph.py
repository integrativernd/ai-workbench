from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_anthropic import ChatAnthropic
from IPython.display import Image, display
from langchain_community.tools.tavily_search import TavilySearchResults
from PIL import Image
import io
import json
# from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

search_tool = TavilySearchResults(max_results=2)

# tools = [tool]
# print(search_tool.invoke("What's a 'node' in LangGraph?"))

llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm_with_tools = llm.bind_tools([search_tool])


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]





def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[search_tool])

graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition
)

graph_builder.add_edge("tools", "chatbot")

graph_builder.set_entry_point("chatbot")

graph = graph_builder.compile(checkpointer=memory)

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
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        if user_input.lower() in ["graph", "g"]:
            display_graph()
            continue

        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break
    
# NOTES

# def route_tools(
#     state: State,
# ):
#     """
#     Use in the conditional_edge to route to the ToolNode if the last message
#     has tool calls. Otherwise, route to the end.
#     """
#     if isinstance(state, list):
#         ai_message = state[-1]
#     elif messages := state.get("messages", []):
#         ai_message = messages[-1]
#     else:
#         raise ValueError(f"No messages found in input state to tool_edge: {state}")
#     if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
#         return "tools"
#     return END

# graph_builder.add_conditional_edges(
#     "chatbot",
#     tools_condition,
#     route_tools,
#     # The following dictionary lets you tell the graph to
#     # interpret the condition's outputs as a specific node
#     # It defaults to the identity function, but if you
#     # want to use a node named something else apart from "tools",
#     # You can update the value of the dictionary to something else
#     # e.g., "tools": "my_tools"
#     {"tools": "tools", END: END},
# )

# class BasicToolNode:
#     """A node that runs the tools requested in the last AIMessage."""

#     def __init__(self, tools: list) -> None:
#         self.tools_by_name = {tool.name: tool for tool in tools}

#     def __call__(self, inputs: dict):
#         if messages := inputs.get("messages", []):
#             message = messages[-1]
#         else:
#             raise ValueError("No message found in input")
#         outputs = []
#         for tool_call in message.tool_calls:
#             tool_result = self.tools_by_name[tool_call["name"]].invoke(
#                 tool_call["args"]
#             )
#             outputs.append(
#                 ToolMessage(
#                     content=json.dumps(tool_result),
#                     name=tool_call["name"],
#                     tool_call_id=tool_call["id"],
#                 )
#             )
#         return {"messages": outputs}