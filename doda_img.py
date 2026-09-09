import curses
import os
import sys
import glob

try:
    from PIL import Image
except ImportError:
    Image = None
import time

def rgb_to_ansi(r, g, b, fg=True):
    prefix = "\033[38;2;" if fg else "\033[48;2;"
    return f"{prefix}{r};{g};{b}m"

def render_image(stdscr, filepath):
    if not Image:
        stdscr.clear()
        stdscr.addstr(2, 2, "Pillow library not installed. Run: pip install Pillow")
        stdscr.refresh()
        stdscr.getch()
        return

    try:
        img = Image.open(filepath)
    except Exception as e:
        stdscr.clear()
        stdscr.addstr(2, 2, f"Error loading image: {e}")
        stdscr.refresh()
        stdscr.getch()
        return

    stdscr.clear()
    stdscr.refresh()

    # We will print directly using ANSI sequences, bypassing curses drawing
    # to get true color blocks if the terminal supports it.
    curses.endwin()

    term_h, term_w = os.get_terminal_size()
    # A character is roughly 2x as tall as it is wide.
    # To use half-block characters (upper half fg, lower half bg),
    # we effectively have 2 pixels per vertical character cell.
    max_w = term_w
    max_h = (term_h - 1) * 2 # Reserve 1 line for footer

    # Calculate aspect ratio preserving resize
    img_w, img_h = img.size
    ratio = min(max_w / img_w, max_h / img_h)
    new_w = int(img_w * ratio)
    new_h = int(img_h * ratio)

    if new_w <= 0 or new_h <= 0:
        return

    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    img = img.convert('RGB')

    pixels = img.load()

    sys.stdout.write('\033[2J\033[H') # Clear screen and go to top-left

    # Draw two rows of pixels per line of text using half-block ▄ (\u2584)
    # Upper half uses BG color, lower half uses FG color.
    # Actually, standard half block \u2580 (▀) upper half is FG, lower is BG.
    for y in range(0, new_h, 2):
        line = ""
        for x in range(new_w):
            r1, g1, b1 = pixels[x, y]
            r2, g2, b2 = (0,0,0)
            if y + 1 < new_h:
                r2, g2, b2 = pixels[x, y + 1]

            # \u2580 (Upper half block)
            # FG = Top pixel, BG = Bottom pixel
            fg = rgb_to_ansi(r1, g1, b1, fg=True)
            bg = rgb_to_ansi(r2, g2, b2, fg=False)
            line += f"{fg}{bg}▀"
        sys.stdout.write(line + "\033[0m\n")

    sys.stdout.write(f"\033[0m\n--- {os.path.basename(filepath)} | Press ENTER to return ---")
    sys.stdout.flush()

    input() # Wait for enter

    # Return to curses
    stdscr.clear()
    stdscr.refresh()

class ImageViewerApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_dir = os.getcwd()
        self.images = []
        self.selected_idx = 0
        self.scroll_offset = 0

        self.load_images()

    def load_images(self):
        self.images = ['..']
        extensions = ('*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.webp')
        found = []
        for ext in extensions:
            found.extend(glob.glob(os.path.join(self.current_dir, ext)))
            found.extend(glob.glob(os.path.join(self.current_dir, ext.upper())))

        # Also list directories so we can navigate
        dirs = []
        try:
            for d in os.listdir(self.current_dir):
                if os.path.isdir(os.path.join(self.current_dir, d)):
                    dirs.append(d)
        except Exception:
            pass

        dirs.sort()
        found.sort()

        self.images.extend(dirs)
        self.images.extend([os.path.basename(f) for f in found])

        if self.selected_idx >= len(self.images):
            self.selected_idx = max(0, len(self.images) - 1)

    def draw(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Header
        header = f" Doda Image Viewer - {self.current_dir} "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(0, 0, header.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # File List
        list_h = height - 2
        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + list_h:
            self.scroll_offset = self.selected_idx - list_h + 1

        for i in range(list_h):
            idx = self.scroll_offset + i
            if idx >= len(self.images):
                break

            filename = self.images[idx]
            is_dir = os.path.isdir(os.path.join(self.current_dir, filename)) or filename == '..'

            display_name = filename
            if is_dir and filename != '..':
                display_name += "/"

            attr = curses.color_pair(2) if is_dir else curses.color_pair(3)

            if idx == self.selected_idx:
                attr = curses.color_pair(4) | curses.A_BOLD

            try:
                self.stdscr.attron(attr)
                self.stdscr.addstr(1 + i, 2, display_name.ljust(width - 4)[:width-4])
                self.stdscr.attroff(attr)
            except curses.error:
                pass

        # Footer
        footer = " Arrows: Navigate | ENTER: View/Open | S: Slideshow | Q: Quit "
        self.stdscr.attron(curses.color_pair(1))
        try:
            self.stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1))

    def slideshow(self):
        # Gather all image files
        image_files = []
        for f in self.images:
            path = os.path.join(self.current_dir, f)
            if os.path.isfile(path) and f != '..':
                image_files.append(path)

        if not image_files:
            return

        for path in image_files:
            render_image(self.stdscr, path)
            # wait for enter is already inside render_image

        # Returning clears back to normal UI

    def run(self):
        while True:
            self.draw()
            self.stdscr.refresh()

            key = self.stdscr.getch()

            if key == curses.KEY_UP:
                if self.selected_idx > 0:
                    self.selected_idx -= 1
            elif key == curses.KEY_DOWN:
                if self.selected_idx < len(self.images) - 1:
                    self.selected_idx += 1
            elif key == curses.KEY_NPAGE:
                height, _ = self.stdscr.getmaxyx()
                self.selected_idx = min(len(self.images) - 1, self.selected_idx + (height - 3))
            elif key == curses.KEY_PPAGE:
                height, _ = self.stdscr.getmaxyx()
                self.selected_idx = max(0, self.selected_idx - (height - 3))
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                filename = self.images[self.selected_idx]
                path = os.path.join(self.current_dir, filename)

                if os.path.isdir(path) or filename == '..':
                    self.current_dir = os.path.abspath(path)
                    self.selected_idx = 0
                    self.scroll_offset = 0
                    self.load_images()
                else:
                    render_image(self.stdscr, path)
            elif key == ord('s') or key == ord('S'):
                self.slideshow()
            elif key in (ord('q'), ord('Q'), curses.KEY_F10, 27):
                break

def main(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) # Headers/Footers
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK) # Directories
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK) # Files
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN) # Selection highlight

    app = ImageViewerApp(stdscr)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
