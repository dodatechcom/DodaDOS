# Doda Task (Process & Memory Manager)

Doda Task is a text-mode system process monitor built in Python using `curses` and `psutil`. It is inspired by retro memory mappers and modern tools like `htop`, allowing you to monitor system performance and manage processes directly from your terminal.

## Features

- **Live Monitoring:** Auto-refreshes process list and system usage metrics every 2 seconds.
- **Sorting:** Easily sort running processes by CPU usage, Memory usage, PID, or Name.
- **Process Management:** Safely kill unresponsive processes with a built-in confirmation prompt.

## How to Use

Ensure you have the required dependency (`psutil`) installed:
```bash
pip install -r requirements.txt
```

Execute the utility from your terminal:
```bash
python doda_task.py
```

## Shortcut Keys

| Key             | Action                  |
| --------------- | ----------------------- |
| **Arrow Keys**  | Navigate the process list (Up/Down/PageUp/PageDown). |
| **S**           | Cycle sorting mode (CPU, Mem, PID, Name). |
| **F5**          | Manually refresh the process list. |
| **F8 / Del**    | Kill the currently selected process (prompts for confirmation). |
| **F10**         | Exit the application.   |
