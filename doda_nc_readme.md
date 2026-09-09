# Doda NC (Norton Commander Utility)

Doda NC is a lightweight, dual-pane text-mode file manager built in Python using `curses`. It is inspired by the classic Norton Commander from 1986, designed to make copying, moving, and viewing directory structures fast and efficient.

## Features

- **Dual-Pane Interface:** View two different directories side-by-side simultaneously.
- **Fast Navigation:** Traverse directories quickly using keyboard arrows and Enter.
- **Standard File Operations:** Seamlessly copy, move, create, and delete files/directories using classic function keys.
- **Terminal Friendly:** Runs completely in text-mode, rendering natively inside your terminal window using Python's `curses` library.
- **Cross-Platform Logic:** Under the hood, file operations are powered by standard `shutil` and `os`, working across various environments.

## How to Use

To launch the utility, execute the python script in your terminal:

```bash
python doda_nc.py
```

*Note: Ensure your terminal emulator supports text-based interfaces and has sufficient width/height for rendering dual panes.*

## Shortcut Keys

The application strictly relies on standard keystrokes for productivity:

| Key             | Action                                                                                   |
| --------------- | ---------------------------------------------------------------------------------------- |
| **Up Arrow**    | Move the selection cursor up in the active pane.                                         |
| **Down Arrow**  | Move the selection cursor down in the active pane.                                       |
| **Tab**         | Switch focus between the left and right panes.                                           |
| **Enter**       | Open the selected directory. (If `..` is selected, it navigates to the parent folder). |
| **F5 (Copy)**   | Copies the currently selected file or directory to the path of the *inactive* pane.      |
| **F6 (Move)**   | Moves the currently selected file or directory to the path of the *inactive* pane.       |
| **F7 (Mkdir)**  | Prompts for a name and creates a new directory in the *active* pane's path.              |
| **F8 (Delete)** | Deletes the currently selected file or directory.                                        |
| **F10 (Quit)**  | Exits the application.                                                                   |

## Architecture

- `doda_nc.py`: Contains all the `curses` UI logic, drawing, and keyboard event handling.
- `doda_nc_logic.py`: Contains the pure business logic functions (`copy_item`, `move_item`, `make_dir`, `delete_item`).
- `test_doda_nc_logic.py`: Contains unit tests for the core file operations to ensure data safety.
