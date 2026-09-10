import os
import sys
import time
import datetime
import psutil

def draw_status_bar():
    # Attempt to get terminal size
    try:
        term_h, term_w = os.get_terminal_size()
    except Exception:
        term_h, term_w = 24, 80

    while True:
        try:
            now = datetime.datetime.now().strftime("%H:%M:%S")
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent

            # Check for battery if available
            bat_str = ""
            if hasattr(psutil, "sensors_battery"):
                bat = psutil.sensors_battery()
                if bat is not None:
                    bat_str = f"| BAT: {int(bat.percent)}% "

            status_text = f" Doda OS Status | CPU: {cpu:04.1f}% | MEM: {mem:04.1f}% {bat_str}| TIME: {now} "

            # Pad to right
            pad = term_w - len(status_text)
            if pad > 0:
                status_text = (" " * pad) + status_text

            # ANSI to save cursor position, jump to bottom line, print in reverse video, and restore cursor
            # \033[s : save cursor
            # \033[{term_h};0H : jump to bottom left
            # \033[7m : reverse video (colors)
            # \033[0m : reset
            # \033[u : restore cursor

            sys.stdout.write(f"\033[s\033[{term_h};0H\033[7m{status_text[:term_w]}\033[0m\033[u")
            sys.stdout.flush()

            time.sleep(1)
        except KeyboardInterrupt:
            # Clear the bottom line on exit
            sys.stdout.write(f"\033[s\033[{term_h};0H\033[K\033[u")
            sys.stdout.flush()
            break
        except Exception:
            # Ignore and loop if terminal size changes rapidly
            time.sleep(1)

if __name__ == "__main__":
    # Start as a daemon/background task
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        # On linux, fork to background
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except AttributeError:
            pass # Windows doesn't have fork

    print("Doda Resident Status Bar loaded. It will draw at the bottom of the screen.")
    print("Press Ctrl+C to stop.")

    # Initialize CPU percentage
    psutil.cpu_percent(interval=None)
    time.sleep(0.1)

    draw_status_bar()
