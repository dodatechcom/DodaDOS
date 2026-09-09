import curses
import os
import sys
import subprocess
import urllib.request
import textwrap
import html

class NetworkSuiteApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.menu_items = ["1. Ping Utility", "2. Text Web Browser", "3. Exit"]
        self.selected_idx = 0

    def draw_menu(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Header
        header = " Doda Net - TCP/IP Network Suite "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(0, 0, header.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Draw menu box
        box_w = 40
        box_h = 8
        box_y = height // 2 - box_h // 2
        box_x = width // 2 - box_w // 2

        self.stdscr.attron(curses.color_pair(2))
        try:
            for i in range(box_h):
                if i == 0 or i == box_h - 1:
                    self.stdscr.addstr(box_y + i, box_x, "-" * box_w)
                else:
                    self.stdscr.addstr(box_y + i, box_x, "|")
                    self.stdscr.addstr(box_y + i, box_x + box_w - 1, "|")
            self.stdscr.addstr(box_y, box_x, "+")
            self.stdscr.addstr(box_y, box_x + box_w - 1, "+")
            self.stdscr.addstr(box_y + box_h - 1, box_x, "+")
            self.stdscr.addstr(box_y + box_h - 1, box_x + box_w - 1, "+")
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2))

        # Menu Items
        for i, item in enumerate(self.menu_items):
            y = box_y + 2 + i
            x = box_x + 4
            if i == self.selected_idx:
                attr = curses.color_pair(4) | curses.A_BOLD
            else:
                attr = curses.color_pair(0)
            try:
                self.stdscr.attron(attr)
                self.stdscr.addstr(y, x, item.ljust(box_w - 8))
                self.stdscr.attroff(attr)
            except curses.error:
                pass

        # Footer
        footer = " Arrows: Navigate | ENTER: Select "
        self.stdscr.attron(curses.color_pair(2))
        try:
            self.stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2))

        self.stdscr.refresh()

    def tool_ping(self):
        curses.echo()
        try:
            curses.curs_set(1)
        except curses.error:
            pass

        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        self.stdscr.addstr(1, 2, "Enter host/IP to ping:")
        self.stdscr.refresh()

        try:
            host = self.stdscr.getstr(2, 2, 50).decode('utf-8').strip()
        except Exception:
            host = ""

        curses.noecho()
        try:
            curses.curs_set(0)
        except curses.error:
            pass

        if not host:
            return

        curses.endwin()
        print(f"\n--- Pinging {host} ---")
        try:
            # -c 4 for linux, -n 4 for windows
            param = '-n' if sys.platform.lower() == 'win32' else '-c'
            subprocess.run(["ping", param, "4", host])
        except Exception as e:
            print(f"Error executing ping: {e}")

        input("\nPress Enter to return to menu...")
        self.stdscr.clear()

    def strip_html_tags(self, text):
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    def tool_browser(self):
        curses.echo()
        try:
            curses.curs_set(1)
        except curses.error:
            pass

        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        self.stdscr.addstr(1, 2, "Enter URL (e.g. http://example.com):")
        self.stdscr.refresh()

        try:
            url = self.stdscr.getstr(2, 2, 200).decode('utf-8').strip()
        except Exception:
            url = ""

        curses.noecho()
        try:
            curses.curs_set(0)
        except curses.error:
            pass

        if not url:
            return

        if not url.startswith('http'):
            url = 'http://' + url

        self.stdscr.clear()
        self.stdscr.addstr(height//2, width//2 - 5, "Loading...")
        self.stdscr.refresh()

        lines = []
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'DodaNet/1.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                html_bytes = response.read()
                html_str = html_bytes.decode('utf-8', errors='ignore')

                # Very naive HTML to text parsing
                text = html.unescape(self.strip_html_tags(html_str))

                # Split and wrap
                for line in text.splitlines():
                    line = line.strip()
                    if line:
                        wrapped = textwrap.wrap(line, width=width-2)
                        lines.extend(wrapped)

        except Exception as e:
            lines = [f"Error loading {url}:", str(e)]

        if not lines:
            lines = ["(Empty response)"]

        # Viewer loop
        scroll = 0
        while True:
            self.stdscr.clear()

            # Header
            header = f" Doda Browser - {url} "
            self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
            try:
                self.stdscr.addstr(0, 0, header.center(width)[:width-1])
            except curses.error:
                pass
            self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

            for i in range(height - 2):
                if scroll + i < len(lines):
                    try:
                        self.stdscr.addstr(1 + i, 0, lines[scroll + i][:width-1])
                    except curses.error:
                        pass

            # Footer
            footer = " Arrows: Scroll | Q/ESC: Back "
            self.stdscr.attron(curses.color_pair(2))
            try:
                self.stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
            except curses.error:
                pass
            self.stdscr.attroff(curses.color_pair(2))

            self.stdscr.refresh()

            k = self.stdscr.getch()
            if k == curses.KEY_UP and scroll > 0:
                scroll -= 1
            elif k == curses.KEY_DOWN and scroll < len(lines) - (height - 2):
                scroll += 1
            elif k == curses.KEY_NPAGE:
                scroll = min(len(lines) - (height - 2), scroll + height - 2)
                if scroll < 0: scroll = 0
            elif k == curses.KEY_PPAGE:
                scroll = max(0, scroll - (height - 2))
            elif k in (ord('q'), ord('Q'), 27):
                break

    def run(self):
        while True:
            self.draw_menu()
            key = self.stdscr.getch()

            if key == curses.KEY_UP and self.selected_idx > 0:
                self.selected_idx -= 1
            elif key == curses.KEY_DOWN and self.selected_idx < len(self.menu_items) - 1:
                self.selected_idx += 1
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                if self.selected_idx == 0:
                    self.tool_ping()
                elif self.selected_idx == 1:
                    self.tool_browser()
                elif self.selected_idx == 2:
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
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN) # Highlight

    app = NetworkSuiteApp(stdscr)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
