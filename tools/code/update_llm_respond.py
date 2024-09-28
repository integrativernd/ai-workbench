import re

def update_file(file_path, new_import, new_tool_name, new_tool_function, new_tool_inputs):
    with open(file_path, 'r') as file:
        content = file.readlines()

    # Add new import
    import_section_end = 0
    for i, line in enumerate(content):
        if line.strip() and not line.strip().startswith('from') and not line.strip().startswith('import'):
            import_section_end = i
            break
    content.insert(import_section_end, f"{new_import}\n")

    # Update TOOL_MAP
    tool_map_start = None
    tool_map_end = None
    for i, line in enumerate(content):
        if 'TOOL_MAP: Dict[str, ToolFunction] = {' in line:
            tool_map_start = i
            break
    
    if tool_map_start is None:
        raise ValueError("TOOL_MAP not found in the file")

    # Find the end of TOOL_MAP
    bracket_count = 1
    for i in range(tool_map_start + 1, len(content)):
        bracket_count += content[i].count('{') - content[i].count('}')
        if bracket_count == 0:
            tool_map_end = i
            break

    if tool_map_end is None:
        raise ValueError("End of TOOL_MAP not found")

    # Add new tool to TOOL_MAP
    indent = re.match(r'\s*', content[tool_map_end-1]).group()
    new_tool_line = f'{indent}"{new_tool_name}": {new_tool_function},\n'
    content.insert(tool_map_end, new_tool_line)

    # Update TOOL_INPUT_MAP
    input_map_start = None
    input_map_end = None
    for i, line in enumerate(content):
        if 'TOOL_INPUT_MAP: Dict[str, List[str]] = {' in line:
            input_map_start = i
            break
    
    if input_map_start is None:
        raise ValueError("TOOL_INPUT_MAP not found in the file")

    # Find the end of TOOL_INPUT_MAP
    bracket_count = 1
    for i in range(input_map_start + 1, len(content)):
        bracket_count += content[i].count('{') - content[i].count('}')
        if bracket_count == 0:
            input_map_end = i
            break

    if input_map_end is None:
        raise ValueError("End of TOOL_INPUT_MAP not found")

    # Add new tool inputs to TOOL_INPUT_MAP
    indent = re.match(r'\s*', content[input_map_end-1]).group()
    new_input_line = f'{indent}"{new_tool_name}": {new_tool_inputs},\n'
    content.insert(input_map_end, new_input_line)

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.writelines(content)

def main():
    file_path = 'llm/respond.py'
    new_import = '    open_pull_request,'
    new_tool_name = 'open_pull_request'
    new_tool_function = 'lambda data: django_rq.enqueue(open_pull_request, data)'
    new_tool_inputs = '["description"]'

    update_file(file_path, new_import, new_tool_name, new_tool_function, new_tool_inputs)

if __name__ == '__main__':
    main()