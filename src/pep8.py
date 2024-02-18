import ast


def apply_rules(lines):

    lines = find_code(lines, replace_tabs)
    lines = move_imports_to_start(lines)
    lines = split_imports(lines)
    lines = format_newlines(lines)
    lines = remove_trailing_newlines(lines)
    lines = split_long_comments(lines)

    return lines


# Helper function to check for triple quotes
def is_triple_quotes(line, idx, char):
    if idx + 2 < len(line):
        return char == line[idx + 1] == line[idx + 2]
    else:
        return False


def find_code(lines, callback):
    modified_lines = []
    in_string = False
    in_triple_quotes = False
    apostrophe = None
    for line in lines:
        modified_line = ""
        in_comment = False
        for idx, char in enumerate(line):
            if in_comment:
                modified_line += char
            else:
                # Inside a string
                if in_string:
                    modified_line += char
                    if in_triple_quotes and char == apostrophe:
                        # Check for triple quotes end
                        if is_triple_quotes(line, idx, apostrophe):
                            in_triple_quotes = False
                            in_string = False
                    elif char == apostrophe:
                        in_string = False
                # Outside of strings
                else:
                    if char == "#":
                        modified_line += char
                        in_comment = True
                    elif char in ["'", '"']:
                        modified_line += char
                        # Check for triple quotes start
                        if is_triple_quotes(line, idx, char):
                            in_triple_quotes = True
                        in_string = True
                        apostrophe = char
                    else:
                        # Apply callback to characters outside of strings
                        modified_line += callback(line, idx)
        modified_lines.append(modified_line)

    return modified_lines


def replace_tabs(line, idx):
    if line[idx] == "\t":
        print(f"replaced tab in line: {line}")
        return "    "
    else:
        return line[idx]


def move_imports_to_start(lines):
    code = "\n".join(lines)
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        print(f"Error parsing code: {e}")
        return lines
    
    imports_on_depth_0 = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for line in range(node.lineno, node.end_lineno+1):
                imports_on_depth_0.append(line)
    if imports_on_depth_0:
        print(f"Moving imports from lines: {imports_on_depth_0} ")

    indexes = [idx-1 for idx in imports_on_depth_0]
    moved_lines = [lines[i] for i in indexes]
    remaining_lines = [line for index, line in enumerate(
        lines) if index not in indexes]
    lines = moved_lines + remaining_lines
    return lines


def split_imports(lines):
    indent_level = 0
    for idx, line in enumerate(lines):
        if line.strip().startswith("import"):
            imports = line.split(",")
            if len(imports) > 1:
                print(f"Splitting imports in line {idx}: {line}")
                # Adjust indent to match the original line's indentation level
                indent = line[:line.find("import")]
                indent_level = len(indent)
                lines[idx] = imports[0]

                for package in imports[1:]:
                    package = package.strip()
                    idx += 1
                    # Insert new import line with the same indentation level
                    lines.insert(idx, " " * indent_level + "import " + package)
    return lines


def format_newlines_between_functions_and_classes(lines):
    code = "\n".join(lines)
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        print(f"Error parsing code: {e}")
        return lines
    
    function_and_class_starts = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            function_and_class_starts.append(node.lineno)
    if function_and_class_starts:
        print("Formatting newlines between functions and classes...")

    function_and_class_starts = [x - 1 for x in function_and_class_starts]
    idx = 0
    while idx < len(function_and_class_starts):
        current_line = function_and_class_starts[idx]
        while (current_line >= 1
               and (lines[current_line - 1].strip() == ""
                    or lines[current_line - 1].strip().startswith("@"))):
            if lines[current_line - 1].strip().startswith("@"):
                current_line -= 1
            else:
                lines.pop(current_line - 1)
                function_and_class_starts = [x - 1 for x
                                             in function_and_class_starts]
                current_line -= 1
                
        if current_line > 0:
            lines.insert(current_line, "")
            lines.insert(current_line, "")
            function_and_class_starts = [x + 2 for x
                                         in function_and_class_starts]
        idx += 1

    return lines


def format_newlines_between_methods(lines):
    code = "\n".join(lines)
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        print(f"Error parsing code: {e}")
        return lines
    
    method_starts = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for class_node in node.body:
                if isinstance(class_node, ast.FunctionDef):
                    method_starts.append(class_node.lineno)
    if method_starts:
        print("Formatting newlines between methods...")

    method_starts = [x - 1 for x in method_starts]
    idx = 0
    while idx < len(method_starts):
        current_line = method_starts[idx]
        while (current_line >= 1
               and (lines[current_line - 1].strip() == ""
                    or lines[current_line - 1].strip().startswith("@"))):
            if lines[current_line - 1].strip().startswith("@"):
                current_line -= 1
            else:
                lines.pop(current_line - 1)
                method_starts = [x - 1 for x in method_starts]
                current_line -= 1

        lines.insert(current_line, "")
        method_starts = [x + 1 for x in method_starts]
        idx += 1

    return lines


def format_newlines(lines):
    lines = format_newlines_between_functions_and_classes(lines)
    lines = format_newlines_between_methods(lines)
    return lines


def split_long_comments(lines, max_length=79):
    new_lines = []
    comment_buffer = ''
    indent_level = 0
    for line in lines:
        if line.strip().startswith("#"):
            indent = line[:line.find("#")]
            indent_level = len(indent)
            comment_buffer += line.strip()[1:].strip() + ' '
        else:
            while len(comment_buffer) > max_length - 2 - indent_level:
                split_index = comment_buffer.rfind(" ", 0, max_length
                                                   - 2 - indent_level)
                if split_index == -1:
                    split_index = max_length
                new_lines.append(" " * indent_level + "# "
                                 + comment_buffer[:split_index])
                comment_buffer = comment_buffer[split_index:].strip()
            
            # append the leftover
            if comment_buffer:
                new_lines.append(" " * indent_level + "# " + comment_buffer)
                comment_buffer = ''
            
            new_lines.append(line)

    if comment_buffer:
        new_lines.append("# " + comment_buffer)

    return new_lines


def remove_trailing_newlines(lines):
    # newlines are only removed because a newline is added at the end
    # while saving the file
    if len(lines) > 0 and lines[-1].strip() == "":
        while len(lines) > 0 and lines[-1].strip() == "":
            lines.pop()
    return lines
