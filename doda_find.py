import curses
import os
import sys
import fnmatch
import textwrap

def view_file(stdscr, filepath):
    if not os.path.isfile(filepath):
        return

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception:
        return

    stdscr.clear()
    height, width = stdscr.getmaxyx()

    scroll_offset = 0
    while True:
        stdscr.clear()
        for i in range(height - 1):
            if scroll_offset + i < len(lines):
                line = lines[scroll_offset + i].rstrip()
                line = line[:width-1]
                try:
                    stdscr.addstr(i, 0, line)
                except curses.error:
                    pass

        bar = f"--- View: {os.path.basename(filepath)} --- (Press Q or Esc to quit) "
        stdscr.attron(curses.color_pair(2))
        try:
            stdscr.addstr(height - 1, 0, bar.ljust(width)[:width-1])
        except curses.error:
            pass
        stdscr.attroff(curses.color_pair(2))

        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP:
            if scroll_offset > 0: scroll_offset -= 1
        elif key == curses.KEY_DOWN:
            if scroll_offset < len(lines) - (height - 1): scroll_offset += 1
        elif key == curses.KEY_NPAGE:
            scroll_offset = min(len(lines) - (height - 1), scroll_offset + height - 1)
            if scroll_offset < 0: scroll_offset = 0
        elif key == curses.KEY_PPAGE:
            scroll_offset = max(0, scroll_offset - (height - 1))
        elif key in (ord('q'), ord('Q'), 27):
            break

class FileFinderApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr

        # Initial search params
        self.search_dir = os.getcwd()
        self.file_mask = "*.*"
        self.containing_text = ""

        # State
        self.active_field = 0 # 0: dir, 1: mask, 2: text, 3: results
        self.results = []
        self.selected_result_idx = 0
        self.scroll_offset = 0
        self.is_searching = False

    def draw_box(self, y, x, h, w, title, active=False):
        color = curses.color_pair(4) if active else curses.color_pair(2)
        self.stdscr.attron(color)
        try:
            for i in range(h):
                if i == 0 or i == h - 1:
                    self.stdscr.addstr(y + i, x, "-" * w)
                else:
                    self.stdscr.addstr(y + i, x, "|")
                    self.stdscr.addstr(y + i, x + w - 1, "|")
            # Draw corners
            self.stdscr.addstr(y, x, "+")
            self.stdscr.addstr(y, x + w - 1, "+")
            self.stdscr.addstr(y + h - 1, x, "+")
            self.stdscr.addstr(y + h - 1, x + w - 1, "+")
        except curses.error:
            pass
        self.stdscr.attroff(color)

        if title:
            title_color = curses.color_pair(1) | curses.A_BOLD if active else curses.color_pair(3) | curses.A_BOLD
            self.stdscr.attron(title_color)
            try:
                self.stdscr.addstr(y, x + 2, f" {title} ")
            except curses.error:
                pass
            self.stdscr.attroff(title_color)

    def draw(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Header
        header = " Doda Find - File Search Utility "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(0, 0, header.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Search Panel Box
        self.draw_box(2, 2, 8, width - 4, "Search Criteria")

        # Fields
        try:
            # Dir
            self.stdscr.addstr(3, 4, "Directory:")
            attr = curses.color_pair(5) if self.active_field == 0 else curses.color_pair(0)
            self.stdscr.attron(attr)
            self.stdscr.addstr(3, 17, self.search_dir.ljust(width - 22)[:width-22])
            self.stdscr.attroff(attr)

            # Mask
            self.stdscr.addstr(5, 4, "File Mask:")
            attr = curses.color_pair(5) if self.active_field == 1 else curses.color_pair(0)
            self.stdscr.attron(attr)
            self.stdscr.addstr(5, 17, self.file_mask.ljust(width - 22)[:width-22])
            self.stdscr.attroff(attr)

            # Text
            self.stdscr.addstr(7, 4, "Text:")
            attr = curses.color_pair(5) if self.active_field == 2 else curses.color_pair(0)
            self.stdscr.attron(attr)
            self.stdscr.addstr(7, 17, self.containing_text.ljust(width - 22)[:width-22])
            self.stdscr.attroff(attr)
        except curses.error:
            pass

        # Results Box
        res_h = height - 13
        if res_h > 2:
            self.draw_box(11, 2, res_h, width - 4, f"Results ({len(self.results)})", active=(self.active_field == 3))

            visible_lines = res_h - 2

            if self.selected_result_idx < self.scroll_offset:
                self.scroll_offset = self.selected_result_idx
            elif self.selected_result_idx >= self.scroll_offset + visible_lines:
                self.scroll_offset = self.selected_result_idx - visible_lines + 1

            for i in range(visible_lines):
                idx = self.scroll_offset + i
                if idx >= len(self.results):
                    break

                filepath = self.results[idx]
                disp_path = filepath
                if len(disp_path) > width - 8:
                    disp_path = "..." + disp_path[-(width-11):]

                attr = curses.color_pair(0)
                if idx == self.selected_result_idx and self.active_field == 3:
                    attr = curses.color_pair(4) | curses.A_BOLD
                elif idx == self.selected_result_idx:
                    attr = curses.color_pair(5)

                try:
                    self.stdscr.attron(attr)
                    self.stdscr.addstr(12 + i, 4, disp_path.ljust(width - 8))
                    self.stdscr.attroff(attr)
                except curses.error:
                    pass

        # Footer
        footer = " TAB: Next Field | ENTER: Search | F3: View | F10: Quit "
        self.stdscr.attron(curses.color_pair(2))
        try:
            self.stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2))

    def do_search(self):
        self.results = []
        self.selected_result_idx = 0
        self.scroll_offset = 0

        # Show searching message
        height, width = self.stdscr.getmaxyx()
        msg = " Searching... "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(height // 2, (width - len(msg)) // 2, msg)
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.refresh()

        try:
            for root, dirs, files in os.walk(self.search_dir):
                for filename in files:
                    if fnmatch.fnmatch(filename, self.file_mask):
                        filepath = os.path.join(root, filename)

                        # Check containing text if specified
                        if self.containing_text:
                            try:
                                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    if self.containing_text.lower() in content.lower():
                                        self.results.append(filepath)
                            except Exception:
                                pass
                        else:
                            self.results.append(filepath)
        except Exception:
            pass

        if self.results:
            self.active_field = 3 # jump to results

    def edit_field(self, field_idx):
        curses.echo()
        try:
            curses.curs_set(1)
        except curses.error:
            pass

        height, width = self.stdscr.getmaxyx()

        # Determine current text
        if field_idx == 0:
            current = self.search_dir
            y, x = 3, 17
        elif field_idx == 1:
            current = self.file_mask
            y, x = 5, 17
        elif field_idx == 2:
            current = self.containing_text
            y, x = 7, 17

        # Draw prompt for new value at bottom to avoid inline curses editing quirks
        prompt = "New value (leave empty to keep current): "
        self.stdscr.attron(curses.color_pair(2))
        try:
            self.stdscr.addstr(height - 2, 0, prompt.ljust(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2))
        self.stdscr.refresh()

        try:
            val = self.stdscr.getstr(height - 2, len(prompt), width - len(prompt) - 1).decode('utf-8').strip()
            if val:
                if field_idx == 0:
                    self.search_dir = val
                elif field_idx == 1:
                    self.file_mask = val
                elif field_idx == 2:
                    self.containing_text = val
        except Exception:
            pass

        curses.noecho()
        try:
            curses.curs_set(0)
        except curses.error:
            pass

    def run(self):
        while True:
            self.draw()
            self.stdscr.refresh()

            key = self.stdscr.getch()

            if key == ord('\t'):
                self.active_field = (self.active_field + 1) % 4
                if self.active_field == 3 and not self.results:
                    self.active_field = 0
            elif key == curses.KEY_UP:
                if self.active_field == 3 and self.selected_result_idx > 0:
                    self.selected_result_idx -= 1
                elif self.active_field > 0 and self.active_field < 3:
                    self.active_field -= 1
            elif key == curses.KEY_DOWN:
                if self.active_field == 3 and self.selected_result_idx < len(self.results) - 1:
                    self.selected_result_idx += 1
                elif self.active_field < 2:
                    self.active_field += 1
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                if self.active_field < 3:
                    self.edit_field(self.active_field)
            elif key == ord('s') or key == ord('S'):
                # Quick search shortcut if not in results
                if self.active_field < 3:
                    self.do_search()
            elif key == curses.KEY_F3:
                # View file
                if self.active_field == 3 and self.results:
                    filepath = self.results[self.selected_result_idx]
                    view_file(self.stdscr, filepath)
            elif key == curses.KEY_F10:
                break

def main(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.start_color()
    curses.use_default_colors()

    # Colors
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) # Header
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK) # Borders
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Titles inactive
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN) # Active / Highlight
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE) # Selected inactive

    app = FileFinderApp(stdscr)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
