import os
import tempfile
import pytest
from unittest.mock import patch

from src import folder_util


def test_find_py_files_in_subfolders():
    # given
    with tempfile.TemporaryDirectory() as tmp_dir:
        sub_dir = os.path.join(tmp_dir, 'subdir')
        os.makedirs(sub_dir)
        files = ['test1.py', 'test2.py', 'not_py.txt']
        py_files = files[:2]
        for file in files:
            open(os.path.join(tmp_dir, file), 'a').close()
        expected = [os.path.join(tmp_dir, file) for file in py_files]

        # when
        actual = folder_util.find_py_files_in_subfolders(tmp_dir)

        # then
        assert len(actual) == 2
        assert all(file in actual for file in expected)


@pytest.mark.parametrize("folders, name", [
    (
            [],
            "output1"
    ),
    (
            ['output1', 'outputX'],
            "output2"
    ),
    (
            ['output1', 'output2', 'outputX'],
            "output3"
    )
])
@patch('os.path.isdir', return_value=True)
def test_get_next_folder_name(mocked_isdir, folders, name):
    base_folder = '/path/to/base'

    with patch('os.listdir', return_value=folders):
        assert folder_util.get_next_folder_name(base_folder) == name


def test_copy_folder_successful_copy():
    # given
    source_folder = '/path/to/source'
    destination_folder = '/path/to/destination'

    with patch('shutil.copytree') as mock_copytree:
        # when
        status = folder_util.copy_folder(source_folder, destination_folder)

        # then
        assert status is True
        mock_copytree.assert_called_once_with(source_folder, os.path.abspath(
            destination_folder))


def test_copy_folder_file_exists_error():
    # given
    source_folder = '/path/to/source'
    destination_folder = '/path/to/destination'

    # Mock shutil.copytree to raise FileExistsError
    with patch('shutil.copytree', side_effect=FileExistsError), \
            patch('builtins.print') as mock_print:
        # when
        status = folder_util.copy_folder(source_folder, destination_folder)

        # then
        assert status == False
        mock_print.assert_called_once_with(
            f"Destination folder '{os.path.abspath(destination_folder)}' " +
            "already exists. Please move/delete the existing output folder."
        )


def test_copy_folder_exception():
    # given
    source_folder = '/path/to/source'
    destination_folder = '/path/to/destination'

    # Mock shutil.copytree to raise an exception
    with patch('shutil.copytree', side_effect=Exception('Some error')), \
            patch('builtins.print') as mock_print:
        # when
        status = folder_util.copy_folder(source_folder, destination_folder)

        # then
        assert status == False
        mock_print.assert_called_once_with(f"An error occurred: Some error")


@patch('src.folder_util.get_next_folder_name', return_value="output1")
def test_copy_folder_to_new_output_folder_successful_copy(mock_folder_name):
    # given
    with tempfile.TemporaryDirectory() as tmp_dir:
        source_folder = tmp_dir
        output_path = './outputs'

        with patch('src.folder_util.copy_folder', return_value=True):
            # when
            actual_output_path = folder_util.copy_folder_to_new_output_folder(
                source_folder, output_path)
            # then
            assert actual_output_path == os.path.join(output_path, 'output1')


def test_copy_folder_to_new_output_folder_unsuccessful_copy():
    # given
    with tempfile.TemporaryDirectory() as tmp_dir:
        source_folder = tmp_dir
        output_path = './outputs'

        with patch('src.folder_util.copy_folder', return_value=False):
            # when
            actual_output_path = folder_util.copy_folder_to_new_output_folder(
                source_folder, output_path)
            # then
            assert actual_output_path is None
