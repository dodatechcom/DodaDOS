import curses
import os
import sys
import json
import urllib.request

# Default remote repository url (mock for now, we'll just parse it if available, else load default)
REPO_URL = "https://raw.githubusercontent.com/jules-agent/doda-dos/main/repo.json"

DEFAULT_CATALOG = {
    "packages": [
        {
            "id": "snake",
            "name": "Classic Snake",
            "version": "1.0",
            "desc": "A python text-mode clone of the classic snake game.",
            "url": "https://raw.githubusercontent.com/jules-agent/doda-dos/main/games/snake.py"
        },
        {
            "id": "tetris",
            "name": "Text Tetris",
            "version": "1.1",
            "desc": "Fall blocks, clear lines. Curses based.",
            "url": "https://raw.githubusercontent.com/jules-agent/doda-dos/main/games/tetris.py"
        },
        {
            "id": "calc",
            "name": "Doda Calc",
            "version": "1.0",
            "desc": "Retro programmer's calculator with hex/bin support.",
            "url": "https://raw.githubusercontent.com/jules-agent/doda-dos/main/doda_calc.py"
        }
    ]
}

class PackageManagerApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.packages = []
        self.selected_idx = 0
        self.scroll_offset = 0

        self.fetch_catalog()

    def fetch_catalog(self):
        # In a real app we'd fetch the JSON from REPO_URL
        # For our fallback retro ecosystem, we use the embedded dict
        self.packages = DEFAULT_CATALOG['packages']

    def install_package(self):
        if not self.packages:
            return

        pkg = self.packages[self.selected_idx]
        url = pkg['url']
        filename = os.path.basename(url) or f"{pkg['id']}.py"

        curses.endwin()
        print(f"\n--- Installing {pkg['name']} v{pkg['version']} ---")

        # Try to use doda_fetch if available
        if os.path.exists("doda_fetch.py"):
            import subprocess
            subprocess.run(["python", "doda_fetch.py", url, filename])
        else:
            # Fallback
            print(f"Downloading from {url}...")
            try:
                urllib.request.urlretrieve(url, filename)
                print(f"Successfully installed to {filename}")
            except Exception as e:
                print(f"Installation failed: {e}")

        input("\nPress Enter to return...")
        self.stdscr.clear()

    def draw(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        header = " Doda Get - Package Manager "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(0, 0, header.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Table Header
        self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        try:
            self.stdscr.addstr(1, 0, f"{'Package Name':<20} {'Version':<10} {'Description'}".ljust(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

        # Packages
        visible_lines = height - 4
        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + visible_lines:
            self.scroll_offset = self.selected_idx - visible_lines + 1

        for i in range(visible_lines):
            idx = self.scroll_offset + i
            if idx >= len(self.packages):
                break

            pkg = self.packages[idx]
            name = pkg['name'][:18].ljust(20)
            ver = pkg['version'][:8].ljust(10)
            desc = pkg['desc']

            line = f"{name} {ver} {desc}"

            attr = curses.color_pair(0)
            if idx == self.selected_idx:
                attr = curses.color_pair(4) | curses.A_BOLD

            try:
                self.stdscr.attron(attr)
                self.stdscr.addstr(2 + i, 0, line.ljust(width)[:width-1])
                self.stdscr.attroff(attr)
            except curses.error:
                pass

        footer = " Arrows: Navigate | ENTER: Install Package | Q/F10: Quit "
        self.stdscr.attron(curses.color_pair(2))
        try:
            self.stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2))

        self.stdscr.refresh()

    def run(self):
        while True:
            self.draw()

            key = self.stdscr.getch()
            if key == curses.KEY_UP and self.selected_idx > 0:
                self.selected_idx -= 1
            elif key == curses.KEY_DOWN and self.selected_idx < len(self.packages) - 1:
                self.selected_idx += 1
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                self.install_package()
            elif key in (ord('q'), ord('Q'), curses.KEY_F10, 27):
                break

def main(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)

    app = PackageManagerApp(stdscr)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
