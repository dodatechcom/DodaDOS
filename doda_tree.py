import os
import sys

# ANSI color codes
RESET = '\033[0m'
DIR_COLOR = '\033[1;36m'  # Cyan for directories
FILE_COLOR = '\033[0m'    # Default for files
SYMLINK_COLOR = '\033[1;35m' # Magenta for links

def print_tree(directory, prefix=""):
    try:
        entries = sorted(os.listdir(directory))
    except PermissionError:
        print(prefix + "└── " + "\033[1;31m" + "[Permission Denied]" + RESET)
        return

    entries_count = len(entries)

    for i, entry in enumerate(entries):
        path = os.path.join(directory, entry)
        is_last = (i == entries_count - 1)

        # Box drawing characters
        connector = "└── " if is_last else "├── "

        # Determine color
        if os.path.islink(path):
            color = SYMLINK_COLOR
        elif os.path.isdir(path):
            color = DIR_COLOR
        else:
            color = FILE_COLOR

        print(f"{prefix}{connector}{color}{entry}{RESET}")

        if os.path.isdir(path) and not os.path.islink(path):
            # Recursively print subdirectory
            extension = "    " if is_last else "│   "
            print_tree(path, prefix + extension)

def main():
    start_path = "."
    if len(sys.argv) > 1:
        start_path = sys.argv[1]

    if not os.path.exists(start_path):
        print(f"Error: Path '{start_path}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(start_path):
        print(f"Error: Path '{start_path}' is not a directory.")
        sys.exit(1)

    print(f"{DIR_COLOR}{os.path.abspath(start_path)}{RESET}")
    print_tree(start_path)

if __name__ == "__main__":
    main()
