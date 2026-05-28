"""
Text-Konsole für Pygame.
Zeigt Log-Meldungen im Spiel an und nutzt Farben aus global_constants.
"""

import pygame
from core.utils.global_constants import COLORS
from core.utils.global_constants import FONT_CONSOLE

class Console:
    """
    Eine Text-Konsole für Debug-Ausgaben im Spiel.
    """

    def __init__(self, x: int, y: int, width: int, height: int, max_lines: int = 15):
        """
        Initialisiert die Konsole.

        Args:
            x: X-Position.
            y: Y-Position.
            width: Breite.
            height: Höhe.
            max_lines: Maximale Anzahl an Zeilen.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_lines = max_lines
        self.lines = []  # Liste von (text, color)-Tuples
        self.font = pygame.font.SysFont(*FONT_CONSOLE)  #  Nutzt globale Konstante

    def log(self, text: str, color: tuple = COLORS["text"]):
        """Fügt eine neue Zeile zur Konsole hinzu."""
        self.lines.append((text, color))
        if len(self.lines) > self.max_lines:
            self.lines.pop(0)  # Entfernt die älteste Zeile

    def clear(self):
        """Löscht die Konsole."""
        self.lines = []

    def render(self, surface: pygame.Surface):
        """Zeichnet die Konsole auf die Oberfläche."""
        # Hintergrund (aus global_constants)
        pygame.draw.rect(surface, COLORS["background"], (self.x, self.y, self.width, self.height))
        # Rahmen (aus global_constants)
        pygame.draw.rect(surface, COLORS["primary"], (self.x, self.y, self.width, self.height), 1)

        # Text zeilenweise ausgeben
        for i, (line, color) in enumerate(self.lines):
            text_surface = self.font.render(line, True, color)
            surface.blit(text_surface, (self.x + 10, self.y + 10 + i * 20))