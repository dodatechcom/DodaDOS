import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
import time

# Retro Color Palette (inspired by GEM / Windows 3.1)
COLOR_DESKTOP = (0, 128, 128)      # Teal background
COLOR_WINDOW_BG = (192, 192, 192)  # Light gray
COLOR_TITLEBAR_ACTIVE = (0, 0, 128)# Dark blue
COLOR_TITLEBAR_INACTIVE = (128, 128, 128) # Gray
COLOR_TEXT_WHITE = (255, 255, 255)
COLOR_TEXT_BLACK = (0, 0, 0)
COLOR_BORDER_LIGHT = (255, 255, 255)
COLOR_BORDER_DARK = (128, 128, 128)

class Icon:
    def __init__(self, name, x, y, action):
        self.name = name
        self.rect = pygame.Rect(x, y, 64, 64)
        self.action = action
        self.selected = False

    def draw(self, surface, font):
        # Draw a simple box as an icon placeholder
        icon_box = (self.rect.x + 16, self.rect.y + 4, 32, 32)
        color = (0, 0, 128) if self.selected else (255, 255, 0)
        pygame.draw.rect(surface, color, icon_box)
        pygame.draw.rect(surface, COLOR_TEXT_WHITE, icon_box, 2)

        # Draw text
        text_color = COLOR_TEXT_WHITE if not self.selected else (255, 255, 0)
        text_bg = (0, 0, 128) if self.selected else None

        text_surf = font.render(self.name, True, text_color, text_bg)
        text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.bottom - 10))
        surface.blit(text_surf, text_rect)

class Window:
    def __init__(self, title, x, y, width, height, content_func=None):
        self.title = title
        self.rect = pygame.Rect(x, y, width, height)
        self.content_func = content_func

        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.close_rect = pygame.Rect(0, 0, 16, 14)
        self.update_rects()

    def update_rects(self):
        self.title_rect = pygame.Rect(self.rect.x + 3, self.rect.y + 3, self.rect.width - 6, 18)
        self.close_rect.topleft = (self.rect.right - 20, self.rect.y + 5)
        self.content_rect = pygame.Rect(self.rect.x + 3, self.rect.y + 24, self.rect.width - 6, self.rect.height - 27)

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.update_rects()

    def draw(self, desktop, is_active):
        # Window Border and BG
        desktop.draw_3d_rect(desktop.screen, COLOR_WINDOW_BG, self.rect, raised=True)

        # Title Bar
        title_color = COLOR_TITLEBAR_ACTIVE if is_active else COLOR_TITLEBAR_INACTIVE
        pygame.draw.rect(desktop.screen, title_color, self.title_rect)

        # Title Text
        title_surf = desktop.title_font.render(self.title, True, COLOR_TEXT_WHITE)
        desktop.screen.blit(title_surf, (self.title_rect.x + 4, self.title_rect.y + 2))

        # Close Button
        desktop.draw_3d_rect(desktop.screen, COLOR_WINDOW_BG, self.close_rect, raised=True)
        # Draw 'X' inside close button
        pygame.draw.line(desktop.screen, COLOR_TEXT_BLACK, (self.close_rect.x+3, self.close_rect.y+3), (self.close_rect.right-4, self.close_rect.bottom-4), 2)
        pygame.draw.line(desktop.screen, COLOR_TEXT_BLACK, (self.close_rect.right-4, self.close_rect.y+3), (self.close_rect.x+3, self.close_rect.bottom-4), 2)

        # Content Area
        # desktop.draw_3d_rect(desktop.screen, COLOR_TEXT_WHITE, self.content_rect, raised=False)
        pygame.draw.rect(desktop.screen, COLOR_TEXT_WHITE, self.content_rect)
        pygame.draw.rect(desktop.screen, COLOR_BORDER_DARK, self.content_rect, 1)

        if self.content_func:
            self.content_func(desktop.screen, self.content_rect, desktop.font)


class Desktop:
    def __init__(self, width=640, height=480):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Doda GUI Shell")
        self.clock = pygame.time.Clock()
        self.running = True

        # Load a retro font if possible, else default
        try:
            self.font = pygame.font.SysFont("courier", 14, bold=True)
            self.title_font = pygame.font.SysFont("arial", 14, bold=True)
        except Exception:
            self.font = pygame.font.Font(None, 20)
            self.title_font = pygame.font.Font(None, 20)

        self.windows = []
        self.icons = []
        self.setup_desktop()

    def setup_desktop(self):
        # Create Desktop Icons
        self.icons.append(Icon("About", 20, 20, self.open_about))
        self.icons.append(Icon("SysInfo", 20, 100, self.open_sysinfo))
        self.icons.append(Icon("Clock", 20, 180, self.open_clock))

        # Double click state tracking
        self.last_click_time = 0
        self.last_clicked_icon = None

    # --- Built-in Apps ---
    def open_about(self):
        def render_about(surface, rect, font):
            lines = [
                "Doda GUI Shell v1.0",
                "",
                "A lightweight, retro graphical",
                "environment for DOS-like systems.",
                "",
                "Built with Python & Pygame."
            ]
            for i, line in enumerate(lines):
                surf = font.render(line, True, COLOR_TEXT_BLACK)
                surface.blit(surf, (rect.x + 10, rect.y + 10 + (i * 20)))

        w = Window("About Doda", 200, 150, 300, 200, render_about)
        self.windows.append(w)

    def open_sysinfo(self):
        def render_sysinfo(surface, rect, font):
            try:
                import doda_hw
                info = doda_hw.gather_all_info()
                cpu = info['cpu']
                mem = info['mem']

                lines = [
                    "Hardware Information",
                    "-"*20,
                    f"CPU: {cpu['model'][:25]}...",
                    f"Cores: {cpu['cores']} / Threads: {cpu['threads']}",
                    "",
                    f"Memory Total: {doda_hw.format_bytes(mem['total'])}",
                    f"Memory Avail: {doda_hw.format_bytes(mem['available'])}",
                ]
            except Exception as e:
                lines = ["Error loading doda_hw:", str(e)]

            for i, line in enumerate(lines):
                surf = font.render(line, True, COLOR_TEXT_BLACK)
                surface.blit(surf, (rect.x + 10, rect.y + 10 + (i * 20)))

        w = Window("System Info", 250, 100, 350, 250, render_sysinfo)
        self.windows.append(w)

    def open_clock(self):
        def render_clock(surface, rect, font):
            import datetime
            now = datetime.datetime.now().strftime("%H:%M:%S")
            # Draw big text
            big_font = pygame.font.SysFont("arial", 32, bold=True)
            surf = big_font.render(now, True, COLOR_TEXT_BLACK)
            tr = surf.get_rect(center=rect.center)
            surface.blit(surf, tr)

        w = Window("Clock", 300, 200, 200, 100, render_clock)
        self.windows.append(w)
    # -----------------------

    def draw_3d_rect(self, surface, color, rect, raised=True):
        pygame.draw.rect(surface, color, rect)
        c_topleft = COLOR_BORDER_LIGHT if raised else COLOR_BORDER_DARK
        c_bottomright = COLOR_BORDER_DARK if raised else COLOR_BORDER_LIGHT

        # Top and Left lines
        pygame.draw.line(surface, c_topleft, (rect[0], rect[1]), (rect[0] + rect[2] - 1, rect[1]))
        pygame.draw.line(surface, c_topleft, (rect[0], rect[1]), (rect[0], rect[1] + rect[3] - 1))
        # Bottom and Right lines
        pygame.draw.line(surface, c_bottomright, (rect[0], rect[1] + rect[3] - 1), (rect[0] + rect[2] - 1, rect[1] + rect[3] - 1))
        pygame.draw.line(surface, c_bottomright, (rect[0] + rect[2] - 1, rect[1]), (rect[0] + rect[2] - 1, rect[1] + rect[3] - 1))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    # Check windows (reverse order to get topmost first)
                    clicked_window = None
                    for w in reversed(self.windows):
                        if w.close_rect.collidepoint(event.pos):
                            self.windows.remove(w)
                            clicked_window = True
                            break
                        elif w.title_rect.collidepoint(event.pos):
                            w.is_dragging = True
                            w.drag_offset_x = w.rect.x - event.pos[0]
                            w.drag_offset_y = w.rect.y - event.pos[1]
                            clicked_window = w
                            break
                        elif w.rect.collidepoint(event.pos):
                            clicked_window = w
                            break

                    if clicked_window and clicked_window is not True:
                        # Move to front
                        self.windows.remove(clicked_window)
                        self.windows.append(clicked_window)

                    if not clicked_window:
                        # Check icons if no window was clicked
                        for icon in self.icons:
                            if icon.rect.collidepoint(event.pos):
                                icon.selected = True
                            else:
                                icon.selected = False

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for w in self.windows:
                        w.is_dragging = False

            elif event.type == pygame.MOUSEMOTION:
                # Handle window dragging
                if self.windows:
                    active_w = self.windows[-1]
                    if active_w.is_dragging:
                        new_x = event.pos[0] + active_w.drag_offset_x
                        new_y = event.pos[1] + active_w.drag_offset_y
                        active_w.move(new_x - active_w.rect.x, new_y - active_w.rect.y)

                # Basic double-click simulation for icons
                now = time.time()
                for icon in self.icons:
                    if icon.rect.collidepoint(event.pos):
                        if icon == self.last_clicked_icon and (now - self.last_click_time) < 0.5:
                            # Double click!
                            icon.action()
                            icon.selected = False
                        self.last_clicked_icon = icon
                        self.last_click_time = now

    def update(self):
        pass

    def draw(self):
        self.screen.fill(COLOR_DESKTOP)

        # Draw Icons
        for icon in self.icons:
            icon.draw(self.screen, self.font)

        # Draw Windows (back to front)
        for i, w in enumerate(self.windows):
            is_active = (i == len(self.windows) - 1)
            w.draw(self, is_active)

        # Draw Taskbar (Bottom)
        taskbar_rect = (0, self.height - 24, self.width, 24)
        self.draw_3d_rect(self.screen, COLOR_WINDOW_BG, taskbar_rect, raised=True)

        # Start button
        start_rect = (2, self.height - 22, 60, 20)
        self.draw_3d_rect(self.screen, COLOR_WINDOW_BG, start_rect, raised=True)
        start_surf = self.font.render("DODA", True, COLOR_TEXT_BLACK)
        self.screen.blit(start_surf, (start_rect[0] + 12, start_rect[1] + 4))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    app = Desktop()
    app.run()
