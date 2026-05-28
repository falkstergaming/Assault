"""
Game Controller für Sturm auf Grayskull.
Verarbeitet Spielerinput (Tasten, Zahleneingabe) und leitet Aktionen weiter.
"""

import pygame
from pygame.locals import *
from typing import Optional, Callable, Dict

class GameController:
    """
    Verwaltet die Eingabe und leitet Aktionen an das Spiel weiter.
    """

    def __init__(self):
        """Initialisiert den Controller."""
        self.input_buffer = ""  # Für Zahleneingabe
        self.callbacks: Dict[int, Callable] = {}  # Tasten-Callbacks
        self.number_callback: Optional[Callable[[int], None]] = None  # Callback für Zahleneingabe

    def handle_input(self) -> None:
        """
        Verarbeitet alle Pygame-Events (Tasten, Maus).
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                return  # Wird in der Hauptschleife behandelt

            elif event.type == KEYDOWN:
                # Zahleneingabe (0-9)
                if event.unicode.isdigit():
                    self.input_buffer += event.unicode
                # Backspace für Löschen
                elif event.key == K_BACKSPACE:
                    self.input_buffer = self.input_buffer[:-1]
                # Enter für Bestätigung der Zahleneingabe
                elif event.key == K_RETURN and self.input_buffer:
                    if self.number_callback:
                        try:
                            number = int(self.input_buffer)
                            self.number_callback(number)
                        except ValueError:
                            pass
                        self.input_buffer = ""
                # Tasten-Callbacks (1-9, ESC, etc.)
                elif event.key in self.callbacks:
                    self.callbacks[event.key]()

    def register_key_callback(self, key: int, callback: Callable) -> None:
        """
        Registriert einen Callback für eine Taste.

        Args:
            key: Pygame-Tastenkonstante (z. B. K_1, K_ESCAPE).
            callback: Funktion, die aufgerufen wird, wenn die Taste gedrückt wird.
        """
        self.callbacks[key] = callback

    def register_number_callback(self, callback: Callable[[int], None]) -> None:
        """
        Registriert einen Callback für Zahleneingaben.

        Args:
            callback: Funktion, die mit der eingegebenen Zahl aufgerufen wird.
        """
        self.number_callback = callback

    def get_input_buffer(self) -> str:
        """Gibt den aktuellen Eingabepuffer zurück (für Anzeige)."""
        return self.input_buffer