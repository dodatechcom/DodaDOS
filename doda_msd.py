import curses
import os
import platform
import psutil
import textwrap

def draw_box(stdscr, y, x, h, w, title):
    # Draw border
    stdscr.attron(curses.color_pair(2))
    try:
        for i in range(h):
            if i == 0 or i == h - 1:
                stdscr.addstr(y + i, x, "-" * w)
            else:
                stdscr.addstr(y + i, x, "|")
                stdscr.addstr(y + i, x + w - 1, "|")
        # Draw corners
        stdscr.addstr(y, x, "+")
        stdscr.addstr(y, x + w - 1, "+")
        stdscr.addstr(y + h - 1, x, "+")
        stdscr.addstr(y + h - 1, x + w - 1, "+")
    except curses.error:
        pass
    stdscr.attroff(curses.color_pair(2))

    # Title
    if title:
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            stdscr.addstr(y, x + 2, f" {title} ")
        except curses.error:
            pass
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

def format_bytes(b):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if b < 1024.0:
            return f"{b:.2f} {unit}"
        b /= 1024.0
    return f"{b:.2f} PB"

def get_system_info():
    info = {}

    # OS
    info['os_system'] = platform.system()
    info['os_release'] = platform.release()
    info['os_version'] = platform.version()
    info['architecture'] = platform.machine()

    # CPU
    info['cpu'] = platform.processor() or "Unknown CPU"
    info['cpu_cores'] = psutil.cpu_count(logical=False)
    info['cpu_threads'] = psutil.cpu_count(logical=True)

    # Memory
    mem = psutil.virtual_memory()
    info['mem_total'] = format_bytes(mem.total)
    info['mem_used'] = format_bytes(mem.used)
    info['mem_percent'] = mem.percent

    # Disk (root)
    disk = psutil.disk_usage('/')
    info['disk_total'] = format_bytes(disk.total)
    info['disk_used'] = format_bytes(disk.used)
    info['disk_percent'] = disk.percent

    return info

def main(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    info = get_system_info()

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Header
        header = " Doda MSD - Microsoft Diagnostics Clone "
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            stdscr.addstr(0, 0, header.center(width)[:width-1])
        except curses.error:
            pass
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # We need a decent terminal size to draw nicely, e.g. at least 80x24
        if width < 50 or height < 15:
            try:
                stdscr.addstr(2, 2, "Terminal too small to display panels.")
            except curses.error:
                pass
        else:
            # Calculate panel sizes
            panel_w = width // 2 - 2

            # OS Panel
            draw_box(stdscr, 2, 1, 6, panel_w, "Operating System")
            stdscr.addstr(3, 3, f"System:  {info['os_system']}")
            stdscr.addstr(4, 3, f"Release: {info['os_release']}")
            os_ver = textwrap.shorten(info['os_version'], width=panel_w-15, placeholder="...")
            stdscr.addstr(5, 3, f"Version: {os_ver}")
            stdscr.addstr(6, 3, f"Arch:    {info['architecture']}")

            # CPU Panel
            draw_box(stdscr, 2, panel_w + 2, 6, panel_w, "Processor")
            cpu_name = textwrap.shorten(info['cpu'], width=panel_w-12, placeholder="...")
            stdscr.addstr(3, panel_w + 4, f"Name:    {cpu_name}")
            stdscr.addstr(4, panel_w + 4, f"Cores:   {info['cpu_cores']} Physical")
            stdscr.addstr(5, panel_w + 4, f"Threads: {info['cpu_threads']} Logical")

            # Memory Panel
            draw_box(stdscr, 9, 1, 6, panel_w, "Memory")
            stdscr.addstr(10, 3, f"Total:   {info['mem_total']}")
            stdscr.addstr(11, 3, f"Used:    {info['mem_used']}")
            stdscr.addstr(12, 3, f"Percent: {info['mem_percent']}%")

            # Disk Panel
            draw_box(stdscr, 9, panel_w + 2, 6, panel_w, "Disk Space (/)")
            stdscr.addstr(10, panel_w + 4, f"Total:   {info['disk_total']}")
            stdscr.addstr(11, panel_w + 4, f"Used:    {info['disk_used']}")
            stdscr.addstr(12, panel_w + 4, f"Percent: {info['disk_percent']}%")

        # Footer
        footer = " Press Q or ESC to Quit "
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
        except curses.error:
            pass
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord('q'), ord('Q'), 27):
            break

if __name__ == "__main__":
    curses.wrapper(main)
