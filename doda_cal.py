import curses
import calendar
import datetime
import json
import os

class CalendarApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr

        today = datetime.date.today()
        self.year = today.year
        self.month = today.month
        self.day = today.day

        self.notes_file = "doda_cal_notes.json"
        self.notes = self.load_notes()

        # State
        self.is_editing = False

    def load_notes(self):
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_notes(self):
        try:
            with open(self.notes_file, 'w') as f:
                json.dump(self.notes, f)
        except Exception:
            pass

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
        header = " Doda Cal - Personal Information Manager "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(0, 0, header.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        if width < 60 or height < 15:
            try:
                self.stdscr.addstr(2, 2, "Terminal too small.")
            except curses.error:
                pass
            return

        # Draw Calendar Box (Left)
        cal_w = 34
        self.draw_box(2, 1, 12, cal_w, f"{calendar.month_name[self.month]} {self.year}")

        # Calendar Headers
        headers = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        try:
            for i, h in enumerate(headers):
                self.stdscr.addstr(3, 3 + i * 4, h)
        except curses.error:
            pass

        # Calendar Days
        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(self.year, self.month)

        for row, week in enumerate(month_days):
            for col, d in enumerate(week):
                if d != 0:
                    y = 5 + row
                    x = 3 + col * 4

                    # Highlight selected day
                    if d == self.day:
                        attr = curses.color_pair(4) | curses.A_BOLD
                    else:
                        attr = curses.color_pair(0)

                    # Add indicator if notes exist
                    date_key = f"{self.year}-{self.month:02d}-{d:02d}"
                    note_indicator = "*" if date_key in self.notes and self.notes[date_key] else " "

                    try:
                        self.stdscr.attron(attr)
                        self.stdscr.addstr(y, x, f"{d:2d}{note_indicator}")
                        self.stdscr.attroff(attr)
                    except curses.error:
                        pass

        # Draw Notes Box (Right)
        notes_w = width - cal_w - 4
        notes_x = cal_w + 3
        self.draw_box(2, notes_x, 12, notes_w, "Notes")

        date_key = f"{self.year}-{self.month:02d}-{self.day:02d}"
        note_text = self.notes.get(date_key, "")

        try:
            self.stdscr.addstr(3, notes_x + 2, f"Date: {date_key}")

            # Draw notes content
            lines = note_text.split('\n')
            for i, line in enumerate(lines[:8]):
                disp_line = line[:notes_w - 4]
                self.stdscr.addstr(5 + i, notes_x + 2, disp_line)
        except curses.error:
            pass

        # Footer
        footer = " Arrows: Navigate | ENTER: Edit Note | F10: Quit "
        self.stdscr.attron(curses.color_pair(2))
        try:
            self.stdscr.addstr(height - 1, 0, footer.center(width)[:width-1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2))

    def change_day(self, delta):
        # Handle wrapping around months
        try:
            curr_date = datetime.date(self.year, self.month, self.day)
            new_date = curr_date + datetime.timedelta(days=delta)
            self.year = new_date.year
            self.month = new_date.month
            self.day = new_date.day
        except ValueError:
            pass

    def run(self):
        while True:
            self.draw()
            self.stdscr.refresh()

            key = self.stdscr.getch()

            if key == curses.KEY_RIGHT:
                self.change_day(1)
            elif key == curses.KEY_LEFT:
                self.change_day(-1)
            elif key == curses.KEY_UP:
                self.change_day(-7)
            elif key == curses.KEY_DOWN:
                self.change_day(7)
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                self.edit_note()
            elif key == curses.KEY_F10:
                break

    def edit_note(self):
        date_key = f"{self.year}-{self.month:02d}-{self.day:02d}"
        current_note = self.notes.get(date_key, "")

        # We will drop to a very simple inline input for the note, or we can use an external editor
        # For a self-contained PIM, we'll just read a single line at the bottom
        curses.echo()
        try:
            curses.curs_set(1)
        except curses.error:
            pass

        height, width = self.stdscr.getmaxyx()
        prompt = f"Note for {date_key}: "
        self.stdscr.attron(curses.color_pair(2))
        try:
            self.stdscr.addstr(height - 2, 0, prompt.ljust(width)[:width-1])
            # Pre-fill current text (visually) - simple implementation just expects overwrite
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(2))
        self.stdscr.refresh()

        try:
            new_note = self.stdscr.getstr(height - 2, len(prompt), width - len(prompt) - 1).decode('utf-8').strip()
            if new_note:
                self.notes[date_key] = new_note
            elif date_key in self.notes:
                # If they entered nothing, maybe they want to clear it
                # For safety, let's only clear if they explicitly backspaced or it's empty
                # Actually, simpler: just clear it if empty string
                del self.notes[date_key]

            self.save_notes()
        except Exception:
            pass

        curses.noecho()
        try:
            curses.curs_set(0)
        except curses.error:
            pass

        # Clear prompt
        try:
            self.stdscr.addstr(height - 2, 0, " ".ljust(width)[:width-1])
        except curses.error:
            pass

def main(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) # Header
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK) # Borders / Footer
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Titles
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN) # Highlight

    app = CalendarApp(stdscr)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
