# Doda DOS

Welcome to **Doda DOS**! This repository is a collection of classic, retro MS-DOS style utilities and tools designed to run natively in modern terminal environments (and occasionally GUI windows). Whether you are a retro enthusiast, looking to build an embedded system dashboard, or just miss the days of blue terminal screens and function-key navigation, Doda DOS has something for you.

## 🛠️ The Utilities

Doda DOS is comprised of numerous standalone modules, each mimicking classic software while leveraging modern Python libraries under the hood.

### Text-Mode Utilities (`curses`)

*   **[Doda NC (Norton Commander)](doda_nc_readme.md)**: A classic dual-pane file manager for high-speed file manipulation.
*   **[Doda Edit (Text Editor)](doda_edit_readme.md)**: A full-screen text editor inspired by the classic `EDIT.COM`.
*   **[Doda Find (File Finder)](doda_find_readme.md)**: A fast, interactive file search and viewing utility.
*   **[Doda Tree (Visual Tree)](doda_tree_readme.md)**: An ANSI-colored visual directory tree mapper.
*   **[Doda Mount (Mass Storage)](doda_mount_readme.md)**: A quick mounting/unmounting tool for USB drives and partitions.
*   **[Doda HW (Hardware Inventory)](doda_hw_readme.md)**: A SiSoftware Sandra style hardware diagnostic tool.
*   **[Doda Task (Process Manager)](doda_task_readme.md)**: A process and memory manager for monitoring and killing tasks.
*   **[Doda Net (Network Suite)](doda_net_readme.md)**: A bundled networking suite featuring Ping and a text-mode web browser.
*   **[Doda Zip (Archive Manager)](doda_zip_readme.md)**: Inspect and extract contents from `.zip` archives.
*   **[Doda Image Viewer](doda_img_readme.md)**: A terminal-based ANSI pixel image viewer and slideshow tool.
*   **[Doda Music Player](doda_music_readme.md)**: A background terminal audio player.
*   **[Doda Draw (ANSI Art Editor)](doda_draw_readme.md)**: A text-mode paint application for creating ANSI art.
*   **[Doda Cal (Calendar PIM)](doda_cal_readme.md)**: A retro monthly calendar and note-taking utility.
*   **[Doda Serial (Lab Instrument Control)](doda_serial_readme.md)**: An asynchronous serial terminal to interface with hardware.

### Graphical Utilities (`pygame`)

*   **[Doda GUI Shell](doda_gui_readme.md)**: A retro 16-color graphical desktop environment (like GEM/Windows 3.1) featuring movable windows, icons, and built-in apps.

### Experimental

*   **[UEFI DOS Loader Exploration](uefi_loader_readme.md)**: A C-based exploration into booting native real-mode DOS on modern UEFI firmware.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/doda-dos.git
   cd doda-dos
   ```

2. **Install requirements:**
   Some utilities require modern Python libraries (like `psutil`, `pygame`, `Pillow`, `pyserial`).
   ```bash
   pip install -r requirements.txt
   ```

3. **Run a utility:**
   Simply execute the Python script of your choice in a terminal:
   ```bash
   python doda_nc.py
   ```
   *(Note: For the best experience, ensure your terminal supports colors and is resized to at least 80x24 characters).*
