# Doda Find (File Search Utility)

Doda Find is a fast, interactive, text-mode file search utility built in Python with `curses`. Inspired by classic DOS search tools (like Norton's FileFind), it allows you to quickly locate files across directories and inspect their contents without leaving your terminal.

## Features

- **Interactive UI:** A classic split-pane interface with search criteria at the top and results at the bottom.
- **Deep Search:** Search for files by wildcard masks (e.g., `*.py`) and containing text across an entire directory tree.
- **Built-in Viewer:** Instantly view the contents of any file in the search results using the integrated text viewer.

## How to Use

Execute the utility from your terminal:

```bash
python doda_find.py
```

### Navigating the Interface

When you launch the app, you will be in the **Search Criteria** panel.
1. Use **TAB** to move between fields (Directory, File Mask, Text).
2. Press **ENTER** to edit a field (a prompt will appear at the bottom of the screen).
3. Press **'s'** (while in the criteria panel) to execute the search.
4. Once results appear, focus shifts to the **Results** panel where you can use arrow keys to navigate.

## Shortcut Keys

| Key             | Action                  |
| --------------- | ----------------------- |
| **TAB**         | Cycle through input fields and the results pane. |
| **ENTER**       | Edit the currently highlighted search field.     |
| **S**           | (When in search fields) Execute the search.      |
| **Arrow Keys**  | Navigate up and down through fields or results.  |
| **F3**          | View the currently selected file in the results. |
| **F10**         | Exit the application.                            |
