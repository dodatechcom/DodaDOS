import curses
import os
import sys
from doda_nc_logic import copy_item, move_item, delete_item, make_dir

class Panel:
    def __init__(self, window, path):
        self.window = window
        self.path = os.path.abspath(path)
        self.files = []
        self.selected_idx = 0
        self.scroll_offset = 0
        self.is_active = False
        self.refresh_files()

    def refresh_files(self):
        try:
            entries = os.listdir(self.path)
        except PermissionError:
            entries = []

        self.files = ['..']
        dirs = []
        files = []
        for e in entries:
            try:
                if os.path.isdir(os.path.join(self.path, e)):
                    dirs.append(e)
                else:
                    files.append(e)
            except Exception:
                files.append(e)

        dirs.sort()
        files.sort()
        self.files.extend(dirs + files)

        # Keep selected index in bounds
        if self.selected_idx >= len(self.files):
            self.selected_idx = max(0, len(self.files) - 1)

    def draw(self):
        self.window.clear()
        height, width = self.window.getmaxyx()

        # Draw border
        self.window.box()

        # Title (path)
        title = f" {self.path} "
        if len(title) > width - 2:
            title = " ..." + title[-(width-6):]

        if self.is_active:
            self.window.attron(curses.color_pair(1) | curses.A_BOLD)
            self.window.addstr(0, 2, title)
            self.window.attroff(curses.color_pair(1) | curses.A_BOLD)
        else:
            self.window.addstr(0, 2, title)

        # Draw files
        visible_lines = height - 2

        # Adjust scroll offset
        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + visible_lines:
            self.scroll_offset = self.selected_idx - visible_lines + 1

        for i in range(visible_lines):
            file_idx = self.scroll_offset + i
            if file_idx >= len(self.files):
                break

            filename = self.files[file_idx]
            is_dir = os.path.isdir(os.path.join(self.path, filename))

            display_name = filename
            if len(display_name) > width - 4:
                display_name = display_name[:width-7] + "..."

            # Add trailing slash for directories
            if is_dir and filename != '..':
                display_name += "/"

            attr = curses.color_pair(2) if is_dir else curses.color_pair(3)

            if file_idx == self.selected_idx and self.is_active:
                attr = curses.color_pair(4) | curses.A_BOLD
            elif file_idx == self.selected_idx:
                attr = curses.color_pair(5)

            # Pad with spaces
            display_name = display_name.ljust(width - 4)

            self.window.attron(attr)
            self.window.addstr(i + 1, 2, display_name)
            self.window.attroff(attr)

        self.window.refresh()

def draw_bottom_bar(stdscr):
    height, width = stdscr.getmaxyx()
    bar = "F5 Copy  F6 Move  F7 Mkdir  F8 Del  F10 Quit"
    stdscr.attron(curses.color_pair(6))
    try:
        stdscr.addstr(height - 1, 0, bar.center(width)[:width-1])
    except curses.error:
        pass
    stdscr.attroff(curses.color_pair(6))
    stdscr.refresh()

def main(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.start_color()
    curses.use_default_colors()

    # Colors
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLUE) # Active title
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Directories
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK) # Files
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Selected active
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE) # Selected inactive
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE) # Bottom bar

    height, width = stdscr.getmaxyx()
    half_width = width // 2

    left_win = curses.newwin(height - 1, half_width, 0, 0)
    right_win = curses.newwin(height - 1, width - half_width, 0, half_width)

    left_panel = Panel(left_win, os.getcwd())
    right_panel = Panel(right_win, os.getcwd())

    left_panel.is_active = True

    active_panel = left_panel
    inactive_panel = right_panel

    while True:
        left_panel.draw()
        right_panel.draw()
        draw_bottom_bar(stdscr)

        key = stdscr.getch()

        if key == curses.KEY_UP:
            if active_panel.selected_idx > 0:
                active_panel.selected_idx -= 1
        elif key == curses.KEY_DOWN:
            if active_panel.selected_idx < len(active_panel.files) - 1:
                active_panel.selected_idx += 1
        elif key == ord('\t'):
            active_panel.is_active = False
            inactive_panel.is_active = True

            # Swap active and inactive
            active_panel, inactive_panel = inactive_panel, active_panel
        elif key == ord('\n') or key == curses.KEY_ENTER or key == 10 or key == 13:
            # Open directory
            filename = active_panel.files[active_panel.selected_idx]
            new_path = os.path.join(active_panel.path, filename)
            if os.path.isdir(new_path):
                active_panel.path = os.path.abspath(new_path)
                active_panel.selected_idx = 0
                active_panel.scroll_offset = 0
                active_panel.refresh_files()
        elif key == curses.KEY_F5:
            # Copy
            filename = active_panel.files[active_panel.selected_idx]
            if filename != '..':
                src = os.path.join(active_panel.path, filename)
                dst = inactive_panel.path
                try:
                    copy_item(src, dst)
                    inactive_panel.refresh_files()
                except Exception as e:
                    pass
        elif key == curses.KEY_F6:
            # Move
            filename = active_panel.files[active_panel.selected_idx]
            if filename != '..':
                src = os.path.join(active_panel.path, filename)
                dst = os.path.join(inactive_panel.path, filename)
                try:
                    move_item(src, dst)
                    active_panel.refresh_files()
                    inactive_panel.refresh_files()
                except Exception as e:
                    pass
        elif key == curses.KEY_F7:
            # Mkdir
            curses.echo()
            try:
                curses.curs_set(1)
            except curses.error:
                pass

            # Draw prompt at bottom
            prompt = "New directory name: "
            stdscr.attron(curses.color_pair(6))
            try:
                stdscr.addstr(height - 2, 0, prompt.ljust(width)[:width-1])
            except curses.error:
                pass
            stdscr.attroff(curses.color_pair(6))
            stdscr.refresh()

            # Read input
            try:
                # read up to width - len(prompt) - 1 chars
                name_bytes = stdscr.getstr(height - 2, len(prompt), width - len(prompt) - 1)
                new_folder_name = name_bytes.decode('utf-8').strip()
                if new_folder_name:
                    new_dir = os.path.join(active_panel.path, new_folder_name)
                    make_dir(new_dir)
                    active_panel.refresh_files()
            except Exception as e:
                pass

            curses.noecho()
            try:
                curses.curs_set(0)
            except curses.error:
                pass
            # Clear prompt line
            try:
                stdscr.addstr(height - 2, 0, (" " * width)[:width-1])
            except curses.error:
                pass
            stdscr.refresh()
        elif key == curses.KEY_F8:
            # Delete
            filename = active_panel.files[active_panel.selected_idx]
            if filename != '..':
                src = os.path.join(active_panel.path, filename)
                try:
                    delete_item(src)
                    active_panel.refresh_files()
                except Exception as e:
                    pass
        elif key == curses.KEY_F10:
            break

if __name__ == "__main__":
    curses.wrapper(main)
