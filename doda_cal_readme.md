# Doda Cal (Personal Information Manager)

Doda Cal is a retro-style, terminal-based Personal Information Manager and Calendar utility. Inspired by classic MS-DOS scheduling tools, it allows you to quickly view a monthly calendar grid and attach small notes to specific days.

## Features

- **Interactive Calendar:** A classic split-screen interface displaying a full monthly calendar on the left and selected date details on the right.
- **Fast Navigation:** Use arrow keys to seamlessly traverse days, automatically bridging across months and years.
- **Note Taking:** Press Enter on any day to attach a quick note. Notes are persistently saved locally to a `doda_cal_notes.json` file.
- **Visual Indicators:** Days with attached notes are marked with an asterisk (`*`) on the calendar grid.

## How to Use

Execute the utility from your terminal:

```bash
python doda_cal.py
```

*Note: The terminal window must be at least 60x15 characters to display the calendar correctly.*

## Shortcut Keys

| Key             | Action                  |
| --------------- | ----------------------- |
| **Arrow Keys**  | Navigate between days.  |
| **ENTER**       | Add or overwrite a note for the currently selected day. |
| **F10**         | Exit the application.   |
