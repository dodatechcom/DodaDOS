import os
import sys
import subprocess
import glob
import shlex

# Attempt to load readline for command history and completion
try:
    import readline
except ImportError:
    readline = None

class DodaShell:
    def __init__(self):
        self.running = True
        self.history_file = ".doda_history"
        self.aliases = {
            'ls': 'dir',
            'll': 'dir',
            'clear': 'cls',
            'exit': 'quit'
        }

        self.setup_readline()

    def setup_readline(self):
        if not readline:
            return

        try:
            readline.read_history_file(self.history_file)
        except FileNotFoundError:
            pass

        readline.set_history_length(1000)

        # Tab completion
        def completer(text, state):
            options = [i for i in glob.glob(text + '*') if i]
            # also add builtins
            builtins = ['dir', 'cls', 'quit', 'help', 'cd', 'echo', 'type']
            options.extend([b for b in builtins if b.startswith(text)])

            if state < len(options):
                return options[state]
            else:
                return None

        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")

    def save_history(self):
        if readline:
            readline.write_history_file(self.history_file)

    def print_colored(self, text, color_code):
        print(f"\033[{color_code}m{text}\033[0m")

    def cmd_dir(self, args):
        path = args[0] if args else "."
        try:
            entries = os.listdir(path)
            # Separate dirs and files
            dirs = []
            files = []
            for e in entries:
                if os.path.isdir(os.path.join(path, e)):
                    dirs.append(e)
                else:
                    files.append(e)

            dirs.sort()
            files.sort()

            print(f" Directory of {os.path.abspath(path)}\n")

            for d in dirs:
                self.print_colored(f"{d:<20} <DIR>", "1;36") # Cyan bold

            for f in files:
                sz = os.path.getsize(os.path.join(path, f))
                self.print_colored(f"{f:<20} {sz:>10} bytes", "0") # Default

            print(f"\n  {len(files)} File(s), {len(dirs)} Dir(s)")

        except Exception as e:
            print(f"Error accessing directory: {e}")

    def cmd_cd(self, args):
        if not args:
            print(os.getcwd())
            return

        path = args[0]
        try:
            os.chdir(path)
        except Exception as e:
            print(f"Cannot change dir: {e}")

    def run_doda_tool(self, cmd_name, args):
        # Maps short names like 'nc' to 'doda_nc.py'
        script_name = f"doda_{cmd_name}.py"
        if os.path.exists(script_name):
            try:
                subprocess.run([sys.executable, script_name] + args)
                return True
            except Exception as e:
                print(f"Error launching {script_name}: {e}")
                return True
        return False

    def execute_command(self, cmd_str):
        if not cmd_str.strip():
            return

        try:
            parts = shlex.split(cmd_str)
        except ValueError:
            print("Syntax error in command (unclosed quotes?).")
            return

        cmd = parts[0].lower()
        args = parts[1:]

        # Resolve aliases
        if cmd in self.aliases:
            cmd = self.aliases[cmd]

        # Built-ins
        if cmd in ('quit', 'exit'):
            self.running = False
        elif cmd == 'cls':
            sys.stdout.write('\033[2J\033[H')
            sys.stdout.flush()
        elif cmd == 'dir':
            self.cmd_dir(args)
        elif cmd == 'cd':
            self.cmd_cd(args)
        elif cmd == 'echo':
            print(" ".join(args))
        elif cmd == 'help':
            print("Doda Shell Built-ins: cd, dir, cls, echo, type, quit")
            print("Aliases: ls -> dir, ll -> dir, clear -> cls, exit -> quit")
            print("To run a Doda utility, just type its short name (e.g., 'nc', 'edit config.txt').")
        elif cmd == 'type':
            if args:
                try:
                    with open(args[0], 'r') as f:
                        print(f.read())
                except Exception as e:
                    print(f"Error reading file: {e}")
            else:
                print("Syntax: type <filename>")
        else:
            # Check if it's a Doda tool
            if self.run_doda_tool(cmd, args):
                return

            # Fallback to system shell
            try:
                subprocess.run(parts)
            except FileNotFoundError:
                print(f"Bad command or file name: '{cmd}'")
            except Exception as e:
                print(f"Execution error: {e}")

    def run(self):
        print("Doda DOS Interactive Shell v1.0")
        print("Type 'help' for built-in commands.\n")

        while self.running:
            try:
                # MS-DOS style prompt C:\>
                prompt = f"{os.getcwd()}>"
                cmd_str = input(prompt)
                self.execute_command(cmd_str)
            except KeyboardInterrupt:
                print("^C")
            except EOFError:
                self.running = False
                print("exit")

        self.save_history()

if __name__ == "__main__":
    shell = DodaShell()
    shell.run()
