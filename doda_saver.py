import curses
import time
import random

class ScreensaverApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.stdscr.nodelay(True)
        curses.curs_set(0)

        self.savers = [
            "1. Terminal Cat",
            "2. Bored Ghost",
            "3. Cozy Campfire",
            "4. Clumsy Construction",
            "5. Mischievous Dog",
            "6. Exit"
        ]
        self.selected_idx = 0

    def draw_menu(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        title = " DODA SCREENSAVERS "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        try:
            self.stdscr.addstr(2, (width - len(title)) // 2, title)
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        for i, item in enumerate(self.savers):
            y = 5 + i * 2
            x = (width - 25) // 2
            attr = curses.color_pair(2) | curses.A_BOLD if i == self.selected_idx else curses.color_pair(0)
            try:
                self.stdscr.attron(attr)
                self.stdscr.addstr(y, x, item.ljust(25))
                self.stdscr.attroff(attr)
            except curses.error:
                pass

        self.stdscr.refresh()

    def run_saver(self, saver_id):
        self.stdscr.clear()
        if saver_id == 0:
            self.saver_cat()
        elif saver_id == 1:
            self.saver_ghost()
        elif saver_id == 2:
            self.saver_campfire()
        elif saver_id == 3:
            self.saver_construction()
        elif saver_id == 4:
            self.saver_dog()
        else:
            # placeholders
            while True:
                k = self.stdscr.getch()
                if k != -1: break
                time.sleep(0.05)

    def draw_str(self, y, x, s, attr=0):
        try:
            self.stdscr.attron(attr)
            self.stdscr.addstr(y, x, s)
            self.stdscr.attroff(attr)
        except curses.error:
            pass

    def saver_cat(self):
        height, width = self.stdscr.getmaxyx()
        y = height - 2
        x = width // 2

        cat_frames = ["=^..^=", "=^--^="]
        dir_x = 1
        state = 'walk' # walk, sit, sleep, startle
        timer = 0
        bug_x, bug_y = -1, -1

        self.stdscr.clear()

        while True:
            k = self.stdscr.getch()
            if k != -1:
                # Startle before exit
                self.stdscr.clear()
                self.draw_str(y - 1, x, " =O.O= !!!")
                self.stdscr.refresh()
                time.sleep(0.5)
                break

            self.stdscr.clear()

            if state == 'walk':
                frame = cat_frames[timer % 2]
                x += dir_x
                if x <= 1 or x >= width - 8:
                    dir_x *= -1

                # Chance to sit or chase bug
                if random.random() < 0.05:
                    state = random.choice(['sit', 'bug'])
                    timer = 0
                    if state == 'bug':
                        bug_x = random.randint(5, width - 5)
                        bug_y = y - random.randint(1, 5)

            elif state == 'sit':
                frame = " =^..^="
                if timer > 20:
                    if random.random() < 0.3:
                        state = 'sleep'
                        timer = 0
                    else:
                        state = 'walk'
                        dir_x = random.choice([-1, 1])

            elif state == 'sleep':
                frame = " =u..u="
                if timer % 10 < 5:
                    self.draw_str(y - 1, x + 4, "z")
                else:
                    self.draw_str(y - 2, x + 5, "Z")

                if timer > 60 and random.random() < 0.1:
                    state = 'sit'

            elif state == 'bug':
                frame = " =^o.o^=" if timer % 2 == 0 else " =^O.O^="
                if x < bug_x: x += 1
                elif x > bug_x: x -= 1

                self.draw_str(bug_y, bug_x, "*")
                bug_y += random.choice([-1, 0, 1])
                bug_x += random.choice([-1, 1])

                if timer > 30 or abs(x - bug_x) < 2:
                    state = 'sit'
                    timer = 0

            self.draw_str(y, x, frame)
            self.stdscr.refresh()
            timer += 1
            time.sleep(0.15)

    def saver_ghost(self):
        height, width = self.stdscr.getmaxyx()
        x = width // 2
        y = height // 2

        ghost = " .-. \n(o o)\n| O \\\n \\   \\\n  `~~~'"
        jokes = [
            "Are you afraid of the DOS?",
            "640K ought to be enough for anybody...",
            "Loading HIGH... Boo!",
            "I haunt IRQ 7.",
            "Insert Disk 2 to continue haunting.",
            "A fatal exception 0E has occurred.",
            "Abort, Retry, Fail, Haunt?"
        ]

        dx, dy = 1, 1
        timer = 0
        state = 'float'
        joke = ""
        joke_idx = 0
        joke_x, joke_y = 0, 0

        # Color init for ghost (Cyan) and Ecto (Blue)
        curses.init_pair(10, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(11, curses.COLOR_BLUE, curses.COLOR_BLACK)

        ecto_trails = [] # (y, x, age)

        self.stdscr.clear()

        while True:
            k = self.stdscr.getch()
            if k != -1: break

            self.stdscr.clear()

            # Ecto trails
            new_ecto = []
            for ty, tx, age in ecto_trails:
                if age < 10:
                    char = '.' if age > 5 else 'o'
                    self.draw_str(ty, tx, char, curses.color_pair(11))
                    new_ecto.append((ty, tx, age + 1))
            ecto_trails = new_ecto

            if state == 'float':
                if timer % 2 == 0:
                    ecto_trails.append((y + 4, x + 3, 0))

                x += dx
                y += dy

                if x <= 1 or x >= width - 8: dx *= -1
                if y <= 1 or y >= height - 6: dy *= -1

                # Random drift
                if random.random() < 0.1: dx = random.choice([-1, 1])
                if random.random() < 0.1: dy = random.choice([-1, 1])

                if timer > 50 and random.random() < 0.05:
                    state = 'type'
                    joke = random.choice(jokes)
                    joke_idx = 0
                    joke_y = y - 2 if y > 3 else y + 6
                    joke_x = max(1, min(width - len(joke) - 1, x - len(joke)//2))
                    timer = 0

            elif state == 'type':
                if timer % 2 == 0 and joke_idx < len(joke):
                    joke_idx += 1

                self.draw_str(joke_y, joke_x, joke[:joke_idx], curses.A_BOLD)

                if joke_idx >= len(joke) and timer > len(joke) * 2 + 30:
                    state = 'float'
                    timer = 0

            # Draw ghost
            for i, line in enumerate(ghost.split('\n')):
                self.draw_str(y + i, x, line, curses.color_pair(10) | curses.A_BOLD)

            self.stdscr.refresh()
            timer += 1
            time.sleep(0.1)

    def saver_campfire(self):
        height, width = self.stdscr.getmaxyx()
        cx = width // 2
        cy = height - 5

        curses.init_pair(12, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(13, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        fire_base = [
            "  (  . )  ",
            " ( `  ) . ",
            " ( . ) )  ",
            " /\\___/\\  ",
        ]

        particles = []
        timer = 0
        camper_state = 'none'
        camper_x = -10

        self.stdscr.clear()
        while True:
            k = self.stdscr.getch()
            if k != -1: break

            self.stdscr.clear()

            # Draw fire
            fire_frame = random.choice([
                "  (  . )  \n ( `  ) . \n ( . ) )  \n /\\___/\\  ",
                "  . (  )  \n ( . ` )  \n ( ( . )  \n /\\___/\\  "
            ])
            for i, line in enumerate(fire_frame.split('\n')):
                self.draw_str(cy + i, cx - 5, line, curses.color_pair(12) | curses.A_BOLD)

            # Particles
            if random.random() < 0.4:
                particles.append([cy, cx + random.randint(-2, 2)])

            new_p = []
            for py, px in particles:
                self.draw_str(py, px, random.choice(['.', ',', '`', '*']), curses.color_pair(13) | curses.A_BOLD)
                if py > cy - 8 and random.random() < 0.8:
                    new_p.append([py - 1, px + random.choice([-1, 0, 1])])
            particles = new_p

            # Camper logic
            if camper_state == 'none':
                if timer > 100 and random.random() < 0.05:
                    camper_state = 'walk_in'
                    camper_x = -5
                    timer = 0
            elif camper_state == 'walk_in':
                camper_x += 1
                self.draw_str(cy + 2, camper_x, " o ")
                self.draw_str(cy + 3, camper_x, "/|\\")
                self.draw_str(cy + 4, camper_x, "/ \\")
                if camper_x >= cx - 12:
                    camper_state = 'roast'
                    timer = 0
            elif camper_state == 'roast':
                self.draw_str(cy + 2, camper_x, " o ")
                self.draw_str(cy + 3, camper_x, "/|\\-----[]")
                self.draw_str(cy + 4, camper_x, "/ \\")
                if timer > 50:
                    camper_state = 'walk_out'
            elif camper_state == 'walk_out':
                camper_x -= 1
                self.draw_str(cy + 2, camper_x, " o ")
                self.draw_str(cy + 3, camper_x, "/|\\")
                self.draw_str(cy + 4, camper_x, "/ \\")
                if camper_x < -5:
                    camper_state = 'none'

            self.stdscr.refresh()
            timer += 1
            time.sleep(0.15)

    def saver_construction(self):
        height, width = self.stdscr.getmaxyx()
        ground_y = height - 2

        stack = [] # list of (y, x) for blocks
        workers = [] # list of dicts: x, state

        max_workers = 3

        self.stdscr.clear()
        while True:
            k = self.stdscr.getch()
            if k != -1: break

            self.stdscr.clear()

            # Spawn workers
            if len(workers) < max_workers and random.random() < 0.05:
                # Target a random column near the center to drop a block
                target_x = (width // 2) + random.randint(-5, 5) * 2
                start_x = -5 if target_x < width//2 else width + 5
                workers.append({'x': start_x, 'tx': target_x, 'state': 'carry'})

            # Update workers
            for w in workers:
                if w['state'] == 'carry':
                    if w['x'] < w['tx']: w['x'] += 1
                    elif w['x'] > w['tx']: w['x'] -= 1
                    else:
                        w['state'] = 'drop'
                        # Calculate stack height at tx
                        cols = [by for by, bx in stack if bx == w['tx']]
                        by = min(cols) - 1 if cols else ground_y
                        stack.append((by, w['tx']))
                elif w['state'] == 'drop':
                    w['state'] = 'leave'
                    w['tx'] = -5 if w['x'] < width//2 else width + 5
                elif w['state'] == 'leave':
                    if w['x'] < w['tx']: w['x'] += 1
                    elif w['x'] > w['tx']: w['x'] -= 1

                # Draw worker
                if w['state'] == 'carry':
                    self.draw_str(ground_y - 1, w['x'], "O_o")
                    self.draw_str(ground_y - 2, w['x'], "[█]")
                elif w['state'] == 'drop':
                    self.draw_str(ground_y - 1, w['x'], "o_O")
                else:
                    self.draw_str(ground_y - 1, w['x'], "O_O")

            # Remove left workers
            workers = [w for w in workers if 0 <= w['x'] <= width]

            # Draw stack
            for by, bx in stack:
                self.draw_str(by, bx, "[█]")

            # Collapse logic
            if len(stack) > 15 and random.random() < 0.05:
                # Collapse!
                stack.clear()
                # Make workers throw hands up
                for w in workers:
                    self.draw_str(ground_y - 2, w['x'], "\\o/")

                self.stdscr.refresh()
                time.sleep(1)

            self.stdscr.refresh()
            time.sleep(0.1)

    def saver_dog(self):
        height, width = self.stdscr.getmaxyx()
        ground_y = height - 2
        x = width // 2

        dog_frames_walk = [
            "  __      \no'')}____//\n `_/      )\n (_(_/-(_/",
            "  __      \no'')}____//\n `_/      )\n  _(_/--(_/"
        ]
        dog_dig = "  __      \no'')}____//\n `_/      )\n \\_\\_/-/_/"
        dog_pee = "  __      \no'')}____//\n `_/      )\n (_(_/-- |"
        dog_kick = "  __      \no'')}____//\n `_/      )\n (_(_/--/ /"

        dir_x = 1
        state = 'walk' # walk, dig, pee, kick
        timer = 0

        puddles = [] # (y, x)
        holes = [] # (y, x)

        # Colors
        curses.init_pair(14, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Pee
        curses.init_pair(15, curses.COLOR_BLACK, curses.COLOR_BLACK) # Hole (invisible/dark)

        self.stdscr.clear()
        while True:
            k = self.stdscr.getch()
            if k != -1: break

            self.stdscr.clear()

            # Draw persistent environment
            for hy, hx in holes:
                self.draw_str(hy, hx, "___", curses.A_UNDERLINE)
            for py, px in puddles:
                self.draw_str(py, px, "~~~", curses.color_pair(14) | curses.A_BOLD)

            # State machine
            if state == 'walk':
                frame = dog_frames_walk[timer % 2]
                x += dir_x
                if x <= 1 or x >= width - 12:
                    dir_x *= -1

                if random.random() < 0.05:
                    state = random.choice(['dig', 'pee'])
                    timer = 0

            elif state == 'dig':
                frame = dog_dig if timer % 2 == 0 else dog_frames_walk[0]
                if timer > 15:
                    holes.append((ground_y, x + 5))
                    state = 'walk'

            elif state == 'pee':
                frame = dog_pee
                if timer == 10:
                    puddles.append((ground_y, x - 2 if dir_x == 1 else x + 10))
                if timer > 20:
                    state = 'kick'
                    timer = 0

            elif state == 'kick':
                frame = dog_kick if timer % 2 == 0 else dog_frames_walk[0]
                # Cover up puddles/holes behind the dog
                if timer == 10:
                    target_x = x - 2 if dir_x == 1 else x + 10
                    puddles = [(py, px) for py, px in puddles if abs(px - target_x) > 3]
                    holes = [(hy, hx) for hy, hx in holes if abs(hx - target_x) > 3]

                if timer > 15:
                    state = 'walk'

            # Mirror frame if walking left (naive text flip for dog)
            lines = frame.split('\n')
            if dir_x == -1:
                # Basic reverse mapping for chars
                rev_map = str.maketrans("()/{}`'<>", ")\\}\\{',><")
                lines = [l[::-1].translate(rev_map) for l in lines]

            for i, line in enumerate(lines):
                self.draw_str(ground_y - 3 + i, x, line)

            self.stdscr.refresh()
            timer += 1
            time.sleep(0.15)

    def run(self):
        while True:
            self.draw_menu()

            key = self.stdscr.getch()
            if key == -1:
                time.sleep(0.05)
                continue

            if key == curses.KEY_UP:
                if self.selected_idx > 0:
                    self.selected_idx -= 1
            elif key == curses.KEY_DOWN:
                if self.selected_idx < len(self.savers) - 1:
                    self.selected_idx += 1
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                if self.selected_idx == 5:
                    break
                else:
                    self.run_saver(self.selected_idx)

def main(stdscr):
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)

    app = ScreensaverApp(stdscr)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
