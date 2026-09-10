# Doda Shell (Command Line Environment)

Doda Shell is a custom, interactive Python REPL designed to replace standard bash/cmd interfaces. It binds the entire Doda DOS ecosystem together, providing a nostalgic `C:\>` style prompt with modern usability enhancements.

## Features

- **Persistent Command History:** Remember previous commands across sessions (using the `.doda_history` file).
- **Tab Completion:** Use the `TAB` key to auto-complete filenames, directories, and built-in commands.
- **Colored Output:** The built-in `dir` command categorizes and color-codes directories and files for readability.
- **Short Name Execution:** To run any Doda DOS utility, simply type its short name. For example, typing `nc` automatically resolves to `python doda_nc.py`.

## Built-in Commands

- `dir` (or `ls`, `ll`): List directory contents with ANSI color coding.
- `cd <path>`: Change the current working directory.
- `cls` (or `clear`): Clear the terminal screen.
- `type <file>`: Print the raw contents of a file to the screen.
- `echo <text>`: Print text.
- `help`: Display a list of available built-in commands.
- `quit` (or `exit`): Exit the shell.

## How to Use

Launch the shell to enter the Doda DOS environment:
```bash
python doda_shell.py
```
