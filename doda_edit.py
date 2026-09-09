import curses
import sys
import os

class Editor:
    def __init__(self, stdscr, filepath):
        self.stdscr = stdscr
        self.filepath = filepath
        self.lines = []
        self.cursor_y = 0
        self.cursor_x = 0
        self.scroll_y = 0
        self.scroll_x = 0

        self.load_file()

    def load_file(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.lines = f.read().splitlines()
            except Exception:
                self.lines = ["Error loading file."]

        if not self.lines:
            self.lines = [""]

    def save_file(self):
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.lines))
            return True
        except Exception:
            return False

    def draw(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Header
        header = f" Doda Edit - {self.filepath} "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(0, 0, header.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Content
        visible_lines = height - 2
        for i in range(visible_lines):
            line_idx = self.scroll_y + i
            if line_idx < len(self.lines):
                line = self.lines[line_idx]
                visible_line = line[self.scroll_x : self.scroll_x + width - 1]
                try:
                    self.stdscr.addstr(1 + i, 0, visible_line)
                except curses.error:
                    pass

        # Footer
        footer = " F2: Save | F10: Exit "
        self.stdscr.attron(curses.color_pair(2))
        try:
            self.stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2))

        # Cursor
        cy = 1 + self.cursor_y - self.scroll_y
        cx = self.cursor_x - self.scroll_x

        if 1 <= cy < height - 1 and 0 <= cx < width:
            self.stdscr.move(cy, cx)

    def handle_input(self):
        while True:
            self.draw()
            self.stdscr.refresh()

            key = self.stdscr.getch()
            height, width = self.stdscr.getmaxyx()

            if key == curses.KEY_UP:
                if self.cursor_y > 0:
                    self.cursor_y -= 1
                    self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
            elif key == curses.KEY_DOWN:
                if self.cursor_y < len(self.lines) - 1:
                    self.cursor_y += 1
                    self.cursor_x = min(self.cursor_x, len(self.lines[self.cursor_y]))
            elif key == curses.KEY_LEFT:
                if self.cursor_x > 0:
                    self.cursor_x -= 1
                elif self.cursor_y > 0:
                    self.cursor_y -= 1
                    self.cursor_x = len(self.lines[self.cursor_y])
            elif key == curses.KEY_RIGHT:
                if self.cursor_x < len(self.lines[self.cursor_y]):
                    self.cursor_x += 1
                elif self.cursor_y < len(self.lines) - 1:
                    self.cursor_y += 1
                    self.cursor_x = 0
            elif key in (curses.KEY_BACKSPACE, 8, 127):
                if self.cursor_x > 0:
                    line = self.lines[self.cursor_y]
                    self.lines[self.cursor_y] = line[:self.cursor_x-1] + line[self.cursor_x:]
                    self.cursor_x -= 1
                elif self.cursor_y > 0:
                    curr_line = self.lines.pop(self.cursor_y)
                    self.cursor_y -= 1
                    self.cursor_x = len(self.lines[self.cursor_y])
                    self.lines[self.cursor_y] += curr_line
            elif key == curses.KEY_DC: # Delete
                line = self.lines[self.cursor_y]
                if self.cursor_x < len(line):
                    self.lines[self.cursor_y] = line[:self.cursor_x] + line[self.cursor_x+1:]
                elif self.cursor_y < len(self.lines) - 1:
                    next_line = self.lines.pop(self.cursor_y + 1)
                    self.lines[self.cursor_y] += next_line
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                line = self.lines[self.cursor_y]
                self.lines.insert(self.cursor_y + 1, line[self.cursor_x:])
                self.lines[self.cursor_y] = line[:self.cursor_x]
                self.cursor_y += 1
                self.cursor_x = 0
            elif key == curses.KEY_F2:
                # Save
                self.save_file()
            elif key == curses.KEY_F10:
                break
            elif 32 <= key <= 126: # Printable chars
                line = self.lines[self.cursor_y]
                self.lines[self.cursor_y] = line[:self.cursor_x] + chr(key) + line[self.cursor_x:]
                self.cursor_x += 1

            # Scroll adjustments
            if self.cursor_y < self.scroll_y:
                self.scroll_y = self.cursor_y
            elif self.cursor_y >= self.scroll_y + (height - 2):
                self.scroll_y = self.cursor_y - (height - 3)

            if self.cursor_x < self.scroll_x:
                self.scroll_x = self.cursor_x
            elif self.cursor_x >= self.scroll_x + width - 1:
                self.scroll_x = self.cursor_x - width + 2

def main(stdscr, filepath):
    try:
        curses.curs_set(1)
    except curses.error:
        pass

    curses.start_color()
    curses.use_default_colors()

    # MS-DOS edit colors (Blue background, White text)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN) # Menu/header
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN) # Footer
    # the main text area is typically just terminal default if we want to play nice,
    # or we can force blue. We'll stick to default terminal for text area.

    editor = Editor(stdscr, filepath)
    editor.handle_input()

if __name__ == "__main__":
    filepath = "untitled.txt"
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    curses.wrapper(main, filepath)
