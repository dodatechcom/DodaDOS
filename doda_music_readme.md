# Doda Music Player

Doda Music is a text-based terminal audio player utilizing `pygame` to bring background audio to your DOS-like environment. It allows you to browse and play a variety of audio formats directly from the command line.

## Features

- **Built-in File Browser:** Navigate your directories within a clean `curses` UI to find audio files easily.
- **Audio Playback:** Uses the `pygame.mixer` backend to play standard formats (MP3, WAV, OGG, MIDI).
- **Playback Controls:** Pause, unpause, and stop currently playing tracks. The UI displays the status in real-time.

## How to Use

Ensure you have the required dependencies (`pygame`) installed:
```bash
pip install -r requirements.txt
```

Execute the utility from your terminal to launch the audio browser:
```bash
python doda_music.py
```

## Shortcut Keys

| Key             | Action                  |
| --------------- | ----------------------- |
| **Arrow Keys**  | Navigate the directory browser. |
| **ENTER**       | Open a directory or PLAY the selected audio file. |
| **SPACEBAR**    | Pause / Unpause the current track. |
| **S**           | Stop playback completely. |
| **Q, ESC, F10** | Exit the application.   |
