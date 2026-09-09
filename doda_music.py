import curses
import os
import sys
import glob

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame

class MusicPlayerApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_dir = os.getcwd()
        self.audio_files = []
        self.selected_idx = 0
        self.scroll_offset = 0

        self.now_playing = None
        self.is_playing = False

        try:
            pygame.mixer.init()
            self.mixer_initialized = True
        except Exception:
            self.mixer_initialized = False

        self.load_files()

    def load_files(self):
        self.audio_files = ['..']
        extensions = ('*.mp3', '*.wav', '*.ogg', '*.mid', '*.midi', '*.mod')
        found = []
        for ext in extensions:
            found.extend(glob.glob(os.path.join(self.current_dir, ext)))
            found.extend(glob.glob(os.path.join(self.current_dir, ext.upper())))

        dirs = []
        try:
            for d in os.listdir(self.current_dir):
                if os.path.isdir(os.path.join(self.current_dir, d)):
                    dirs.append(d)
        except Exception:
            pass

        dirs.sort()
        found.sort()

        self.audio_files.extend(dirs)
        self.audio_files.extend([os.path.basename(f) for f in found])

        if self.selected_idx >= len(self.audio_files):
            self.selected_idx = max(0, len(self.audio_files) - 1)

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
        header = f" Doda Music Player - {self.current_dir} "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(0, 0, header.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Player Status Box
        self.draw_box(2, 2, 5, width - 4, "Now Playing")
        try:
            if self.now_playing:
                status = "▶ PLAYING" if self.is_playing else "⏸ PAUSED"
                display_name = self.now_playing
                if len(display_name) > width - 8:
                    display_name = "..." + display_name[-(width-11):]
                self.stdscr.addstr(3, 4, display_name)
                self.stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
                self.stdscr.addstr(4, 4, status)
                self.stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            else:
                self.stdscr.addstr(3, 4, "No file loaded.")
                self.stdscr.addstr(4, 4, "■ STOPPED")
        except curses.error:
            pass

        # File List Box
        list_y = 8
        list_h = height - 10
        self.draw_box(list_y, 2, list_h, width - 4, "Audio Files")

        visible_lines = list_h - 2
        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + visible_lines:
            self.scroll_offset = self.selected_idx - visible_lines + 1

        for i in range(visible_lines):
            idx = self.scroll_offset + i
            if idx >= len(self.audio_files):
                break

            filename = self.audio_files[idx]
            is_dir = os.path.isdir(os.path.join(self.current_dir, filename)) or filename == '..'

            display_name = filename
            if is_dir and filename != '..':
                display_name += "/"

            attr = curses.color_pair(2) if is_dir else curses.color_pair(0)

            if idx == self.selected_idx:
                attr = curses.color_pair(4) | curses.A_BOLD

            try:
                self.stdscr.attron(attr)
                self.stdscr.addstr(list_y + 1 + i, 4, display_name.ljust(width - 8)[:width-8])
                self.stdscr.attroff(attr)
            except curses.error:
                pass

        # Footer
        footer = " Arrows: Navigate | ENTER: Play/Open | SPACE: Pause | S: Stop | Q: Quit "
        self.stdscr.attron(curses.color_pair(1))
        try:
            self.stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1))

    def play_file(self, filepath):
        if not self.mixer_initialized:
            return

        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            self.now_playing = os.path.basename(filepath)
            self.is_playing = True
        except Exception:
            pass

    def toggle_pause(self):
        if not self.mixer_initialized or not self.now_playing:
            return

        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True

    def stop_playing(self):
        if not self.mixer_initialized:
            return
        pygame.mixer.music.stop()
        self.now_playing = None
        self.is_playing = False

    def run(self):
        while True:
            self.draw()
            self.stdscr.refresh()

            key = self.stdscr.getch()

            if key == curses.KEY_UP:
                if self.selected_idx > 0:
                    self.selected_idx -= 1
            elif key == curses.KEY_DOWN:
                if self.selected_idx < len(self.audio_files) - 1:
                    self.selected_idx += 1
            elif key == curses.KEY_NPAGE:
                height, _ = self.stdscr.getmaxyx()
                self.selected_idx = min(len(self.audio_files) - 1, self.selected_idx + (height - 13))
            elif key == curses.KEY_PPAGE:
                height, _ = self.stdscr.getmaxyx()
                self.selected_idx = max(0, self.selected_idx - (height - 13))
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                filename = self.audio_files[self.selected_idx]
                path = os.path.join(self.current_dir, filename)

                if os.path.isdir(path) or filename == '..':
                    self.current_dir = os.path.abspath(path)
                    self.selected_idx = 0
                    self.scroll_offset = 0
                    self.load_files()
                else:
                    self.play_file(path)
            elif key == ord(' '):
                self.toggle_pause()
            elif key == ord('s') or key == ord('S'):
                self.stop_playing()
            elif key in (ord('q'), ord('Q'), curses.KEY_F10, 27):
                if self.mixer_initialized:
                    pygame.mixer.quit()
                break

def main(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) # Headers
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK) # Borders / Dirs
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Titles
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN) # Highlight
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK) # Playing Status

    app = MusicPlayerApp(stdscr)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
