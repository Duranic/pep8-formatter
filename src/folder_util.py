import shutil
import os


def find_py_files_in_subfolders(folder_path):
    files = []
    for folder, subfolders, filenames in os.walk(folder_path):
        for file in filenames:
            if file.endswith(".py"):
                file_path = os.path.join(folder, file)
                file_path = os.path.normpath(file_path)
                files.append(file_path)
    return files


def copy_folder(source_folder, destination_folder):
    destination_path = os.path.abspath(destination_folder)
    try:
        shutil.copytree(source_folder, destination_path)
        print(
            f"Folder '{source_folder}' successfully copied " +
            f"to '{os.path.abspath(destination_path)}'.")
        return True
    except FileExistsError:
        print(
            f"Destination folder '{os.path.abspath(destination_path)}' " +
            "already exists. Please move/delete the existing output folder.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def get_next_folder_name(base_folder):
    # Get a list of existing folders in the base folder
    existing_folders = [folder for folder in os.listdir(base_folder)
                        if os.path.isdir(os.path.join(base_folder, folder))]
    
    # Find the highest numbered folder
    highest_number = 0
    for folder in existing_folders:
        try:
            folder_number = int(folder.split("output")[-1])
            highest_number = max(highest_number, folder_number)
        except ValueError:
            pass

    # Create the name for the next folder
    next_folder_name = f"output{highest_number + 1}"
    return next_folder_name


def copy_folder_to_new_output_folder(folder_path, output_path):
    folder_name = get_next_folder_name(output_path)
    output_path = os.path.join(output_path, folder_name)
    copy_status = copy_folder(folder_path, output_path)
    if copy_status:
        return output_path
    else:
        return None
