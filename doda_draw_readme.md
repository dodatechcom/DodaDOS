# Doda Draw (ANSI Art Editor)

Doda Draw is a text-mode drawing program tailored for creating retro ANSI art. Use your keyboard to paint characters on a full-screen canvas, select from classic 16-color ANSI palettes, and save your creations directly to disk.

## Features

- **Free-Form Canvas:** Use the arrow keys to move the cursor freely around the terminal.
- **Paint Mechanics:** Press `SPACE` to stamp the current brush character in the selected color onto the canvas.
- **Dynamic Brushes & Colors:** Cycle through multiple ASCII characters to use as your brush, and instantly switch colors using the number keys (1-7).
- **Save/Load:** Save your artwork to local files and load them up later to continue editing.

## How to Use

Execute the utility from your terminal:

```bash
python doda_draw.py
```

## Shortcut Keys

| Key             | Action                  |
| --------------- | ----------------------- |
| **Arrow Keys**  | Move the cursor around the canvas. |
| **SPACEBAR**    | Paint the current brush character. |
| **BACKSPACE**   | Erase the character at the current position. |
| **1 - 7**       | Select drawing color (Red, Green, Yellow, Blue, Magenta, Cyan, White). |
| **B**           | Cycle through available brush characters (e.g. `█`, `▒`, `#`, `.`). |
| **F2**          | Save the canvas to a file. |
| **F3**          | Load a canvas from a file. |
| **F10**         | Exit the editor. |
