# pygame_client/ui_elements.py
import pygame

pygame.font.init()

# Definisi Warna dari style.css
COLOR_PRIMARY = (0, 123, 255)
COLOR_SUCCESS = (40, 167, 69)
COLOR_DANGER = (220, 53, 69)
COLOR_WARNING = (255, 193, 7)
COLOR_INFO = (23, 162, 184)
COLOR_LIGHT_GRAY = (204, 204, 204)
COLOR_DARK_GRAY = (52, 58, 64)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_TABLE_BG = (240, 248, 255)

# Fonts
FONT_NORMAL = pygame.font.SysFont("Segoe UI", 24)
FONT_BOLD = pygame.font.SysFont("Segoe UI", 24, bold=True)
FONT_CARD = pygame.font.SysFont("Segoe UI", 30, bold=True)
FONT_SMALL = pygame.font.SysFont("Segoe UI", 18)

class Button:
    def __init__(self, x, y, width, height, text, color=COLOR_PRIMARY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_surf = FONT_BOLD.render(text, True, COLOR_WHITE)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        self.disabled = False

    def draw(self, screen):
        color = COLOR_LIGHT_GRAY if self.disabled else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        screen.blit(self.text_surf, self.text_rect)

    def is_clicked(self, event):
        return not self.disabled and event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

class Card:
    def __init__(self, x, y, text, is_selected=False, is_helper=False):
        self.rect = pygame.Rect(x, y, 100, 70)
        self.text = text
        self.is_selected = is_selected
        self.is_helper = is_helper
        self.text_surf = FONT_CARD.render(text, True, COLOR_DARK_GRAY)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
    
    def draw(self, screen):
        if self.is_selected:
            bg_color = (255, 190, 187) # Merah muda
            border_color = COLOR_DANGER
        elif self.is_helper:
            bg_color = COLOR_SUCCESS
            border_color = (30, 126, 52)
        else:
            bg_color = COLOR_WARNING
            border_color = (224, 168, 0)

        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=8)
        screen.blit(self.text_surf, self.text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

class TextInputBox:
    def __init__(self, x, y, width, height, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
    
    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_WHITE, self.rect)
        pygame.draw.rect(screen, COLOR_DARK_GRAY if self.active else COLOR_LIGHT_GRAY, self.rect, 2, border_radius=6)
        
        if self.text:
            text_surf = FONT_NORMAL.render(self.text, True, COLOR_BLACK)
        else:
            text_surf = FONT_NORMAL.render(self.placeholder, True, COLOR_LIGHT_GRAY)
        
        screen.blit(text_surf, (self.rect.x + 10, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))