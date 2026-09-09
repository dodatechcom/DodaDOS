# Doda Mount (Mass Storage Utility)

Doda Mount is a text-mode utility for discovering and managing block devices. Inspired by classic disk management tools, it allows users to scan for connected drives (like USB pen drives) and easily mount or unmount them from within a `curses` interface.

## Features

- **Device Discovery:** Automatically scans and lists physical disks and their partitions using `lsblk`.
- **Easy Mounting:** Press a single key to automatically mount a selected partition to a temporary directory (`/mnt/doda_<device>`).
- **Unmounting:** Safely unmount drives before removal.

## How to Use

Execute the utility from your terminal.

*Note: Depending on your system configuration, mounting and unmounting block devices usually requires root privileges. The script will attempt to use `sudo` for these specific actions.*

```bash
python doda_mount.py
```

## Shortcut Keys

| Key             | Action                  |
| --------------- | ----------------------- |
| **Arrow Keys**  | Navigate the list of discovered block devices. |
| **F5**          | Mount the currently selected unmounted partition. |
| **F8**          | Unmount the currently selected mounted partition. |
| **F10**         | Exit the application.   |
