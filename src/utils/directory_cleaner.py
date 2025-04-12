import shutil
import os

def ensure_clean_directory(directory_path: str):
    """
    Ensures the directory exists and is empty.
    """
    shutil.rmtree(directory_path, ignore_errors=True)
    os.makedirs(directory_path, exist_ok=True)

# Example usage
# ensure_clean_directory("/path/to/directory")


if __name__ == "__main__":
    test_directory = "./temp/test"
    print(os.listdir(test_directory))
    os.makedirs(test_directory, exist_ok=True)
    with open(f"{test_directory}/test.txt", "w") as f:
        f.write("Test")
    ensure_clean_directory(test_directory)
    print("Directory cleaned successfully")
    