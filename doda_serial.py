import curses
import sys
import threading
import time

import serial

class SerialTerminalApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.port = "/dev/ttyUSB0"
        self.baudrate = 9600
        self.is_connected = False

        self.output_buffer = []
        self.input_buffer = ""

        self.scroll_offset = 0
        self.serial_conn = None
        self.read_thread = None
        self.stop_event = threading.Event()

    def append_output(self, text):
        lines = text.replace('\r', '').split('\n')
        for line in lines:
            if line:
                self.output_buffer.append(line)
        # Keep buffer manageable
        if len(self.output_buffer) > 1000:
            self.output_buffer = self.output_buffer[-1000:]

        # Draw immediately if possible, but safely
        # Note: curses from a different thread can be risky,
        # so we rely on the main loop's timeout to refresh.

    def serial_read_loop(self):
        while not self.stop_event.is_set():
            if self.serial_conn and self.serial_conn.is_open:
                try:
                    if self.serial_conn.in_waiting > 0:
                        data = self.serial_conn.read(self.serial_conn.in_waiting)
                        try:
                            text = data.decode('utf-8', errors='replace')
                            self.append_output(f"RX: {text.strip()}")
                        except Exception:
                            pass
                except Exception:
                    self.is_connected = False
                    self.append_output("Connection lost.")
                    break
            time.sleep(0.05)

    def toggle_connection(self):
        if self.is_connected:
            self.stop_event.set()
            if self.read_thread:
                self.read_thread.join()
            if self.serial_conn:
                self.serial_conn.close()
            self.is_connected = False
            self.append_output("Disconnected.")
        else:
            try:
                self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
                self.is_connected = True
                self.stop_event.clear()
                self.read_thread = threading.Thread(target=self.serial_read_loop, daemon=True)
                self.read_thread.start()
                self.append_output(f"Connected to {self.port} at {self.baudrate} baud.")
            except Exception as e:
                self.append_output(f"Failed to connect: {e}")

    def change_settings(self):
        curses.echo()
        try:
            curses.curs_set(1)
        except curses.error:
            pass

        height, width = self.stdscr.getmaxyx()

        # Port
        prompt = f"Enter Port (current {self.port}): "
        self.stdscr.attron(curses.color_pair(2))
        try:
            self.stdscr.addstr(height - 2, 0, prompt.ljust(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2))
        self.stdscr.refresh()

        try:
            new_port = self.stdscr.getstr(height - 2, len(prompt), 50).decode('utf-8').strip()
            if new_port:
                self.port = new_port
        except Exception:
            pass

        # Baudrate
        prompt = f"Enter Baudrate (current {self.baudrate}): "
        self.stdscr.attron(curses.color_pair(2))
        try:
            self.stdscr.addstr(height - 2, 0, prompt.ljust(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2))
        self.stdscr.refresh()

        try:
            new_baud = self.stdscr.getstr(height - 2, len(prompt), 50).decode('utf-8').strip()
            if new_baud:
                self.baudrate = int(new_baud)
        except Exception:
            pass

        curses.noecho()
        try:
            curses.curs_set(0)
        except curses.error:
            pass

    def send_data(self):
        if not self.input_buffer:
            return

        if self.is_connected and self.serial_conn:
            try:
                # Add carriage return and newline for standard instrument commands
                data = (self.input_buffer + '\r\n').encode('utf-8')
                self.serial_conn.write(data)
                self.append_output(f"TX: {self.input_buffer}")
            except Exception as e:
                self.append_output(f"Failed to send: {e}")
        else:
            self.append_output("Cannot send: Not connected.")

        self.input_buffer = ""

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
        header = " Doda Serial - Lab Instrument Control "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(0, 0, header.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Connection Status
        status_text = f" Port: {self.port} | Baud: {self.baudrate} | Status: "
        if self.is_connected:
            status_text += "CONNECTED "
            status_color = curses.color_pair(5) | curses.A_BOLD # Green
        else:
            status_text += "DISCONNECTED "
            status_color = curses.color_pair(6) | curses.A_BOLD # Red

        self.stdscr.attron(status_color)
        try:
            self.stdscr.addstr(1, 0, status_text.ljust(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(status_color)

        # Output Box
        out_h = height - 5
        self.draw_box(2, 0, out_h, width, "Terminal Output")

        visible_lines = out_h - 2
        start_idx = max(0, len(self.output_buffer) - visible_lines - self.scroll_offset)

        for i in range(min(visible_lines, len(self.output_buffer) - start_idx)):
            try:
                self.stdscr.addstr(3 + i, 2, self.output_buffer[start_idx + i][:width-4])
            except curses.error:
                pass

        # Input Bar
        self.stdscr.attron(curses.color_pair(2))
        try:
            self.stdscr.addstr(height - 2, 0, " > " + self.input_buffer.ljust(width - 4)[:width-4])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2))

        # Footer
        footer = " F2: Connect/Disconnect | F3: Settings | F10: Quit "
        self.stdscr.attron(curses.color_pair(1))
        try:
            self.stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1))

        self.stdscr.refresh()

    def run(self):
        self.stdscr.nodelay(True)
        while True:
            self.draw()

            key = self.stdscr.getch()
            if key == -1:
                time.sleep(0.05)
                continue

            if key == curses.KEY_UP:
                if self.scroll_offset < len(self.output_buffer) - 1:
                    self.scroll_offset += 1
            elif key == curses.KEY_DOWN:
                if self.scroll_offset > 0:
                    self.scroll_offset -= 1
            elif key == curses.KEY_PPAGE:
                height, _ = self.stdscr.getmaxyx()
                self.scroll_offset = min(len(self.output_buffer) - 1, self.scroll_offset + (height - 5))
            elif key == curses.KEY_NPAGE:
                height, _ = self.stdscr.getmaxyx()
                self.scroll_offset = max(0, self.scroll_offset - (height - 5))
            elif key == curses.KEY_F2:
                self.toggle_connection()
            elif key == curses.KEY_F3:
                self.change_settings()
            elif key == curses.KEY_F10:
                self.stop_event.set()
                if self.read_thread:
                    self.read_thread.join()
                if self.serial_conn:
                    self.serial_conn.close()
                break
            elif key in (curses.KEY_BACKSPACE, 8, 127):
                self.input_buffer = self.input_buffer[:-1]
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                self.send_data()
            elif 32 <= key <= 126:
                self.input_buffer += chr(key)

def main(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) # Header/Footer
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK) # Borders
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Titles
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN) # Highlight
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK) # Connected
    curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK) # Disconnected

    app = SerialTerminalApp(stdscr)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
