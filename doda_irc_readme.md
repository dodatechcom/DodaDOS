# Doda IRC (Terminal Client)

Doda IRC is a text-mode IRC (Internet Relay Chat) client. It allows you to connect to modern retro-computing networks (like Libera.chat) directly from your DOS-like terminal environment.

## Features

- **Asynchronous Chat:** Uses background threading to ensure the UI remains responsive while messages stream in.
- **Split-Pane UI:** A classic chat layout with a scrollable message history box and an active input bar.
- **Basic Commands:** Supports standard IRC slashes commands like `/join <channel>` and `/nick <nickname>`.

## How to Use

Execute the utility:
```bash
python doda_irc.py
```

## Shortcut Keys

| Key             | Action                  |
| --------------- | ----------------------- |
| **F2**          | Connect to the IRC server. |
| **F3**          | Disconnect from the IRC server. |
| **Arrow Keys**  | Scroll the message history. |
| **F10**         | Exit the client safely. |
