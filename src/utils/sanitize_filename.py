

"""
This module provides a utility function to sanitize filenames by removing or replacing
special characters that might cause issues with file systems.
Functions:
    sanitize_filename(filename: str) -> str:
        Sanitizes a filename by removing or replacing special characters.
Usage Example:
    To sanitize a filename, use the `sanitize_filename` function:
    sanitized_name = sanitize_filename("example filename.txt")
    print(sanitized_name)  # Output: example_filename.txt
The module also includes a demonstration and testing section that showcases the usage
of the `sanitize_filename` function with various test cases.
"""

import re

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename by removing or replacing special characters that might
    cause issues with file systems.
    
    Args:
        filename (str): The original filename.
    
    Returns:
        str: A sanitized filename.
    """

    max_name_length = 40
    # Strip leading/trailing spaces and replace spaces with underscores
    filename = filename.strip().replace(" ", "_")

    # Replace invalid characters with an underscore
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    
    # Replace single and double quotes with an underscore
    filename = filename.replace("'", "_").replace('"', "_")
    
    # Split the filename into name and extension
    if '.' in filename:
        name, ext = filename.rsplit('.', 1)
        # Ensure the name length is within safe limits (40 chars)
        name = name[:max_name_length]
        filename = f"{name}.{ext}"
    else:
        filename = filename[:max_name_length]

    # Prevent trailing dots (Windows restriction)
    filename = filename.rstrip(".")

    # If filename becomes empty, use a default name
    return filename if filename else "default_filename"

## demo and testing
if __name__ == "__main__":
    """
    Main function to demonstrate the sanitize_filename utility.
    """
    test_filenames = [
        "my file.txt",
        "invalid*name?.txt",
        "   spaces  at  start and end   .txt   ",
        "super_long_filename_" + "a" * 80 + ".txt",
        "",
        "normal_file-name.doc", 
        "'BC_-_PRIMA_-_KASEJKT032248_(CCSU72532139.pdf'"
    ]

    print("Sanitized Filenames:")
    for original in test_filenames:
        sanitized = sanitize_filename(original)
        print(f"Original: {original}")
        print(f"Sanitized: {sanitized}")
        print()
        
