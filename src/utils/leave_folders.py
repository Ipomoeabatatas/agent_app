import os

def find_non_empty_leaf_folders(root_path):
    non_empty_leaf_folders = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        if not dirnames and filenames:
            non_empty_leaf_folders.append(dirpath)

    return non_empty_leaf_folders

# Example usage
if __name__ == "__main__":
    root_path = "/path/to/your/root/folder"
    root_path = "/home/tanpohkeam/ubts/msg_app/data"
    result = find_non_empty_leaf_folders(root_path)
    for folder in result:
        print(folder)
        
        # Suggested file: /home/tanpohkeam/ubts/msg_app/src/utils/leaf_folder_utils.py
        # Suggested function name: get_non_empty_leaf_folders

        def get_non_empty_leaf_folders(root_path):
            return find_non_empty_leaf_folders(root_path)