import os

file_path = r"\\?\D:\dev\tdx\nul"

print(f"Checking for existence of: {file_path}")
if os.path.exists(file_path):
    try:
        os.remove(file_path)
        print(f"Successfully deleted {file_path}")
    except Exception as e:
        print(f"Error deleting {file_path}: {e}")
else:
    print(f"File {file_path} does not exist")
