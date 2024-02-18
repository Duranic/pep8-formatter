import pytest
from unittest.mock import patch
from io import StringIO

from src import pep8


@pytest.mark.parametrize("lines, expected_lines", [
    ([], []), ([""], []),
    (
            ["sample code", "", "sample code2"],
            ["sample code", "", "sample code2"]
    ),
    (
            ["sample code", "", "sample code2", ""],
            ["sample code", "", "sample code2"]
    ),
    (
            ["sample code", "", "sample code2", "", "", ""],
            ["sample code", "", "sample code2"]
    )
])
def test_remove_trailing_newlines(lines, expected_lines):
    actual_lines = pep8.remove_trailing_newlines(lines)

    assert actual_lines == expected_lines


@pytest.mark.parametrize("lines, expected_lines", [
    ([], []), ([""], [""]),
    (["import os"], ["import os"]),
    (
            ["import os,     sys"],
            ["import os", "import sys"]
    ),
    (
            ["import pkg, pkg2, numpy", "", "sample code"],
            ["import pkg", "import pkg2", "import numpy", "", "sample code"]
    ),
    (
            ["import os, sys", "", "import numpy", "", "sample code"],
            ["import os", "import sys", "", "import numpy", "", "sample code"]
    ),
])
def test_split_imports(lines, expected_lines):
    actual_lines = pep8.split_imports(lines)

    assert actual_lines == expected_lines


@pytest.mark.parametrize("lines, expected_result", [
    (
            ["def test_function():", "    print('No imports')"],
            ["def test_function():", "    print('No imports')"]
    ),
    (
            [
                "def test_function():",
                "    import os",
                "    import sys",
                "    print('With imports in function')"
            ],
            [
                "def test_function():",
                "    import os",
                "    import sys",
                "    print('With imports in function')"
            ]
    ),
    (
            [
                "def test_function():",
                "    import os",
                "    import sys",
                "import numpy",
                "print('With imports outside function')",
            ],
            [
                "import numpy",
                "def test_function():",
                "    import os",
                "    import sys",
                "print('With imports outside function')",
            ]
    ),
])
def test_move_imports_to_start(lines, expected_result):
    actual_lines = pep8.move_imports_to_start(lines)

    assert actual_lines == expected_result


@patch('sys.stdout', new_callable=StringIO)
def test_move_imports_to_start_unparsable_code(mock_stdout):
    # ast can't parse the code so the function returns the unchanged lines
    # and prints the error

    lines = ["def test_function():",
             "import numpy",
             "print('Cant parse since nothing in function')"]

    actual_lines = pep8.move_imports_to_start(lines)

    assert actual_lines == lines
    assert mock_stdout.getvalue() == ("Error parsing code: expected an "
                                      "indented block (<unknown>, line 2)\n")


@pytest.fixture
def example_code():
    return [
        "",
        "class MyClass:",
        "    def __init__(self):",
        "        pass",
        "",
        "",
        "    def method1(self):",
        "        pass",
        "    def method2(self):",
        "        pass",
        "def my_function():",
        "    pass",
        "",
        "",
        "",
        "@decorator",
        "def my_function_with_decorator():",
        "    pass"
    ]


def test_format_newlines_between_functions_and_classes(example_code):
    expected_lines = [
        "class MyClass:",
        "    def __init__(self):",
        "        pass",
        "",
        "",
        "    def method1(self):",
        "        pass",
        "    def method2(self):",
        "        pass",
        "",
        "",
        "def my_function():",
        "    pass",
        "",
        "",
        "@decorator",
        "def my_function_with_decorator():",
        "    pass"
    ]

    formatted_lines = pep8.format_newlines_between_functions_and_classes(
        example_code)
    assert formatted_lines == expected_lines


def test_format_newlines_between_methods(example_code):
    expected_lines = [
        "",
        "class MyClass:",
        "",
        "    def __init__(self):",
        "        pass",
        "",
        "    def method1(self):",
        "        pass",
        "",
        "    def method2(self):",
        "        pass",
        "def my_function():",
        "    pass",
        "",
        "",
        "",
        "@decorator",
        "def my_function_with_decorator():",
        "    pass"
    ]

    formatted_lines = pep8.format_newlines_between_methods(example_code)
    assert formatted_lines == expected_lines


def test_split_long_comments():
    input_lines = [
        "This is a normal line",
        "    # This is a very long comment that needs to be split into"
        + " multiple lines to fit the max length requirement",
        "    # This is another long comment that needs to be split into"
        + " multiple lines to fit the max length requirement",
        "    # Short comment",
        "This is another normal line"
    ]
    expected_lines = [
        "This is a normal line",
        "    # This is a very long comment that needs to be split into"
        + " multiple lines",
        "    # to fit the max length requirement This is another"
        + " long comment that",
        "    # needs to be split into multiple lines to fit the"
        + " max length requirement",
        "    # Short comment",
        "This is another normal line"
    ]

    actual_lines = pep8.split_long_comments(input_lines)

    assert actual_lines == expected_lines


@pytest.mark.parametrize("input_lines, expected_lines", [
    ([], []),
    (["", "", "", ""], []),
    (
            ["Single line"],
            ["Single line"]),
    (
            ["This is a line", "This is another line", ""],
            ["This is a line", "This is another line"]
    ),
    (
            ["This is a line", "This is another line", "", ""],
            ["This is a line", "This is another line"]
    )
])
def test_remove_trailing_newlines(input_lines, expected_lines):
    actual_lines = pep8.remove_trailing_newlines(input_lines)

    assert actual_lines == expected_lines


@pytest.mark.parametrize("input_lines, expected_output", [
    (
            ["\tprint('Hello, world!')"],
            ["    print('Hello, world!')"]
    ),
    (
            ["    if x < 10:\t"],
            ["    if x < 10:    "]
    ),
    (
            ["    # This is a comment with a tab\t"],
            ["    # This is a comment with a tab\t"]
    ),
    (
            ["\t\tprint('Indented with tabs')"],
            ["        print('Indented with tabs')"]
    ),
    # Test case for string
    (
            ["print('Indented with a\ttab')"],
            ["print('Indented with a\ttab')"]
    ),
    # Test case for string with triple quotes
    (
            ["print('''Indented with\ttabs''')"],
            ["print('''Indented with\ttabs''')"]
    )
])
def test_find_code(input_lines, expected_output):
    modified_lines = pep8.find_code(input_lines, pep8.replace_tabs)

    assert modified_lines == expected_output


@pytest.mark.parametrize("line, idx, char, expected", [
    ('"""', 0, '"', True),  # Triple quotes at index 0
    ('   """', 3, '"', True),  # Triple quotes after spaces
    ("   '''", 3, "'", True),  # Triple single quotes 
    ('def function():', 3, '"', False),  # Not part of triple quotes
    ('', 0, '"', False),  # Empty line
    ('"', 0, '"', False),  # Single quote
    ('""', 0, '"', False),  # Double quotes
    ('   """', 3, "'", False),  # Triple quotes inside ' string
])
def test_is_triple_quotes(line, idx, char, expected):
    actual = pep8.is_triple_quotes(line, idx, char)

    assert actual == expected


@pytest.mark.parametrize("line, idx, expected", [
    ("\tdef function():", 0, "    "),
    ("def\tfunction():", 3, "    "),
    ("def function():", 3, " "),
    ("def function():", 4, "f")
])
def test_replace_tabs(line, idx, expected):
    actual = pep8.replace_tabs(line, idx)

    assert actual == expected
