import curses
import os
import sys

class ANSIArtEditor:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = self.stdscr.getmaxyx()

        self.canvas_h = self.height - 2
        self.canvas_w = self.width

        # Grid of (char, color_pair)
        self.canvas = [[(' ', 0) for _ in range(self.canvas_w)] for _ in range(self.canvas_h)]

        self.cursor_y = self.canvas_h // 2
        self.cursor_x = self.canvas_w // 2

        self.current_color = 1 # 1 to 7
        self.brush_char = '█'

    def draw_ui(self):
        self.stdscr.clear()

        # Draw canvas
        for y in range(self.canvas_h):
            for x in range(self.canvas_w):
                char, color = self.canvas[y][x]
                if char != ' ':
                    try:
                        attr = curses.color_pair(color)
                        self.stdscr.attron(attr)
                        self.stdscr.addstr(1 + y, x, char)
                        self.stdscr.attroff(attr)
                    except curses.error:
                        pass

        # Draw Header
        header = f" Doda Draw - ANSI Art Editor | Brush: '{self.brush_char}' | Color: {self.current_color} "
        self.stdscr.attron(curses.color_pair(8) | curses.A_BOLD) # Header color
        try:
            self.stdscr.addstr(0, 0, header.ljust(self.width)[:self.width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(8) | curses.A_BOLD)

        # Draw Footer
        footer = " Arrows: Move | SPACE: Paint | 1-7: Colors | B: Brush | F2: Save | F3: Load | F10: Quit "
        self.stdscr.attron(curses.color_pair(9))
        try:
            self.stdscr.addstr(self.height - 1, 0, footer.center(self.width)[:self.width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(9))

        # Place cursor
        try:
            self.stdscr.move(1 + self.cursor_y, self.cursor_x)
        except curses.error:
            pass

        self.stdscr.refresh()

    def change_brush(self):
        brushes = ['█', '▓', '▒', '░', '#', '*', '+', '-', '.', ' ']
        try:
            idx = brushes.index(self.brush_char)
            self.brush_char = brushes[(idx + 1) % len(brushes)]
        except ValueError:
            self.brush_char = brushes[0]

    def save_file(self):
        curses.echo()
        try:
            curses.curs_set(1)
        except curses.error:
            pass

        prompt = "Save as (filename): "
        self.stdscr.attron(curses.color_pair(9))
        self.stdscr.addstr(self.height - 1, 0, prompt.ljust(self.width)[:self.width-1])
        self.stdscr.attroff(curses.color_pair(9))
        self.stdscr.refresh()

        try:
            filename = self.stdscr.getstr(self.height - 1, len(prompt), 50).decode('utf-8').strip()
            if filename:
                import json
                with open(filename, 'w') as f:
                    json.dump(self.canvas, f)
        except Exception:
            pass

        curses.noecho()

    def load_file(self):
        curses.echo()
        try:
            curses.curs_set(1)
        except curses.error:
            pass

        prompt = "Load file: "
        self.stdscr.attron(curses.color_pair(9))
        self.stdscr.addstr(self.height - 1, 0, prompt.ljust(self.width)[:self.width-1])
        self.stdscr.attroff(curses.color_pair(9))
        self.stdscr.refresh()

        try:
            filename = self.stdscr.getstr(self.height - 1, len(prompt), 50).decode('utf-8').strip()
            if filename and os.path.exists(filename):
                import json
                with open(filename, 'r') as f:
                    data = json.load(f)

                    # Safe load handling terminal size differences
                    for y in range(min(self.canvas_h, len(data))):
                        for x in range(min(self.canvas_w, len(data[y]))):
                            # JSON loading turns tuples into lists, so we map back
                            char, color = data[y][x]
                            self.canvas[y][x] = (char, color)
        except Exception:
            pass

        curses.noecho()

    def run(self):
        while True:
            self.draw_ui()

            key = self.stdscr.getch()

            if key == curses.KEY_UP and self.cursor_y > 0:
                self.cursor_y -= 1
            elif key == curses.KEY_DOWN and self.cursor_y < self.canvas_h - 1:
                self.cursor_y += 1
            elif key == curses.KEY_LEFT and self.cursor_x > 0:
                self.cursor_x -= 1
            elif key == curses.KEY_RIGHT and self.cursor_x < self.canvas_w - 1:
                self.cursor_x += 1
            elif key == ord(' '):
                self.canvas[self.cursor_y][self.cursor_x] = (self.brush_char, self.current_color)
            elif key == curses.KEY_BACKSPACE or key == 8 or key == 127:
                self.canvas[self.cursor_y][self.cursor_x] = (' ', 0)
                if self.cursor_x > 0:
                    self.cursor_x -= 1
            elif ord('1') <= key <= ord('7'):
                self.current_color = key - ord('0')
            elif key == ord('b') or key == ord('B'):
                self.change_brush()
            elif key == curses.KEY_F2:
                self.save_file()
            elif key == curses.KEY_F3:
                self.load_file()
            elif key == curses.KEY_F10:
                break

def main(stdscr):
    try:
        curses.curs_set(1) # Show cursor
    except curses.error:
        pass

    curses.start_color()
    curses.use_default_colors()

    # Setup color palette (1-7 standard ANSI colors)
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_BLUE, -1)
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)
    curses.init_pair(6, curses.COLOR_CYAN, -1)
    curses.init_pair(7, curses.COLOR_WHITE, -1)

    # UI Colors
    curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLUE) # Header
    curses.init_pair(9, curses.COLOR_CYAN, curses.COLOR_BLACK) # Footer

    app = ANSIArtEditor(stdscr)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
