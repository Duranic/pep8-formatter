import argparse
import os

import folder_util
import file_handler
import pep8


def main():
    parser = argparse.ArgumentParser("pep8 tool")
    parser.add_argument("-f", "--folder_path", type=str,
                        help="folder path", default="./test")
    args = parser.parse_args()

    folder_path = args.folder_path
    if not folder_path and os.path.isdir(folder_path):
        print("Invalid folder path. Please provide a valid folder path.")
        exit()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(dir_path, "../outputs")

    count = count_py_files_in_folder(folder_path)
    if count:
        output_path = folder_util.copy_folder_to_new_output_folder(folder_path,
                                                                   output_path)
        if output_path:
            files = folder_util.find_py_files_in_subfolders(output_path)
            process_files_with_pep8(files)


def count_py_files_in_folder(folder_path):
    files = folder_util.find_py_files_in_subfolders(folder_path)
    count = len(files)
    print(f"Found {count} .py file{'s' if count != 1 else ''}"
          f" in the provided folder path")
    print("Files:")
    for file in files:
        print(f"    {file}")
    return count


def process_files_with_pep8(files):
    for file in files:
        print(f"\nProcessing file: {file}")
        lines = file_handler.read_from_file(file)
        lines = pep8.apply_rules(lines)
        file_handler.write_to_file(file, lines)


if __name__ == "__main__":
    main()
