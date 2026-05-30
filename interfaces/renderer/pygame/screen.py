import pygame
import os
from pathlib import Path
from typing import List
from core.utils.global_constants import COLORS
from interfaces.renderer.pygame.components.button import HexButton

class Screen:
    """Verwaltet das Pygame-Fenster, Hintergrundbild, Hex-Buttons und Text-Rendering."""

    def __init__(self, width: int = 1280, height: int = 720):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Sturm auf Grayskull")
        self.background = None
        self.buttons: List[HexButton] = []  # Hex-Buttons
        self.font = pygame.font.SysFont("Courier New", 16)  # ✅ Font für draw_text
        self._load_background()

    def _load_background(self) -> None:
        """Lädt ein Hintergrundbild (JPG) aus dem artwork/-Ordner."""
        artwork_dir = Path("interfaces/renderer/pygame/artwork")
        if artwork_dir.exists():
            for jpg_file in artwork_dir.glob("*.jpg"):
                try:
                    self.background = pygame.image.load(str(jpg_file)).convert()
                    if self.background.get_size() != (self.width, self.height):
                        self.background = pygame.transform.scale(self.background, (self.width, self.height))
                    print(f"Geladenes Hintergrundbild: {jpg_file.name}")
                    break
                except Exception as e:
                    print(f"Fehler beim Laden von {jpg_file}: {e}")

    def draw_text(self, text: str, x: int, y: int, color: tuple = COLORS["text"]):
        """Zeichnet Text auf dem Bildschirm mit globaler Farbe."""
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def add_button(self, button: HexButton):
        """Fügt einen HexButton hinzu."""
        self.buttons.append(button)

    def render(self) -> None:
        """Rendert Hintergrund, Hex-Buttons und andere UI-Elemente."""
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(COLORS["background"])

        # Hex-Buttons rendern
        for button in self.buttons:
            button.render(self.screen)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Behandelt Events für Hex-Buttons. Gibt True zurück, wenn ein Button geklickt wurde."""
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False

    def get_surface(self) -> pygame.Surface:
        """Gibt die Pygame-Oberfläche zurück."""
        return self.screen