import curses
import psutil
import time

class TaskManagerApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.processes = []

        self.selected_idx = 0
        self.scroll_offset = 0
        self.sort_key = 'cpu' # 'pid', 'name', 'cpu', 'mem'

        self.refresh_processes()

    def refresh_processes(self):
        self.processes = []
        for p in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                info = p.info
                self.processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        self.sort_processes()

        if self.selected_idx >= len(self.processes):
            self.selected_idx = max(0, len(self.processes) - 1)

    def sort_processes(self):
        if self.sort_key == 'pid':
            self.processes.sort(key=lambda x: x['pid'])
        elif self.sort_key == 'name':
            self.processes.sort(key=lambda x: (x['name'] or '').lower())
        elif self.sort_key == 'cpu':
            self.processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        elif self.sort_key == 'mem':
            self.processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)

    def draw(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Header
        header = " Doda Task - Process & Memory Manager "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(0, 0, header.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Columns Header
        cols = f"{'PID':<8} {'USER':<12} {'CPU%':<6} {'MEM%':<6} {'NAME'}"
        self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        try:
            self.stdscr.addstr(1, 0, cols.ljust(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

        # Process List
        list_h = height - 4
        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + list_h:
            self.scroll_offset = self.selected_idx - list_h + 1

        for i in range(list_h):
            idx = self.scroll_offset + i
            if idx >= len(self.processes):
                break

            p = self.processes[idx]

            pid = str(p['pid'])
            user = str(p['username'])[:11] if p['username'] else ""
            cpu = f"{p['cpu_percent']:.1f}" if p['cpu_percent'] is not None else "0.0"
            mem = f"{p['memory_percent']:.1f}" if p['memory_percent'] is not None else "0.0"
            name = str(p['name'])

            line = f"{pid:<8} {user:<12} {cpu:<6} {mem:<6} {name}"

            attr = curses.color_pair(0)
            if idx == self.selected_idx:
                attr = curses.color_pair(4) | curses.A_BOLD

            try:
                self.stdscr.attron(attr)
                self.stdscr.addstr(2 + i, 0, line.ljust(width)[:width-1])
                self.stdscr.attroff(attr)
            except curses.error:
                pass

        # Footer
        footer = f" Sort: {self.sort_key.upper()} | F5: Refresh | S: Sort | F8: Kill | F10: Quit "
        self.stdscr.attron(curses.color_pair(2))
        try:
            self.stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2))

    def run(self):
        self.stdscr.nodelay(True)
        last_refresh = time.time()

        while True:
            self.draw()
            self.stdscr.refresh()

            # Auto refresh every 2 seconds
            if time.time() - last_refresh > 2.0:
                self.refresh_processes()
                last_refresh = time.time()

            key = self.stdscr.getch()
            if key == -1:
                time.sleep(0.05)
                continue

            if key == curses.KEY_UP:
                if self.selected_idx > 0:
                    self.selected_idx -= 1
            elif key == curses.KEY_DOWN:
                if self.selected_idx < len(self.processes) - 1:
                    self.selected_idx += 1
            elif key == curses.KEY_NPAGE:
                height, _ = self.stdscr.getmaxyx()
                self.selected_idx = min(len(self.processes) - 1, self.selected_idx + (height - 4))
            elif key == curses.KEY_PPAGE:
                height, _ = self.stdscr.getmaxyx()
                self.selected_idx = max(0, self.selected_idx - (height - 4))
            elif key == ord('s') or key == ord('S'):
                keys = ['cpu', 'mem', 'pid', 'name']
                curr_idx = keys.index(self.sort_key)
                self.sort_key = keys[(curr_idx + 1) % len(keys)]
                self.refresh_processes()
            elif key == curses.KEY_F5:
                self.refresh_processes()
                last_refresh = time.time()
            elif key == curses.KEY_F8 or key == curses.KEY_DC:
                if not self.processes:
                    continue
                p_info = self.processes[self.selected_idx]
                pid = p_info['pid']
                name = p_info['name']

                # Switch to blocking mode for input
                self.stdscr.nodelay(False)
                curses.echo()

                height, width = self.stdscr.getmaxyx()
                prompt = f"Kill Process {pid} ({name})? (y/N): "

                self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                try:
                    self.stdscr.addstr(height - 2, 0, prompt.ljust(width)[:width-1])
                except curses.error:
                    pass
                self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
                self.stdscr.refresh()

                try:
                    ans = self.stdscr.getstr(height - 2, len(prompt), 1).decode('utf-8').lower()
                    if ans == 'y':
                        p = psutil.Process(pid)
                        p.terminate()
                except Exception:
                    pass

                curses.noecho()
                self.stdscr.nodelay(True)

                # Clear prompt line
                try:
                    self.stdscr.addstr(height - 2, 0, (" " * width)[:width-1])
                except curses.error:
                    pass

                self.refresh_processes()
                last_refresh = time.time()
            elif key == curses.KEY_F10:
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

    app = TaskManagerApp(stdscr)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
