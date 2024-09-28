import re

def append_tool_class(file_path, new_tool_class):
    with open(file_path, 'r') as file:
        content = file.read()

    # Find the position to insert the new tool class
    last_tool_class_pos = content.rfind('class', 1, content.rfind('class ToolRegistry')) - 1
    if last_tool_class_pos == -1:
        raise ValueError("Could not find appropriate position to insert new tool class")

    # Insert the new tool class
    content = content[:last_tool_class_pos] + new_tool_class + "\n" + content[last_tool_class_pos:]

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

    # Insert the new tool registration
    new_registration = f"tool_registry.register(\"{tool_name}\", {tool_name}())\n"
    content.insert(registry_end, new_registration)

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.writelines(content)

def main():
    file_path = 'llm/respond.py'  # Replace with your actual file path
    
    new_tool_class = """
class OpenDiagnosticTool(BaseTool):
    def __init__(self):
        super().__init__(["description"])

    def execute(self, request_data):
        # Implement the logic to open a pull request here
        print(f"Opening pull request with description: {request_data['description']}")
        request_data['content'] = "Pull request opened successfully."
        return request_data
"""

    append_tool_class(file_path, new_tool_class)
    update_tool_registry(file_path, "OpenPullRequestTool")

    print("Tool class added and registered successfully.")

if __name__ == "__main__":
    main()