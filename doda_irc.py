import curses
import socket
import threading
import time

class IRCClientApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.server = "irc.libera.chat"
        self.port = 6667
        self.channel = "#dodados"
        self.nickname = "DodaUser_" + str(int(time.time()) % 1000)

        self.sock = None
        self.is_connected = False
        self.stop_event = threading.Event()
        self.read_thread = None

        self.messages = []
        self.input_buffer = ""
        self.scroll_offset = 0

        self.active_pane = 1 # 0 for settings/connect, 1 for chat input

    def append_message(self, msg):
        self.messages.append(msg)
        if len(self.messages) > 1000:
            self.messages = self.messages[-1000:]

        # Auto-scroll if we are at the bottom
        height, _ = self.stdscr.getmaxyx()
        vis = height - 6
        if self.scroll_offset >= max(0, len(self.messages) - vis - 1):
            self.scroll_offset = max(0, len(self.messages) - vis)

    def irc_read_loop(self):
        buffer = ""
        while not self.stop_event.is_set():
            if self.sock:
                try:
                    data = self.sock.recv(2048)
                    if not data:
                        self.append_message("Connection closed by server.")
                        self.is_connected = False
                        break

                    buffer += data.decode('utf-8', errors='ignore')
                    while '\r\n' in buffer:
                        line, buffer = buffer.split('\r\n', 1)
                        if line.startswith("PING"):
                            self.sock.send(f"PONG {line.split()[1]}\r\n".encode('utf-8'))
                        else:
                            self.append_message(line)
                except socket.timeout:
                    continue
                except Exception as e:
                    self.append_message(f"Socket error: {e}")
                    self.is_connected = False
                    break
            else:
                break

    def connect_irc(self):
        if self.is_connected:
            self.append_message("Already connected. Disconnect first.")
            return

        self.append_message(f"Connecting to {self.server}:{self.port} as {self.nickname}...")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(1.0)
            self.sock.connect((self.server, self.port))

            self.sock.send(f"USER {self.nickname} 0 * :Doda DOS User\r\n".encode('utf-8'))
            self.sock.send(f"NICK {self.nickname}\r\n".encode('utf-8'))

            self.is_connected = True
            self.stop_event.clear()
            self.read_thread = threading.Thread(target=self.irc_read_loop, daemon=True)
            self.read_thread.start()

            time.sleep(1)
            self.sock.send(f"JOIN {self.channel}\r\n".encode('utf-8'))
            self.append_message(f"Joined {self.channel}")

        except Exception as e:
            self.append_message(f"Failed to connect: {e}")
            if self.sock:
                self.sock.close()
            self.is_connected = False

    def disconnect_irc(self):
        if self.is_connected:
            self.stop_event.set()
            try:
                self.sock.send("QUIT :Leaving\r\n".encode('utf-8'))
                self.sock.close()
            except Exception:
                pass
            if self.read_thread:
                self.read_thread.join()
            self.is_connected = False
            self.append_message("Disconnected.")

    def send_message(self):
        if not self.input_buffer:
            return

        if self.input_buffer.startswith('/'):
            # Basic commands
            cmd = self.input_buffer.split()
            if cmd[0] == '/join' and len(cmd) > 1:
                self.channel = cmd[1]
                if self.is_connected:
                    self.sock.send(f"JOIN {self.channel}\r\n".encode('utf-8'))
                    self.append_message(f"Joined {self.channel}")
            elif cmd[0] == '/nick' and len(cmd) > 1:
                self.nickname = cmd[1]
                if self.is_connected:
                    self.sock.send(f"NICK {self.nickname}\r\n".encode('utf-8'))
        else:
            # Regular chat
            if self.is_connected:
                msg = f"PRIVMSG {self.channel} :{self.input_buffer}\r\n"
                try:
                    self.sock.send(msg.encode('utf-8'))
                    self.append_message(f"<{self.nickname}> {self.input_buffer}")
                except Exception as e:
                    self.append_message(f"Send failed: {e}")
            else:
                self.append_message("Cannot send: Not connected.")

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
        header = f" Doda IRC - {self.nickname} on {self.server} {self.channel} "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(0, 0, header.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Messages Box
        msg_h = height - 5
        self.draw_box(1, 0, msg_h, width, "Chat")

        vis = msg_h - 2
        start_idx = self.scroll_offset
        for i in range(vis):
            idx = start_idx + i
            if idx >= len(self.messages):
                break
            try:
                self.stdscr.addstr(2 + i, 2, self.messages[idx][:width-4])
            except curses.error:
                pass

        # Input Box
        self.stdscr.attron(curses.color_pair(2))
        try:
            self.stdscr.addstr(height - 3, 0, " > " + self.input_buffer.ljust(width-4)[:width-4])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2))

        # Footer
        footer = " F2: Connect | F3: Disconnect | F10: Quit | /nick <name> | /join <#chan> "
        self.stdscr.attron(curses.color_pair(1))
        try:
            self.stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1))

    def run(self):
        self.stdscr.nodelay(True)
        while True:
            self.draw()
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key == -1:
                time.sleep(0.05)
                continue

            if key == curses.KEY_F2:
                self.connect_irc()
            elif key == curses.KEY_F3:
                self.disconnect_irc()
            elif key == curses.KEY_UP:
                if self.scroll_offset > 0:
                    self.scroll_offset -= 1
            elif key == curses.KEY_DOWN:
                height, _ = self.stdscr.getmaxyx()
                vis = height - 6
                if self.scroll_offset < len(self.messages) - vis:
                    self.scroll_offset += 1
            elif key == curses.KEY_NPAGE:
                height, _ = self.stdscr.getmaxyx()
                vis = height - 6
                self.scroll_offset = min(len(self.messages) - vis, self.scroll_offset + vis)
                if self.scroll_offset < 0: self.scroll_offset = 0
            elif key == curses.KEY_PPAGE:
                height, _ = self.stdscr.getmaxyx()
                vis = height - 6
                self.scroll_offset = max(0, self.scroll_offset - vis)
            elif key in (curses.KEY_BACKSPACE, 8, 127):
                self.input_buffer = self.input_buffer[:-1]
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                self.send_message()
            elif key == curses.KEY_F10:
                self.disconnect_irc()
                break
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

    app = IRCClientApp(stdscr)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
