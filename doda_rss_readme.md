# Doda RSS (Feed Reader)

Doda RSS is a 3-pane text-mode RSS/Atom feed aggregator for the Doda DOS terminal suite. It fetches live news feeds from the internet and displays them using a clean, retro `curses` UI.

## Features

- **3-Pane Interface:** Easily navigate between your Feeds list, Headlines list, and the Article reading pane using the `TAB` key.
- **Auto-Parsing:** Integrates the `feedparser` library to cleanly extract titles and content, automatically stripping messy HTML tags to render pure text for a terminal experience.
- **Pre-configured Feeds:** Comes out-of-the-box with feeds for Hacker News, BBC, and OSNews.

## How to Use

Ensure you have the required dependencies (`feedparser`) installed:
```bash
pip install -r requirements.txt
```

Launch the reader:
```bash
python doda_rss.py
```

## Shortcut Keys

| Key             | Action                  |
| --------------- | ----------------------- |
| **TAB**         | Switch focus between the Feeds, Headlines, and Article panes. |
| **Arrow Keys**  | Scroll lists and text up and down. |
| **ENTER**       | Fetch the selected feed (in pane 1) or load the selected article (in pane 2). |
| **PgUp / PgDn** | Scroll the article text by full pages. |
| **Q, ESC, F10** | Exit the application.   |
