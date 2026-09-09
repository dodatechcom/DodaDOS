import os
import platform
import psutil
import textwrap
import curses

def get_cpu_info():
    info = {
        'model': platform.processor() or "Unknown",
        'cores': psutil.cpu_count(logical=False),
        'threads': psutil.cpu_count(logical=True),
        'freq_current': 0.0,
        'freq_max': 0.0
    }

    try:
        freq = psutil.cpu_freq()
        if freq:
            info['freq_current'] = freq.current
            info['freq_max'] = freq.max
    except Exception:
        pass

    # On linux, parse /proc/cpuinfo for better details
    if platform.system() == 'Linux':
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line:
                        info['model'] = line.split(':')[1].strip()
                        break
        except Exception:
            pass

    return info

def get_mem_info():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        'total': mem.total,
        'available': mem.available,
        'swap_total': swap.total,
        'swap_used': swap.used
    }

def get_os_info():
    info = {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'node': platform.node()
    }

    # Try to get distribution info on linux
    if platform.system() == 'Linux':
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        info['distro'] = line.split('=')[1].strip().strip('"\'')
                        break
        except Exception:
            info['distro'] = "Linux (Unknown Distro)"
    else:
        info['distro'] = info['system']

    return info

def get_board_info():
    info = {
        'vendor': "Unknown",
        'product': "Unknown",
        'version': "Unknown"
    }
    # DMI data on Linux requires root usually, but we can try
    if platform.system() == 'Linux':
        try:
            with open('/sys/class/dmi/id/board_vendor', 'r') as f:
                info['vendor'] = f.read().strip()
            with open('/sys/class/dmi/id/board_name', 'r') as f:
                info['product'] = f.read().strip()
            with open('/sys/class/dmi/id/board_version', 'r') as f:
                info['version'] = f.read().strip()
        except Exception:
            info['vendor'] = "Access Denied (Requires Root)"
    return info

def format_bytes(b):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if b < 1024.0:
            return f"{b:.2f} {unit}"
        b /= 1024.0
    return f"{b:.2f} PB"

def gather_all_info():
    return {
        'cpu': get_cpu_info(),
        'mem': get_mem_info(),
        'os': get_os_info(),
        'board': get_board_info()
    }

def draw_box(stdscr, y, x, h, w, title):
    color = curses.color_pair(2)
    stdscr.attron(color)
    try:
        for i in range(h):
            if i == 0 or i == h - 1:
                stdscr.addstr(y + i, x, "-" * w)
            else:
                stdscr.addstr(y + i, x, "|")
                stdscr.addstr(y + i, x + w - 1, "|")
        stdscr.addstr(y, x, "+")
        stdscr.addstr(y, x + w - 1, "+")
        stdscr.addstr(y + h - 1, x, "+")
        stdscr.addstr(y + h - 1, x + w - 1, "+")
    except curses.error:
        pass
    stdscr.attroff(color)

    if title:
        stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
        try:
            stdscr.addstr(y, x + 2, f" {title} ")
        except curses.error:
            pass
        stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)

def render_ui(stdscr, info):
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Header
    header = " Doda HW - Hardware Inventory "
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    try:
        stdscr.addstr(0, 0, header.center(width)[:width-1])
    except curses.error:
        pass
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

    if width < 70 or height < 20:
        try:
            stdscr.addstr(2, 2, "Terminal too small to display panels (need 70x20).")
        except curses.error:
            pass
    else:
        panel_w = width // 2 - 2

        # CPU Panel
        draw_box(stdscr, 2, 1, 7, panel_w, "Central Processing Unit")
        cpu = info['cpu']
        model_str = textwrap.shorten(cpu['model'], width=panel_w-13, placeholder="...")
        stdscr.addstr(3, 3, f"Model:   {model_str}")
        stdscr.addstr(4, 3, f"Cores:   {cpu['cores']} (Physical)")
        stdscr.addstr(5, 3, f"Threads: {cpu['threads']} (Logical)")
        stdscr.addstr(6, 3, f"Speed:   {cpu['freq_current']:.1f} MHz (Max {cpu['freq_max']:.1f})")

        # Memory Panel
        draw_box(stdscr, 2, panel_w + 2, 7, panel_w, "System Memory")
        mem = info['mem']
        stdscr.addstr(3, panel_w + 4, f"Total RAM: {format_bytes(mem['total'])}")
        stdscr.addstr(4, panel_w + 4, f"Avail RAM: {format_bytes(mem['available'])}")
        stdscr.addstr(5, panel_w + 4, f"Total SWP: {format_bytes(mem['swap_total'])}")
        stdscr.addstr(6, panel_w + 4, f"Used SWP:  {format_bytes(mem['swap_used'])}")

        # Motherboard Panel
        draw_box(stdscr, 10, 1, 6, panel_w, "Motherboard / BIOS")
        board = info['board']
        ven_str = textwrap.shorten(board['vendor'], width=panel_w-13, placeholder="...")
        prod_str = textwrap.shorten(board['product'], width=panel_w-13, placeholder="...")
        stdscr.addstr(11, 3, f"Vendor:  {ven_str}")
        stdscr.addstr(12, 3, f"Product: {prod_str}")
        stdscr.addstr(13, 3, f"Version: {board['version']}")

        # OS Panel
        draw_box(stdscr, 10, panel_w + 2, 6, panel_w, "Operating System")
        os_info = info['os']
        dist_str = textwrap.shorten(os_info['distro'], width=panel_w-13, placeholder="...")
        rel_str = textwrap.shorten(os_info['release'], width=panel_w-13, placeholder="...")
        stdscr.addstr(11, panel_w + 4, f"Distro:  {dist_str}")
        stdscr.addstr(12, panel_w + 4, f"Kernel:  {rel_str}")
        stdscr.addstr(13, panel_w + 4, f"Arch:    {os_info['machine']}")
        stdscr.addstr(14, panel_w + 4, f"Node:    {os_info['node']}")

    # Footer
    footer = " F10 or Q: Quit "
    stdscr.attron(curses.color_pair(2))
    try:
        stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
    except curses.error:
        pass
    stdscr.attroff(curses.color_pair(2))
    stdscr.refresh()

def main(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) # Header
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK) # Borders
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Titles

    info = gather_all_info()

    while True:
        render_ui(stdscr, info)

        key = stdscr.getch()
        if key in (ord('q'), ord('Q'), curses.KEY_F10, 27):
            break

if __name__ == "__main__":
    curses.wrapper(main)
