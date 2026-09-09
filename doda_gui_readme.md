# Doda GUI Shell

Doda GUI is a lightweight, graphical desktop shell for the Doda DOS environment built with Python and Pygame. It mimics the look and feel of early 16-color graphical environments like GEM, Seal, or Windows 3.1, providing an alternative to the standard text-mode utilities.

## Features

- **Retro Aesthetic:** Uses a classic teal desktop background, 3D raised borders, and standard windowing conventions.
- **Window Management:** Supports overlapping, movable windows with active/inactive title bar coloring and close buttons.
- **Mouse Integration:** Fully mouse-driven interface. Double-click icons to launch apps; click and drag title bars to move windows.
- **Built-in Apps:**
  - **About Doda:** A simple dialog box.
  - **SysInfo:** Integrates seamlessly with the `doda_hw` module to present hardware information graphically.
  - **Clock:** A real-time digital clock window.

## How to Use

Ensure you have Pygame installed (it should be in your `requirements.txt` if you have `pygame` from the music player module):
```bash
pip install -r requirements.txt
```

Launch the GUI shell:
```bash
python doda_gui.py
```

## Mouse Controls

| Action            | Result                                     |
| ----------------- | ------------------------------------------ |
| **Single Click**  | Select a desktop icon or bring a window to the front. |
| **Double Click**  | Execute/Launch the selected desktop icon.  |
| **Click & Drag**  | Grab a window's title bar to move it around the screen. |
| **Click 'X'**     | Close the window.                          |
