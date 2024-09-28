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

def update_tool_registry(file_path, function_name, class_name):
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

    # Insert the new tool registration
    new_registration = f"tool_registry.register(\"{function_name}\", {class_name}())\n"
    content.insert(registry_end, new_registration)

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.writelines(content)

def snake_to_pascal(snake_str):
    return ''.join(word.capitalize() for word in snake_str.split('_'))

def add_tool_responder():
    file_path = 'llm/respond.py' # Replace with your actual file path

    prompt = """
        Create a tool to address an existing github issue. Its name should
        clearly indicate that it is designed for an AI agent to analyze a
        specified github issue and work on a solution.
    """

    with open(file_path, 'r') as file:
        existing_code = file.read()

    function_name_message = get_basic_message(
        """
        Generate a logical class name for a tool to address the user's request.
        Only return the name for a valid Python function name (no spaces, special characters, etc.).
        Words should be logically separate with underscores.
        Example: "send_sales_email"
        """,
        [{
            "role": "user",
            "content": prompt
        }]
    )
    function_name = function_name_message.content[0].text
    # turn the function name into a class name
    class_name = snake_to_pascal(function_name)
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
        update_tool_registry(file_path, function_name, class_name)
        print("Tool class added and registered successfully.")
    except Exception as e:
        print(f"Error adding tool class: {e}")
    

if __name__ == "__main__":
    add_tool_responder()