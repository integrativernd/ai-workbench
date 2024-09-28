import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from llm.anthropic_integration import get_basic_message
import json

def append_tool_class(file_path, new_tool_class):
    with open(file_path, 'r') as file:
        content = file.read()

    # Find the position of the comment
    comment_pos = content.find("# AI ADD CLASSES HERE")
    if comment_pos == -1:
        raise ValueError("Could not find the END TOOL RESPONDERS comment")

    # Find the start of the line where the comment begins
    line_start = content.rfind('\n', 0, comment_pos) + 1

    # Insert the new tool class with appropriate spacing
    insert_content = f"\n{new_tool_class}\n"
    content = content[:line_start] + insert_content + content[line_start:]

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.write(content)

def update_tool_registry(file_path, tool_name):
    with open(file_path, 'r') as file:
        content = file.readlines()

    registry_start = None
    registry_end = None

    # Find the tool registry initialization
    for i, line in enumerate(content):
        if line.strip().startswith('tool_registry = ToolRegistry()'):
            registry_start = i
            break

    if registry_start is None:
        raise ValueError("Tool registry initialization not found")

    # Find the end of the tool registry initialization
    for i in range(registry_start + 1, len(content)):
        if not content[i].strip().startswith('tool_registry.register('):
            registry_end = i
            break

    if registry_end is None:
        raise ValueError("End of tool registry initialization not found")
    
    tool_function_name = tool_name.lower().replace(' ', '_')

    # Insert the new tool registration
    new_registration = f"tool_registry.register(\"{tool_function_name}\", {tool_name}())\n"
    content.insert(registry_end, new_registration)

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.writelines(content)

def add_tool_responder():
    file_path = 'llm/respond.py' # Replace with your actual file path

    prompt = """
        Create a AddressGithubIssueTool class. It is used for reading the contents of an existing github issues
        and working to address the issue. It should take a title and a description.\n
    """

    with open(file_path, 'r') as file:
        existing_code = file.read()

    class_name_message = get_basic_message(
        """
        Generate a logical class name for a tool to address the user's request.
        Only return the name for a valid Python class (no spaces, special characters, or numbers at the beginning).
        """,
        [{
            "role": "user",
            "content": prompt
        }]
    )
    class_name = class_name_message.content[0].text
    class_implementation_message = get_basic_message(
        f"""
        Based on the existing code {existing_code} implement a class named {class_name} that will be used to address the user's request.
        Only return the code for the class definition with no comments or docstrings.
        """,
        [{
            "role": "user",
            "content": class_name
        }]
    )
    class_implementation = class_implementation_message.content[0].text

    
    try:
        # new_tool_class_data = message.content[0].text
        # print(new_tool_class_data)
        # new_tool_class_object = json.loads(new_tool_class_data)
        append_tool_class(file_path, class_implementation)
        update_tool_registry(file_path, class_name)
        print("Tool class added and registered successfully.")
    except Exception as e:
        print(f"Error adding tool class: {e}")
    

if __name__ == "__main__":
    add_tool_responder()