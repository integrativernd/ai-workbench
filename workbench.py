import ast
import astor

def update_list_variable(file_path, variable_name, new_item):
    # Read the file content
    with open(file_path, 'r') as file:
        content = file.read()

    # Parse the content into an AST
    tree = ast.parse(content)

    # Find the variable assignment
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable_name:
                    # Found the variable assignment
                    if isinstance(node.value, ast.List):
                        # Add the new item to the list
                        node.value.elts.append(ast_from_value(new_item))
                        break
                    else:
                        raise ValueError(f"{variable_name} is not a list")

    # Generate the modified code
    modified_code = astor.to_source(tree)

    # Write the modified code back to the file
    with open(file_path, 'w') as file:
        file.write(modified_code)

def ast_from_value(value):
    if isinstance(value, dict):
        return ast.Dict(
            keys=[ast_from_value(k) for k in value.keys()],
            values=[ast_from_value(v) for v in value.values()]
        )
    elif isinstance(value, list):
        return ast.List(elts=[ast_from_value(item) for item in value])
    elif isinstance(value, str):
        return ast.Str(s=value)
    elif isinstance(value, (int, float, bool, type(None))):
        return ast.Constant(value=value)
    else:
        raise ValueError(f"Unsupported type: {type(value)}")

# Example usage
new_tool = {
    "name": "new_tool",
    "description": "This is a new tool",
    "input_schema": {
        "type": "object",
        "properties": {
            "param": {
                "type": "string",
                "description": "A parameter for the new tool"
            }
        },
        "required": ["param"]
    }
}

update_list_variable('config/settings.py', 'TOOL_DEFINITIONS', new_tool)