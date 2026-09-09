import curses
import os
import sys
import zipfile

class ArchiveManagerApp:
    def __init__(self, stdscr, zip_path):
        self.stdscr = stdscr
        self.zip_path = zip_path
        self.files = []

        self.selected_idx = 0
        self.scroll_offset = 0

        self.load_archive()

    def load_archive(self):
        self.files = []
        if not os.path.exists(self.zip_path):
            self.files = ["Archive not found."]
            return

        if not zipfile.is_zipfile(self.zip_path):
            self.files = ["File is not a valid zip archive."]
            return

        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zf:
                info_list = zf.infolist()
                for info in info_list:
                    size = info.file_size
                    date_time = info.date_time
                    dt_str = f"{date_time[0]}-{date_time[1]:02d}-{date_time[2]:02d}"
                    is_dir = info.is_dir()

                    self.files.append({
                        'name': info.filename,
                        'size': size,
                        'date': dt_str,
                        'is_dir': is_dir,
                        'info_obj': info
                    })
        except Exception:
            self.files = ["Error reading archive."]

        if not self.files:
            self.files = ["Archive is empty."]

    def draw(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Header
        header = f" Doda Zip - {os.path.basename(self.zip_path)} "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(0, 0, header.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Columns
        if self.files and isinstance(self.files[0], dict):
            cols = f"{'Name':<{(width - 24)}} {'Date':<12} {'Size'}"
            self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            try:
                self.stdscr.addstr(1, 0, cols.ljust(width)[:width-1])
            except curses.error:
                pass
            self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

        # File List
        list_h = height - 4
        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + list_h:
            self.scroll_offset = self.selected_idx - list_h + 1

        for i in range(list_h):
            idx = self.scroll_offset + i
            if idx >= len(self.files):
                break

            item = self.files[idx]

            attr = curses.color_pair(0)
            if idx == self.selected_idx:
                attr = curses.color_pair(4) | curses.A_BOLD

            try:
                if isinstance(item, dict):
                    name_w = width - 24
                    name = item['name']
                    if len(name) > name_w:
                        name = "..." + name[-(name_w-3):]
                    else:
                        name = name.ljust(name_w)

                    date = item['date'].ljust(12)
                    size = f"{item['size']}".rjust(10)
                    line = f"{name} {date} {size}"

                    if item['is_dir'] and idx != self.selected_idx:
                        attr = curses.color_pair(2) # Color dirs differently

                else:
                    line = str(item)

                self.stdscr.attron(attr)
                self.stdscr.addstr(2 + i, 0, line.ljust(width)[:width-1])
                self.stdscr.attroff(attr)
            except curses.error:
                pass

        # Footer
        footer = " Arrows: Navigate | F5: Extract File | F10: Quit "
        self.stdscr.attron(curses.color_pair(2))
        try:
            self.stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2))

    def run(self):
        while True:
            self.draw()
            self.stdscr.refresh()

            key = self.stdscr.getch()

            if key == curses.KEY_UP:
                if self.selected_idx > 0:
                    self.selected_idx -= 1
            elif key == curses.KEY_DOWN:
                if self.selected_idx < len(self.files) - 1:
                    self.selected_idx += 1
            elif key == curses.KEY_NPAGE:
                height, _ = self.stdscr.getmaxyx()
                self.selected_idx = min(len(self.files) - 1, self.selected_idx + (height - 4))
            elif key == curses.KEY_PPAGE:
                height, _ = self.stdscr.getmaxyx()
                self.selected_idx = max(0, self.selected_idx - (height - 4))
            elif key == curses.KEY_F5:
                if not self.files or not isinstance(self.files[self.selected_idx], dict):
                    continue

                item = self.files[self.selected_idx]
                info_obj = item['info_obj']

                curses.echo()
                try:
                    curses.curs_set(1)
                except curses.error:
                    pass

                height, width = self.stdscr.getmaxyx()
                prompt = f"Extract '{item['name']}' to: "

                self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                try:
                    self.stdscr.addstr(height - 2, 0, prompt.ljust(width)[:width-1])
                    self.stdscr.addstr(height - 2, len(prompt), "./")
                except curses.error:
                    pass
                self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
                self.stdscr.refresh()

                try:
                    dest_dir = self.stdscr.getstr(height - 2, len(prompt) + 2, width - len(prompt) - 3).decode('utf-8').strip()
                    dest_dir = "./" + dest_dir # Prepend the pre-filled default

                    if dest_dir:
                        os.makedirs(dest_dir, exist_ok=True)
                        with zipfile.ZipFile(self.zip_path, 'r') as zf:
                            zf.extract(info_obj, path=dest_dir)
                except Exception:
                    pass

                curses.noecho()
                try:
                    curses.curs_set(0)
                except curses.error:
                    pass

                try:
                    self.stdscr.addstr(height - 2, 0, (" " * width)[:width-1])
                except curses.error:
                    pass
            elif key == curses.KEY_F10:
                break

def main(stdscr, zip_path):
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)

    app = ArchiveManagerApp(stdscr, zip_path)
    app.run()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python doda_zip.py <archive.zip>")
        sys.exit(1)
    curses.wrapper(main, sys.argv[1])
