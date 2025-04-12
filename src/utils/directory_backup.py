import shutil
import os

def backup_directory(src_path: str, des_path: str):
    """
    Copies all files and directories from src_path to des_path.

    src_path (str): The source directory path.
    des_path (str): The destination directory path.
    shutil.copytree(src_path, des_path, dirs_exist_ok=True)

    Raises:
    FileNotFoundError: If the source directory does not exist.
    FileExistsError: If the destination directory already exists.
    """
    shutil.copytree(src_path, des_path, dirs_exist_ok=True)

# Example usage

if __name__ == "__main__":
    src_path = "/home/tanpohkeam/ubts/msg_app/data/rag"
    des_path = "/home/tanpohkeam/ubts/msg_app/outputs/rag"
    backup_directory(src_path, des_path)
    