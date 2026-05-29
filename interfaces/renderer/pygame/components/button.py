import pygame
from typing import Optional, Callable
from core.utils.global_constants import COLORS, FACTION_COLORS

class Button:
    """Button-Klasse für das Spiel (z. B. Action-Button, Settings-Button)."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str = "",
        symbol: Optional[pygame.Surface] = None,  # Symbol (z. B. Pygame-Surface für ein Icon)
        callback: Optional[Callable] = None,     # Funktion, die beim Klick aufgerufen wird
        highlight_color: tuple = COLORS["highlight"],  # Farb-Highlight
        base_color: tuple = COLORS["primary"],        # Standardfarbe
        text_color: tuple = COLORS["text"],           # Textfarbe
        font_size: int = 20,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.symbol = symbol
        self.callback = callback
        self.highlight_color = highlight_color
        self.base_color = base_color
        self.text_color = text_color
        self.font = pygame.font.SysFont("Arial", font_size)
        self.rect = pygame.Rect(x, y, width, height)
        self.is_highlighted = False

    def render(self, surface: pygame.Surface):
        """Zeichnet den Button auf der Oberfläche."""
        # Hintergrund (mit Highlight)
        color = self.highlight_color if self.is_highlighted else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, COLORS["text"], self.rect, 2, border_radius=5)  # Rahmen

        # Symbol (falls vorhanden)
        if self.symbol:
            symbol_rect = self.symbol.get_rect(center=self.rect.center)
            surface.blit(self.symbol, symbol_rect)

        # Text (falls vorhanden)
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            if self.symbol:
                text_rect.y += self.height // 4  # Text unter dem Symbol
            surface.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Behandelt Maus-Events (Highlighting, Klicks). Gibt True zurück, wenn der Button geklickt wurde."""
        if event.type == pygame.MOUSEMOTION:
            self.is_highlighted = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Linksklick
            if self.rect.collidepoint(event.pos) and self.callback:
                self.callback()
                return True
        return False

    def set_highlight(self, highlighted: bool):
        """Setzt den Highlight-Status manuell."""
        self.is_highlighted = highlighted