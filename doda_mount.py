import curses
import os
import sys
import subprocess
import json

class MountApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.devices = []
        self.selected_idx = 0
        self.scroll_offset = 0

        self.refresh_devices()

    def refresh_devices(self):
        self.devices = []
        try:
            # We use lsblk -J to output JSON, which is much easier to parse reliably.
            # We want name, size, type, mountpoints, rm (removable)
            result = subprocess.run(['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,MOUNTPOINTS,RM'],
                                    capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            def parse_bd(bd, prefix=""):
                dev_name = prefix + bd.get('name', '')
                size = bd.get('size', '')
                typ = bd.get('type', '')
                mps = bd.get('mountpoints', [])
                mountpoint = mps[0] if mps and mps[0] else ""

                self.devices.append({
                    'name': dev_name,
                    'size': size,
                    'type': typ,
                    'mountpoint': mountpoint,
                    'raw_name': bd.get('name', '')
                })

                if 'children' in bd:
                    for child in bd['children']:
                        parse_bd(child, prefix="  ")

            for bd in data.get('blockdevices', []):
                parse_bd(bd)

        except Exception:
            self.devices.append({
                'name': 'Error retrieving devices',
                'size': '', 'type': '', 'mountpoint': '', 'raw_name': ''
            })

        if self.selected_idx >= len(self.devices):
            self.selected_idx = max(0, len(self.devices) - 1)

    def draw_box(self, y, x, h, w, title):
        color = curses.color_pair(2)
        self.stdscr.attron(color)
        try:
            for i in range(h):
                if i == 0 or i == h - 1:
                    self.stdscr.addstr(y + i, x, "-" * w)
                else:
                    self.stdscr.addstr(y + i, x, "|")
                    self.stdscr.addstr(y + i, x + w - 1, "|")
            self.stdscr.addstr(y, x, "+")
            self.stdscr.addstr(y, x + w - 1, "+")
            self.stdscr.addstr(y + h - 1, x, "+")
            self.stdscr.addstr(y + h - 1, x + w - 1, "+")
        except curses.error:
            pass
        self.stdscr.attroff(color)

        if title:
            self.stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
            try:
                self.stdscr.addstr(y, x + 2, f" {title} ")
            except curses.error:
                pass
            self.stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)

    def draw(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Header
        header = " Doda Mount - Mass Storage Utility "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(0, 0, header.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Main Area
        list_h = height - 4
        self.draw_box(2, 2, list_h, width - 4, "Block Devices")

        # Columns
        cols = f"{'Device':<15} {'Size':<8} {'Type':<8} {'Mountpoint'}"
        self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        try:
            self.stdscr.addstr(3, 4, cols.ljust(width - 8)[:width-8])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

        # List items
        visible_lines = list_h - 3
        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + visible_lines:
            self.scroll_offset = self.selected_idx - visible_lines + 1

        for i in range(visible_lines):
            idx = self.scroll_offset + i
            if idx >= len(self.devices):
                break

            dev = self.devices[idx]
            name = dev.get('name', '')[:15].ljust(15)
            size = dev.get('size', '')[:8].ljust(8)
            typ = dev.get('type', '')[:8].ljust(8)
            mnt = dev.get('mountpoint', '')

            line = f"{name} {size} {typ} {mnt}"

            attr = curses.color_pair(0)
            if idx == self.selected_idx:
                attr = curses.color_pair(4) | curses.A_BOLD

            try:
                self.stdscr.attron(attr)
                self.stdscr.addstr(4 + i, 4, line.ljust(width - 8)[:width-8])
                self.stdscr.attroff(attr)
            except curses.error:
                pass

        # Footer
        footer = " Arrows: Navigate | F5: Mount | F8: Unmount | F10: Quit "
        self.stdscr.attron(curses.color_pair(1))
        try:
            self.stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1))

        self.stdscr.refresh()

    def mount_selected(self):
        if not self.devices:
            return

        dev = self.devices[self.selected_idx]
        raw_name = dev.get('raw_name')
        if not raw_name:
            return

        if dev.get('mountpoint'):
            # Already mounted
            return

        dev_path = f"/dev/{raw_name}"
        target_path = f"/mnt/doda_{raw_name}"

        curses.endwin()
        print(f"\nAttempting to mount {dev_path} to {target_path}...")

        try:
            try:
                os.makedirs(target_path, exist_ok=True)
            except PermissionError:
                subprocess.run(['sudo', 'mkdir', '-p', target_path], check=True)

            # Try to mount. This usually requires sudo.
            result = subprocess.run(['sudo', 'mount', dev_path, target_path], capture_output=True, text=True)
            if result.returncode == 0:
                print("Mount successful!")
            else:
                print(f"Mount failed:\n{result.stderr}")
        except Exception as e:
            print(f"Error: {e}")

        input("\nPress Enter to continue...")
        self.stdscr.clear()
        self.refresh_devices()

    def unmount_selected(self):
        if not self.devices:
            return

        dev = self.devices[self.selected_idx]
        raw_name = dev.get('raw_name')
        mnt = dev.get('mountpoint')

        if not mnt:
            # Not mounted
            return

        dev_path = f"/dev/{raw_name}"

        curses.endwin()
        print(f"\nAttempting to unmount {dev_path} from {mnt}...")

        try:
            result = subprocess.run(['sudo', 'umount', dev_path], capture_output=True, text=True)
            if result.returncode == 0:
                print("Unmount successful!")
            else:
                print(f"Unmount failed:\n{result.stderr}")
        except Exception as e:
            print(f"Error: {e}")

        input("\nPress Enter to continue...")
        self.stdscr.clear()
        self.refresh_devices()

    def run(self):
        while True:
            self.draw()
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key == curses.KEY_UP:
                if self.selected_idx > 0:
                    self.selected_idx -= 1
            elif key == curses.KEY_DOWN:
                if self.selected_idx < len(self.devices) - 1:
                    self.selected_idx += 1
            elif key == curses.KEY_NPAGE:
                height, _ = self.stdscr.getmaxyx()
                self.selected_idx = min(len(self.devices) - 1, self.selected_idx + (height - 7))
            elif key == curses.KEY_PPAGE:
                height, _ = self.stdscr.getmaxyx()
                self.selected_idx = max(0, self.selected_idx - (height - 7))
            elif key == curses.KEY_F5:
                self.mount_selected()
            elif key == curses.KEY_F8:
                self.unmount_selected()
            elif key == curses.KEY_F10:
                break

def main(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) # Header
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK) # Borders
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Titles
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN) # Selection

    app = MountApp(stdscr)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
