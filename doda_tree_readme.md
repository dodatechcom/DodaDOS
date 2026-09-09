# Doda Tree (Visual Directory Tree)

Doda Tree is a command-line utility inspired by the classic MS-DOS `TREE` command. It recursively maps out the structure of a directory and prints it in a visually pleasing, graphical tree format using ANSI colors and Unicode box-drawing characters.

## Features

- **Graphical Hierarchy:** Clearly displays parent-child folder relationships using line characters (`├──` and `└──`).
- **Color Coding:** Differentiates between standard files, directories (Cyan), and symbolic links (Magenta) for quick visual scanning.
- **Permission Safe:** Gracefully handles permission-denied directories without crashing the entire scan.

## How to Use

Execute the utility from your terminal. If no path is provided, it scans the current working directory (`.`).

```bash
python doda_tree.py [directory_path]
```

### Examples

Scan the current directory:
```bash
python doda_tree.py
```

Scan a specific directory (e.g., `/var/log`):
```bash
python doda_tree.py /var/log
```
