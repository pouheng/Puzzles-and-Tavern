import pygame
from ui.fonts import get_font
from config import *


class TabBar:
    def __init__(self, tabs, x, y, width, height):
        self.tabs = tabs
        self.active_tab = 0
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tab_width = width // len(tabs)
        self.tab_rects = []
        self._create_rects()

    def _create_rects(self):
        self.tab_rects = []
        for i in range(len(self.tabs)):
            rect = pygame.Rect(
                self.x + i * self.tab_width, self.y, self.tab_width, self.height
            )
            self.tab_rects.append(rect)

    def handle_click(self, pos):
        for i, rect in enumerate(self.tab_rects):
            if rect.collidepoint(pos):
                self.active_tab = i
                return True
        return False

    def get_active_tab(self):
        return self.tabs[self.active_tab][0]

    def draw(self, screen):
        for i, (tab_name, tab_icon) in enumerate(self.tabs):
            rect = self.tab_rects[i]

            if i == self.active_tab:
                pygame.draw.rect(screen, (80, 80, 100), rect)
                pygame.draw.line(
                    screen,
                    (200, 180, 100),
                    (rect.left, rect.bottom - 3),
                    (rect.right, rect.bottom - 3),
                    4,
                )
            else:
                pygame.draw.rect(screen, (50, 50, 60), rect)

            font = get_font(28)
            text = font.render(
                tab_name,
                True,
                (255, 255, 255) if i == self.active_tab else (150, 150, 150),
            )
            text_rect = text.get_rect(center=(rect.centerx, rect.centery))
            screen.blit(text, text_rect)
