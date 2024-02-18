import pytest
from unittest.mock import patch, call, mock_open

from src import file_handler


def test_write_to_file():
    # given
    open_mock = mock_open()
    
    # when
    with patch("builtins.open", open_mock, create=True):
        file_handler.write_to_file("output.py", ["line 1", "", "line 3"])

    # then
    open_mock.assert_has_calls([
        call("output.py", "w"),
        call().write("line 1\n"),
        call().write("\n"),
        call().write("line 3\n")
    ])


def test_read_from_file():
    # given
    file_content = "line1\n   \nline3"
    open_mock = mock_open(read_data=file_content)
    
    # when
    with patch("builtins.open", open_mock):
        result=file_handler.read_from_file("input.py")

    # then
    assert result == ["line1", "", "line3"]
    open_mock.assert_called_with("input.py", "r")