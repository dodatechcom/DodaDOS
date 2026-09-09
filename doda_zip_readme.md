# Doda Zip (Archive Manager)

Doda Zip is a lightweight, text-mode archive manager built in Python. Inspired by classic utilities like PKZIP/PKUNZIP, it allows you to inspect the contents of `.zip` files and extract specific items without needing to extract the entire archive.

## Features

- **Archive Inspection:** View the contents of a `.zip` file in a clean, split-column UI displaying file names, modification dates, and sizes.
- **Selective Extraction:** Highlight any file inside the archive and extract it to a directory of your choosing.

## How to Use

Pass the path to a `.zip` file as an argument when running the utility:

```bash
python doda_zip.py <path_to_archive.zip>
```

*Example:* `python doda_zip.py backup.zip`

## Shortcut Keys

| Key             | Action                  |
| --------------- | ----------------------- |
| **Arrow Keys**  | Navigate the file list inside the archive (Up/Down/PageUp/PageDown). |
| **F5**          | Extract the currently selected file. Prompts for a destination path. |
| **F10**         | Exit the application.   |
