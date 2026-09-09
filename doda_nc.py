import curses
import os
import sys
import subprocess
from doda_nc_logic import copy_item, move_item, delete_item, make_dir

class Panel:
    def __init__(self, window, path):
        self.window = window
        self.path = os.path.abspath(path)
        self.files = []
        self.selected_idx = 0
        self.scroll_offset = 0
        self.is_active = False
        self.marked_files = set()
        self.sort_by = 'name' # can be 'name', 'size', 'date'
        self.refresh_files()

    def cycle_sort(self):
        if self.sort_by == 'name':
            self.sort_by = 'size'
        elif self.sort_by == 'size':
            self.sort_by = 'date'
        else:
            self.sort_by = 'name'
        self.refresh_files()

    def refresh_files(self):
        # Keep track of marked files that still exist
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


        # Sort functions
        def get_size(f):
            try:
                return os.path.getsize(os.path.join(self.path, f))
            except Exception:
                return 0

        def get_mtime(f):
            try:
                return os.path.getmtime(os.path.join(self.path, f))
            except Exception:
                return 0

        if self.sort_by == 'name':
            dirs.sort(key=lambda f: f.lower())
            files.sort(key=lambda f: f.lower())
        elif self.sort_by == 'size':
            dirs.sort(key=get_size, reverse=True)
            files.sort(key=get_size, reverse=True)
        elif self.sort_by == 'date':
            dirs.sort(key=get_mtime, reverse=True)
            files.sort(key=get_mtime, reverse=True)

        self.files.extend(dirs + files)

        # Remove marked files that are no longer in this directory
        self.marked_files = {f for f in self.marked_files if f in self.files}

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

            # Show mark
            mark = "*" if filename in self.marked_files else " "
            display_name = mark + display_name

            if file_idx == self.selected_idx and self.is_active:
                attr = curses.color_pair(4) | curses.A_BOLD
            elif file_idx == self.selected_idx:
                attr = curses.color_pair(5)
            elif filename in self.marked_files:
                attr = curses.color_pair(1) | curses.A_BOLD

            # Formatting details
            details = ""
            if filename != '..':
                try:
                    stat = os.stat(os.path.join(self.path, filename))
                    size_str = f"{stat.st_size}"
                    # Just simple formatting: if size is too long, it's just big
                    if len(size_str) > 8:
                        size_str = f"{stat.st_size // 1048576}M"
                    details = size_str.rjust(8)
                except Exception:
                    details = "        "

            # Combine name and details, then pad/truncate
            avail_name_width = (width - 4) - len(details) - 1
            if avail_name_width > 0:
                if len(display_name) > avail_name_width:
                    display_name = display_name[:avail_name_width - 3] + "..."
                display_name = display_name.ljust(avail_name_width)
                line_str = f"{display_name} {details}"
            else:
                line_str = display_name.ljust(width - 4)

            self.window.attron(attr)
            self.window.addstr(i + 1, 2, line_str[:width-4])
            self.window.attroff(attr)

        self.window.refresh()

def view_file(stdscr, filepath):
    if not os.path.isfile(filepath):
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception:
        # Binary or unreadable file
        return

    stdscr.clear()
    height, width = stdscr.getmaxyx()

    scroll_offset = 0
    while True:
        stdscr.clear()
        # Draw lines
        for i in range(height - 1):
            if scroll_offset + i < len(lines):
                line = lines[scroll_offset + i].rstrip()
                # truncate to width
                line = line[:width-1]
                try:
                    stdscr.addstr(i, 0, line)
                except curses.error:
                    pass

        # Draw bottom bar
        bar = f"--- View: {os.path.basename(filepath)} --- (Press Q or Esc to quit) "
        stdscr.attron(curses.color_pair(6))
        try:
            stdscr.addstr(height - 1, 0, bar.ljust(width)[:width-1])
        except curses.error:
            pass
        stdscr.attroff(curses.color_pair(6))

        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP:
            if scroll_offset > 0:
                scroll_offset -= 1
        elif key == curses.KEY_DOWN:
            if scroll_offset < len(lines) - (height - 1):
                scroll_offset += 1
        elif key == curses.KEY_NPAGE: # Page Down
            scroll_offset = min(len(lines) - (height - 1), scroll_offset + height - 1)
            if scroll_offset < 0: scroll_offset = 0
        elif key == curses.KEY_PPAGE: # Page Up
            scroll_offset = max(0, scroll_offset - (height - 1))
        elif key in (ord('q'), ord('Q'), 27): # 27 is ESC
            break

def draw_bottom_bar(stdscr):
    height, width = stdscr.getmaxyx()
    bar = "F3 View  F4 Edit  F5 Copy  F6 Move  F7 Mkdir  F8 Del  F10 Quit"
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
        elif key == ord(' '):
            # Toggle mark
            filename = active_panel.files[active_panel.selected_idx]
            if filename != '..':
                if filename in active_panel.marked_files:
                    active_panel.marked_files.remove(filename)
                else:
                    active_panel.marked_files.add(filename)
                # Move down after marking like typical NC
                if active_panel.selected_idx < len(active_panel.files) - 1:
                    active_panel.selected_idx += 1
        elif key == ord('\t'):
            active_panel.is_active = False
            inactive_panel.is_active = True

            # Swap active and inactive
            active_panel, inactive_panel = inactive_panel, active_panel
        elif key == ord('s') or key == ord('S'):
            # Cycle sorting
            active_panel.cycle_sort()
        elif key == ord('\n') or key == curses.KEY_ENTER or key == 10 or key == 13:
            # Open directory or execute file
            filename = active_panel.files[active_panel.selected_idx]
            new_path = os.path.join(active_panel.path, filename)
            if os.path.isdir(new_path):
                active_panel.path = os.path.abspath(new_path)
                active_panel.selected_idx = 0
                active_panel.scroll_offset = 0
                active_panel.refresh_files()
            elif os.path.isfile(new_path) and os.access(new_path, os.X_OK):
                # Execute file
                curses.endwin()
                try:
                    subprocess.run([new_path])
                except Exception:
                    pass
                # Wait for user before returning
                input("Press Enter to continue...")
                stdscr.clear()
                active_panel.refresh_files()
                inactive_panel.refresh_files()
        elif key == curses.KEY_F3:
            # View file
            filename = active_panel.files[active_panel.selected_idx]
            if filename != '..':
                filepath = os.path.join(active_panel.path, filename)
                view_file(stdscr, filepath)
                # clear screen for panel redraw after returning
                stdscr.clear()
        elif key == curses.KEY_F4:
            # Edit file
            filename = active_panel.files[active_panel.selected_idx]
            if filename != '..':
                filepath = os.path.join(active_panel.path, filename)
                if os.path.isfile(filepath):
                    editor = os.environ.get('EDITOR', 'nano')
                    # Temporarily leave curses mode
                    curses.endwin()
                    subprocess.run([editor, filepath])
                    # Return to curses mode
                    stdscr.clear()
                    active_panel.refresh_files()
                    inactive_panel.refresh_files()
        elif key == curses.KEY_F5:
            # Copy
            files_to_copy = list(active_panel.marked_files)
            if not files_to_copy:
                filename = active_panel.files[active_panel.selected_idx]
                if filename != '..':
                    files_to_copy = [filename]

            for filename in files_to_copy:
                src = os.path.join(active_panel.path, filename)
                dst = inactive_panel.path
                try:
                    copy_item(src, dst)
                except Exception as e:
                    pass

            active_panel.marked_files.clear()
            inactive_panel.refresh_files()
            active_panel.refresh_files()
        elif key == curses.KEY_F6:
            # Move
            files_to_move = list(active_panel.marked_files)
            if not files_to_move:
                filename = active_panel.files[active_panel.selected_idx]
                if filename != '..':
                    files_to_move = [filename]

            for filename in files_to_move:
                src = os.path.join(active_panel.path, filename)
                dst = os.path.join(inactive_panel.path, filename)
                try:
                    move_item(src, dst)
                except Exception as e:
                    pass

            active_panel.marked_files.clear()
            active_panel.refresh_files()
            inactive_panel.refresh_files()
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
            files_to_delete = list(active_panel.marked_files)
            if not files_to_delete:
                filename = active_panel.files[active_panel.selected_idx]
                if filename != '..':
                    files_to_delete = [filename]

            if not files_to_delete:
                continue

            # Confirmation Dialog
            curses.echo()
            prompt = f"Delete {len(files_to_delete)} item(s)? (y/N): "
            stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
            try:
                stdscr.addstr(height - 2, 0, prompt.ljust(width)[:width-1])
            except curses.error:
                pass
            stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)
            stdscr.refresh()

            try:
                ans = stdscr.getstr(height - 2, len(prompt), 1).decode('utf-8').lower()
            except Exception:
                ans = 'n'

            curses.noecho()
            # Clear prompt line
            try:
                stdscr.addstr(height - 2, 0, (" " * width)[:width-1])
            except curses.error:
                pass
            stdscr.refresh()

            if ans == 'y':
                for filename in files_to_delete:
                    src = os.path.join(active_panel.path, filename)
                    try:
                        delete_item(src)
                    except Exception as e:
                        pass

            active_panel.marked_files.clear()
            active_panel.refresh_files()
            inactive_panel.refresh_files()
        elif key == curses.KEY_F10:
            break

if __name__ == "__main__":
    curses.wrapper(main)
