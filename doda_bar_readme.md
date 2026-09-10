# Doda Bar (Resident Status Bar)

Doda Bar is a lightweight, memory-resident status bar (similar to TSRs of the MS-DOS era). When run, it persistently floats at the bottom line of your terminal screen, providing a live readout of your system's vitals without interrupting your command line prompt or other non-curses applications.

## Features

- **Live Metrics:** Displays current Time, CPU load percentage, RAM usage, and Battery status (if available on laptops).
- **ANSI Engine:** Achieves the "floating" effect by utilizing ANSI escape codes to save the cursor position, jump to the bottom row, draw the bar in reverse video, and restore the cursor location every second.

## How to Use

Simply execute the script in the background:
```bash
python doda_bar.py &
```

To stop the bar, bring the job to the foreground (`fg`) and press `Ctrl+C`, or kill its process.
