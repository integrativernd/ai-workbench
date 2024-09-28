import re

def append_tool(list_variable, file_path, new_tool):
    with open(file_path, 'r') as file:
        content = file.readlines()

    tool_definitions_start = None
    tool_definitions_end = None
    indent = ''

    # Find the TOOL_DEFINITIONS list
    for i, line in enumerate(content):
        if f'{list_variable} = [' in line:
            tool_definitions_start = i
            indent = re.match(r'\s*', line).group()
            break

    if tool_definitions_start is None:
        raise ValueError(f"{list_variable} not found in the file")

    # Find the end of the TOOL_DEFINITIONS list
    bracket_count = 1
    for i in range(tool_definitions_start + 1, len(content)):
        bracket_count += content[i].count('[') - content[i].count(']')
        if bracket_count == 0:
            tool_definitions_end = i
            break

    if tool_definitions_end is None:
        raise ValueError(f"End of {list_variable} not found")

    # Format the new tool
    new_tool_lines = [f"{indent}    {{\n"]
    for key, value in new_tool.items():
        if isinstance(value, dict):
            new_tool_lines.append(f'{indent}        "{key}": {{\n')
            for sub_key, sub_value in value.items():
                new_tool_lines.append(f'{indent}            "{sub_key}": {repr(sub_value)},\n')
            new_tool_lines.append(f'{indent}        }},\n')
        else:
            new_tool_lines.append(f'{indent}        "{key}": {repr(value)},\n')
    new_tool_lines.append(f"{indent}    }},\n")

    # Insert the new tool
    content[tool_definitions_end:tool_definitions_end] = new_tool_lines

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.writelines(content)

def main():
    # Example usage
    new_tool = {
        "name": "open_pull_request",
        "description": "Invoke this tool when asked to make a pull request",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "Description of the pull request"},
            },
            "required": ["description"]
        }
    }

    append_tool("TOOL_DEFINITION", 'config/settings.py', new_tool)

if __name__ == "__main__":
    main()