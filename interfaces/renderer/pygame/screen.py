"""
Screen-Modul für Pygame.
Lädt Hintergrundbilder (JPG) aus dem artwork/-Ordner und rendert UI-Elemente.
Nutzt Farben aus global_constants.
"""

import pygame
import os
from pathlib import Path
from typing import List
from core.utils.global_constants import COLORS
from core.utils.global_constants import FONT_CONSOLE
from interfaces.renderer.pygame.components.button import Button  # ✅ Importiere Button


class Screen:
    """
    Verwaltet das Pygame-Fenster und rendert UI-Elemente.
    Lädt automatisch JPG-Hintergrundbilder aus dem artwork/-Ordner.
    """

    def __init__(self, width: int = 1280, height: int = 720):
        """
        Initialisiert den Screen.

        Args:
            width: Breite des Fensters.
            height: Höhe des Fensters.
        """
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Sturm auf Grayskull")
        self.background = None
        self.font = pygame.font.SysFont(*FONT_CONSOLE)  # ✅ Font einmal erstellen
        self.buttons: List[Button] = []  # ✅ Liste für Buttons
        self._load_background()

    def _load_background(self) -> None:
        """Lädt ein Hintergrundbild (JPG) aus dem artwork/-Ordner."""
        artwork_dir = Path("interfaces/renderer/pygame/artwork")
        if artwork_dir.exists():
            for jpg_file in artwork_dir.glob("*.jpg"):
                try:
                    self.background = pygame.image.load(str(jpg_file)).convert()
                    # Skalieren, falls nötig
                    if self.background.get_size() != (self.width, self.height):
                        self.background = pygame.transform.scale(self.background, (self.width, self.height))
                    print(f"Geladenes Hintergrundbild: {jpg_file.name}")
                    break  # Nimmt das erste JPG
                except Exception as e:
                    print(f"Fehler beim Laden von {jpg_file}: {e}")
    
    def add_button(self, button: Button):
        """Fügt einen Button zur Screen hinzu."""
        self.buttons.append(button)

    def render(self) -> None:
        """Rendert den Hintergrund (oder Farbe aus global_constants)."""
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(COLORS["background"])  # Fallback: Farbe aus global_constants

        # ✅ Buttons rendern
        for button in self.buttons:
            button.render(self.screen)

    def draw_text(self, text: str, x: int, y: int, color: tuple = COLORS["text"]):
        """Zeichnet Text auf dem Bildschirm mit globaler Farbe."""
        text_surface = self.font.render(text, True, color)  # ✅ Font wiederverwenden
        self.screen.blit(text_surface, (x, y))

    def get_surface(self) -> pygame.Surface:
        """Gibt die Pygame-Oberfläche zurück (für Rendering durch andere Komponenten)."""
        return self.screen
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Behandelt Events für alle Buttons. Gibt True zurück, wenn ein Button geklickt wurde."""        
        for button in self.buttons:
         if button.handle_event(event):
            return True
        return False