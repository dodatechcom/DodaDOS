# Doda Image Viewer

Doda Image is a terminal-based image viewer and slideshow utility. It leverages modern Python libraries (`Pillow`) to read standard image formats (BMP, JPEG, PNG, GIF, WebP) and renders them directly inside the terminal using high-resolution ANSI half-block characters, providing surprisingly detailed graphics in a pure text environment!

## Features

- **ANSI Block Rendering:** Converts pixels to true-color ANSI escape sequences mapped onto Unicode half-blocks, maximizing terminal resolution.
- **File Browser:** Built-in `curses`-based directory navigator to browse for images.
- **Slideshow Mode:** Automatically iterates through all images in the current directory, waiting for a key press between each.

## How to Use

Ensure you have the required dependencies (`Pillow`) installed:
```bash
pip install -r requirements.txt
```

Execute the utility from your terminal to launch the file browser:
```bash
python doda_img.py
```

## Shortcut Keys

| Key             | Action                  |
| --------------- | ----------------------- |
| **Arrow Keys**  | Navigate the directory browser. |
| **ENTER**       | Open a directory or view the selected image. |
| **S**           | Launch a slideshow of all images in the current directory. |
| **Q, ESC**      | Exit the application.   |
