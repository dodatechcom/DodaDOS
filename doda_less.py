import curses
import os
import sys

class MarkdownPager:
    def __init__(self, stdscr, filepath):
        self.stdscr = stdscr
        self.filepath = filepath
        self.scroll_y = 0
        self.lines = []
        self.formatted_lines = []

        self.load_file()

    def load_file(self):
        if not os.path.exists(self.filepath):
            self.lines = [f"File not found: {self.filepath}"]
        else:
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.lines = f.read().splitlines()
            except Exception as e:
                self.lines = [f"Error reading file: {e}"]

        self.format_lines()

    def format_lines(self):
        # Extremely basic tokenizer for bold and lists
        # We represent a line as a list of (text, attr) tuples
        self.formatted_lines = []
        for line in self.lines:
            if line.startswith('#'):
                # Header
                self.formatted_lines.append([(line, curses.color_pair(3) | curses.A_BOLD)])
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                # List item
                self.formatted_lines.append([(line, curses.color_pair(4))])
            elif line.startswith('```') or line.startswith('    '):
                # Code block
                self.formatted_lines.append([(line, curses.color_pair(5))])
            else:
                # Normal line, look for inline **bold** or `code`
                # A full parser is complex; we'll do a simple split by ** and `
                segments = []
                current_text = ""
                i = 0
                is_bold = False
                is_code = False

                while i < len(line):
                    if line[i:i+2] == '**':
                        if current_text:
                            attr = curses.color_pair(6) | curses.A_BOLD if is_bold else (curses.color_pair(5) if is_code else 0)
                            segments.append((current_text, attr))
                            current_text = ""
                        is_bold = not is_bold
                        i += 2
                    elif line[i] == '`':
                        if current_text:
                            attr = curses.color_pair(6) | curses.A_BOLD if is_bold else (curses.color_pair(5) if is_code else 0)
                            segments.append((current_text, attr))
                            current_text = ""
                        is_code = not is_code
                        i += 1
                    else:
                        current_text += line[i]
                        i += 1

                if current_text:
                    attr = curses.color_pair(6) | curses.A_BOLD if is_bold else (curses.color_pair(5) if is_code else 0)
                    segments.append((current_text, attr))

                self.formatted_lines.append(segments)

    def draw(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Header
        header = f" Doda Less - Viewing: {os.path.basename(self.filepath)} "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(0, 0, header.ljust(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Content
        visible_h = height - 2
        for i in range(visible_h):
            idx = self.scroll_y + i
            if idx < len(self.formatted_lines):
                segments = self.formatted_lines[idx]
                x_pos = 0
                for text, attr in segments:
                    # Truncate text if it exceeds width
                    if x_pos >= width - 1:
                        break
                    avail = (width - 1) - x_pos
                    disp_text = text[:avail]
                    try:
                        self.stdscr.attron(attr)
                        self.stdscr.addstr(1 + i, x_pos, disp_text)
                        self.stdscr.attroff(attr)
                    except curses.error:
                        pass
                    x_pos += len(disp_text)

        # Footer
        footer = f" Line {self.scroll_y + 1}/{len(self.formatted_lines)} | Arrows/PgUp/PgDn: Scroll | Q/ESC: Quit "
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
            height, _ = self.stdscr.getmaxyx()
            visible_h = height - 2

            if key == curses.KEY_UP and self.scroll_y > 0:
                self.scroll_y -= 1
            elif key == curses.KEY_DOWN and self.scroll_y < len(self.formatted_lines) - visible_h:
                self.scroll_y += 1
            elif key == curses.KEY_NPAGE:
                self.scroll_y = min(len(self.formatted_lines) - visible_h, self.scroll_y + visible_h)
                if self.scroll_y < 0: self.scroll_y = 0
            elif key == curses.KEY_PPAGE:
                self.scroll_y = max(0, self.scroll_y - visible_h)
            elif key in (ord('q'), ord('Q'), 27):
                break

def main(stdscr, filepath):
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN) # Header
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE) # Footer
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # H1 Header
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK) # Lists
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK) # Code
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Bold

    app = MarkdownPager(stdscr, filepath)
    app.run()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python doda_less.py <file.md>")
        sys.exit(1)
    curses.wrapper(main, sys.argv[1])
