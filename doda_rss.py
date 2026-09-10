import curses
import sys

import feedparser
import html
import re
import textwrap

class RSSReaderApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr

        # UI State
        self.active_pane = 0 # 0: Feeds, 1: Headlines, 2: Reading

        self.feeds = [
            {"name": "Hacker News", "url": "https://news.ycombinator.com/rss"},
            {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
            {"name": "OSNews", "url": "https://www.osnews.com/feed/"}
        ]

        self.headlines = []
        self.current_article = [] # List of strings (wrapped lines)

        # Selections
        self.feed_sel = 0
        self.feed_scroll = 0

        self.hl_sel = 0
        self.hl_scroll = 0

        self.art_scroll = 0

    def draw_box(self, y, x, h, w, title, is_active):
        color = curses.color_pair(4) if is_active else curses.color_pair(2)
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
            tcolor = curses.color_pair(1) | curses.A_BOLD if is_active else curses.color_pair(3) | curses.A_BOLD
            self.stdscr.attron(tcolor)
            try:
                self.stdscr.addstr(y, x + 2, f" {title} ")
            except curses.error:
                pass
            self.stdscr.attroff(tcolor)

    def draw(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Header
        header = " Doda RSS - Syndication Feed Reader "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(0, 0, header.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        if width < 80 or height < 20:
            try:
                self.stdscr.addstr(2, 2, "Terminal too small. Need 80x20.")
            except curses.error:
                pass
            self.stdscr.refresh()
            return

        # Layout metrics
        feed_w = 25
        main_w = width - feed_w - 2
        hl_h = (height - 3) // 2
        art_h = height - 3 - hl_h

        # Feeds Box (Left)
        self.draw_box(2, 0, height - 3, feed_w, "Feeds", self.active_pane == 0)

        # Draw Feed list
        vis_feeds = height - 5
        for i in range(min(vis_feeds, len(self.feeds))):
            name = self.feeds[i]['name'][:feed_w-4]
            attr = curses.color_pair(4) | curses.A_BOLD if i == self.feed_sel else curses.color_pair(0)
            try:
                self.stdscr.attron(attr)
                self.stdscr.addstr(3 + i, 2, name.ljust(feed_w - 4))
                self.stdscr.attroff(attr)
            except curses.error:
                pass

        # Headlines Box (Top Right)
        self.draw_box(2, feed_w + 1, hl_h, main_w, "Headlines", self.active_pane == 1)

        # Draw Headlines list
        vis_hl = hl_h - 2
        if self.hl_sel < self.hl_scroll: self.hl_scroll = self.hl_sel
        elif self.hl_sel >= self.hl_scroll + vis_hl: self.hl_scroll = self.hl_sel - vis_hl + 1

        for i in range(vis_hl):
            idx = self.hl_scroll + i
            if idx >= len(self.headlines): break

            title = self.headlines[idx].get('title', 'No Title')[:main_w-4]
            attr = curses.color_pair(4) | curses.A_BOLD if idx == self.hl_sel else curses.color_pair(0)
            try:
                self.stdscr.attron(attr)
                self.stdscr.addstr(3 + i, feed_w + 3, title.ljust(main_w - 4))
                self.stdscr.attroff(attr)
            except curses.error:
                pass

        # Article Box (Bottom Right)
        art_y = 2 + hl_h
        self.draw_box(art_y, feed_w + 1, art_h, main_w, "Article", self.active_pane == 2)

        # Draw Article content
        vis_art = art_h - 2
        for i in range(vis_art):
            idx = self.art_scroll + i
            if idx >= len(self.current_article): break

            line = self.current_article[idx][:main_w-4]
            try:
                self.stdscr.addstr(art_y + 1 + i, feed_w + 3, line)
            except curses.error:
                pass

        # Footer
        footer = " TAB: Switch Pane | ENTER: Fetch/Read | Arrows: Navigate | F10: Quit "
        self.stdscr.attron(curses.color_pair(1))
        try:
            self.stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1))

        self.stdscr.refresh()

    def fetch_feed(self):
        url = self.feeds[self.feed_sel]['url']

        # Show loading
        self.headlines = []
        self.current_article = []
        self.hl_sel = 0
        self.hl_scroll = 0
        self.art_scroll = 0

        height, width = self.stdscr.getmaxyx()
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            msg = f" Fetching {url}... "
            self.stdscr.addstr(height // 2, (width - len(msg)) // 2, msg)
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.refresh()

        try:
            feed = feedparser.parse(url)
            self.headlines = feed.entries
            if not self.headlines:
                self.headlines = [{'title': 'No entries found or error parsing feed.'}]
        except Exception as e:
            self.headlines = [{'title': f"Error: {e}"}]

    def load_article(self):
        if not self.headlines or self.hl_sel >= len(self.headlines):
            return

        entry = self.headlines[self.hl_sel]

        # Try to find content
        content = ""
        if 'content' in entry:
            content = entry.content[0].value
        elif 'summary' in entry:
            content = entry.summary
        elif 'description' in entry:
            content = entry.description

        # Strip HTML and Unescape
        cleaner = re.compile('<.*?>')
        text = re.sub(cleaner, '', content)
        text = html.unescape(text)

        # Wrap text
        height, width = self.stdscr.getmaxyx()
        main_w = width - 25 - 2 - 4 # Total width - feed panel - borders/padding

        self.current_article = []
        for line in text.splitlines():
            line = line.strip()
            if line:
                self.current_article.extend(textwrap.wrap(line, width=max(10, main_w)))
                self.current_article.append("") # Empty line for paragraphs

        self.art_scroll = 0

    def run(self):
        while True:
            self.draw()

            key = self.stdscr.getch()

            if key == ord('\t'):
                self.active_pane = (self.active_pane + 1) % 3
            elif key == curses.KEY_UP:
                if self.active_pane == 0 and self.feed_sel > 0:
                    self.feed_sel -= 1
                elif self.active_pane == 1 and self.hl_sel > 0:
                    self.hl_sel -= 1
                elif self.active_pane == 2 and self.art_scroll > 0:
                    self.art_scroll -= 1
            elif key == curses.KEY_DOWN:
                if self.active_pane == 0 and self.feed_sel < len(self.feeds) - 1:
                    self.feed_sel += 1
                elif self.active_pane == 1 and self.hl_sel < len(self.headlines) - 1:
                    self.hl_sel += 1
                elif self.active_pane == 2 and self.art_scroll < len(self.current_article) - 1:
                    self.art_scroll += 1
            elif key == curses.KEY_NPAGE and self.active_pane == 2:
                height, _ = self.stdscr.getmaxyx()
                art_h = height - 3 - ((height - 3) // 2)
                self.art_scroll = min(len(self.current_article) - 1, self.art_scroll + art_h - 2)
            elif key == curses.KEY_PPAGE and self.active_pane == 2:
                height, _ = self.stdscr.getmaxyx()
                art_h = height - 3 - ((height - 3) // 2)
                self.art_scroll = max(0, self.art_scroll - (art_h - 2))
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                if self.active_pane == 0:
                    self.fetch_feed()
                    self.active_pane = 1
                elif self.active_pane == 1:
                    self.load_article()
                    self.active_pane = 2
            elif key == curses.KEY_F10 or key in (ord('q'), ord('Q'), 27):
                break

def main(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) # Header/Footer
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK) # Borders
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Titles inactive
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN) # Active / Highlight

    app = RSSReaderApp(stdscr)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
