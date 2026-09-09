# Doda Edit (Text Editor)

Doda Edit is a full-screen, text-mode file editor inspired by the classic MS-DOS `EDIT.COM`. Built with Python's `curses` library, it allows quick editing of files directly within your terminal.

## Features

- **Full-Screen Editing:** Utilizes your entire terminal for an immersive editing experience.
- **Classic UI:** Features a top header bar and a bottom status bar showing commands, reminiscent of DOS utilities.
- **Keyboard Navigation:** Full support for arrow keys, backspace, delete, and Enter for intuitive text manipulation.

## How to Use

Pass the filename you wish to edit as an argument. If the file doesn't exist, a new one will be created upon saving.

```bash
python doda_edit.py <filename>
```
Example: `python doda_edit.py config.txt`

If no filename is provided, it defaults to `untitled.txt`.

## Shortcut Keys

| Key             | Action                  |
| --------------- | ----------------------- |
| **Arrow Keys**  | Move the cursor.        |
| **F2**          | Save the file.          |
| **F10**         | Exit the editor.        |
