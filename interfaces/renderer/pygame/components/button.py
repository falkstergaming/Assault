"""
Button-Klasse für hexagonale Buttons.
- Action-Button: Groß (size=80), rechts am Rand, mittig (für "Weiter").
- Settings-Button: Klein (size=50), oben rechts im Eck.
- BoardButton: Vorbereitung für Hexfelder des Spielfelds (interaktiv).
"""

from math import cos, sin, pi
from typing import List, Tuple, Optional, Callable
import pygame
from core.utils.global_constants import COLORS


class HexButton:
    """
    Basis-Klasse für ALLE hexagonalen Buttons im Spiel.
    - Präzise Kollisionserkennung (Point-in-Polygon).
    - Highlighting bei Mausüberfahrt.
    - Text und Symbol-Unterstützung.
    - Callback-Funktion bei Klick.
    
    Standardgrößen:
    - Action-Button: size=80 (rechts am Rand, mittig).
    - Settings-Button: size=50 (oben rechts im Eck).
    - BoardButton: size variabel (für Spielfeld-Hexfelder).
    """

    def __init__(
        self,
        x: int,
        y: int,
        size: int,          # Größe des Hexagons (Durchmesser)
        color: tuple,
        text: str = "",
        hex_id: Optional[str] = None,
        callback: Optional[Callable] = None,
        highlight_color: Optional[tuple] = None,
        symbol: Optional[pygame.Surface] = None,
        text_color: tuple = (0, 0, 0),  # Standard: Schwarz für bessere Sichtbarkeit
        font_size: int = 20,
    ):
        # Basis-Eigenschaften
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.text = text
        self.hex_id = hex_id
        self.callback = callback
        self.highlight_color = highlight_color if highlight_color else self._lighten_color(color, 30)
        self.symbol = symbol
        self.text_color = text_color
        self.font = pygame.font.SysFont("Arial", font_size)
        self.is_highlighted = False

        # Berechnete Eigenschaften
        self.center_x = x + size / 2
        self.center_y = y + size / 2
        self.points = self._calculate_hex_points()

    def _calculate_hex_points(self) -> List[Tuple[float, float]]:
        """Berechnet die 6 Eckpunkte des Hexagons (aus deinem alten Code)."""
        points = []
        for i in range(6):
            angle_deg = 60 * i
            angle_rad = pi / 180 * angle_deg
            point_x = self.center_x + self.size / 2 * cos(angle_rad)
            point_y = self.center_y + self.size / 2 * sin(angle_rad)
            points.append((point_x, point_y))
        return points

    def _lighten_color(self, color: tuple, factor: int = 30) -> tuple:
        """Hellt eine Farbe um `factor` auf (für Highlighting)."""
        r, g, b = color
        r = min(255, r + factor)
        g = min(255, g + factor)
        b = min(255, b + factor)
        return (r, g, b)

    def point_in_polygon(self, point: Tuple[float, float]) -> bool:
        """Point-in-Polygon-Test für präzise Hexagon-Kollisionserkennung."""
        x, y = point
        inside = False
        j = len(self.points) - 1
        for i in range(len(self.points)):
            if ((self.points[i][1] > y) != (self.points[j][1] > y) and
                x < (self.points[j][0] - self.points[i][0]) * (y - self.points[i][1]) / (self.points[j][1] - self.points[i][1]) + self.points[i][0]):
                inside = not inside
            j = i
        return inside

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Behandelt Maus-Events (Highlighting und Klicks). Gibt True zurück, wenn geklickt."""
        if event.type == pygame.MOUSEMOTION:
            self.is_highlighted = self.point_in_polygon(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.point_in_polygon(event.pos) and self.callback:
                self.callback()
                return True
        return False

    def render(self, surface: pygame.Surface):
        """Zeichnet den hexagonalen Button auf der Oberfläche."""
        color = self.highlight_color if self.is_highlighted else self.color
        pygame.draw.polygon(surface, color, self.points)
        pygame.draw.polygon(surface, COLORS["text"], self.points, 2)  # Rahmen

        # Symbol (falls vorhanden)
        if self.symbol:
            symbol_rect = self.symbol.get_rect(center=(self.center_x, self.center_y - 10))
            surface.blit(self.symbol, symbol_rect)

        # Text (falls vorhanden) - unterstützt Zeilenumbrüche
        if self.text:
            lines = self.text.split('\n')
            if len(lines) == 1:
                # Einfacher Text (zentriert)
                text_surface = self.font.render(self.text, True, self.text_color)
                text_rect = text_surface.get_rect(center=(self.center_x, self.center_y))
                surface.blit(text_surface, text_rect)
            else:
                # Multi-Line Text - zentriert in Hexagon
                y_offset = -6
                for line in lines:
                    text_surface = self.font.render(line, True, self.text_color)
                    text_rect = text_surface.get_rect(center=(self.center_x, self.center_y + y_offset))
                    surface.blit(text_surface, text_rect)
                    y_offset += 12  # Zeilenabstand (kleiner für 80px Hexfelder)