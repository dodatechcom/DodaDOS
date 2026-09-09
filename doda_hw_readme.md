# Doda HW (Hardware Inventory Tool)

Doda HW is a text-mode hardware and system inventory utility for Python. Inspired by classic diagnostic tools like SiSoftware Sandra, it probes your system and displays crucial specifications in a retro, multi-panel interface.

## Features

- **CPU Info:** Displays processor model, physical cores, logical threads, and current/max clock speeds.
- **Memory Info:** Displays total and available RAM alongside Swap usage.
- **Motherboard/BIOS:** Displays DMI information including vendor, product name, and version (requires root privileges on Linux for full output).
- **OS Info:** Displays the operating system distribution, kernel release, architecture, and network node name.

## How to Use

Ensure you have the required dependencies (`psutil`) installed:
```bash
pip install -r requirements.txt
```

Execute the utility from your terminal. For full motherboard details on Linux systems, running with `sudo` may be required:
```bash
python doda_hw.py
```

## Shortcut Keys

| Key             | Action                  |
| --------------- | ----------------------- |
| **Q, ESC, F10** | Exits the application.  |
