# Doda Serial (Lab Instrument Control)

Doda Serial is a text-mode serial terminal program. It is designed to act like classic communication software (such as Procomm or Telix) but focuses specifically on interfacing with modern lab instruments, embedded devices, and microcontrollers via serial ports (RS-232, USB-to-Serial).

## Features

- **Interactive Terminal:** Dedicated output display and command input bar for sending commands to devices.
- **Configurable Connection:** Quickly configure the target COM Port (e.g., `/dev/ttyUSB0` or `COM1`) and Baudrate on the fly.
- **Asynchronous Reading:** Continuously reads from the serial port in the background without blocking the UI.
- **Auto-Formatting:** Automatically appends `\r\n` (Carriage Return + Line Feed) to outgoing commands, as expected by most lab instruments.

## How to Use

Ensure you have the required dependencies (`pyserial`) installed:
```bash
pip install -r requirements.txt
```

Launch the utility in your terminal:
```bash
python doda_serial.py
```

*Note: You may need specific user permissions (like joining the `dialout` group on Linux) to successfully open serial ports.*

## Shortcut Keys

| Key             | Action                  |
| --------------- | ----------------------- |
| **F2**          | Connect or Disconnect the serial port. |
| **F3**          | Open settings to change Port and Baudrate. |
| **F10**         | Exit the application safely. |
| **ENTER**       | Send the currently typed command. |
| **Arrow Keys**  | Scroll the output buffer up and down. |
