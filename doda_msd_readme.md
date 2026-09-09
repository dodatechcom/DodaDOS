# Doda MSD (System Diagnostics)

Doda MSD is a text-mode system information tool inspired by the classic Microsoft Diagnostics (`MSD.EXE`). It probes the system to display hardware and software information in a retro, colorful terminal interface.

## Features

- **Operating System Info:** Displays OS name, release version, and architecture.
- **Processor Info:** Displays CPU model, physical cores, and logical threads.
- **Memory Info:** Displays total RAM, used RAM, and usage percentage.
- **Disk Info:** Displays total and used disk space on the root partition.
- **Retro UI:** Fully renders in text mode using Python's `curses` library, recreating that classic DOS feel.

## How to Use

Ensure you have the required dependency (`psutil`) installed:
```bash
pip install psutil
```

Launch the utility in your terminal:
```bash
python doda_msd.py
```

*Note: The terminal window must be at least 80x24 characters to display the panels correctly.*

## Shortcut Keys

| Key             | Action                  |
| --------------- | ----------------------- |
| **Q** or **ESC**| Exits the application.  |
