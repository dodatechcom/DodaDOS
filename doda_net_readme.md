# Doda Net (TCP/IP Network Suite)

Doda Net is a bundled, out-of-the-box TCP/IP networking suite built for the Doda DOS collection. It provides a polished, menu-driven interface to access the internet and network utilities directly from the terminal without configuration headaches.

## Features

- **Ping Utility:** Easily ping hostnames or IP addresses. It steps out of the `curses` UI temporarily to show real-time ping output, then returns gracefully to the menu.
- **Text Web Browser:** A built-in, rudimentary text-mode web browser that fetches HTTP/HTTPS URLs, strips HTML tags, and presents the raw text payload in a scrollable view.

## How to Use

Execute the utility from your terminal:

```bash
python doda_net.py
```

### Main Menu Shortcuts

| Key             | Action                  |
| --------------- | ----------------------- |
| **Arrow Keys**  | Navigate the menu.      |
| **ENTER**       | Select the highlighted tool. |

### Browser Shortcuts

| Key             | Action                  |
| --------------- | ----------------------- |
| **Arrow Keys**  | Scroll up/down or Page up/down through the web page text. |
| **Q, ESC**      | Exit the browser and return to the main menu. |
