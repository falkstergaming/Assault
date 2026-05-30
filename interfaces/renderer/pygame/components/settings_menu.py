"""
Settings-Menü für Sturm auf Grayskull.
Kontextmenü für Spracheinstellungen und Audio-Lautstärke.
"""

import pygame
from pygame.locals import *
from typing import Optional, Callable
from core.utils.global_constants import COLORS
from core.utils.settings import Settings


class SettingsMenu:
    """
    Kontextmenü für Einstellungen.
    Wird beim Klick auf den Settings-Button angezeigt.
    
    Enthält:
    - Sprache: Deutsch/Englisch (Radio-Buttons)
    - Musik-Lautstärke: Schieberegler 0-100%
    - Effekt-Lautstärke: Schieberegler 0-100%
    """

    def __init__(self, x: int, y: int, width: int = 300, settings: Optional[Settings] = None):
        """
        Initialisiert das Settings-Menü.
        
        Args:
            x: X-Position (linker Rand des Menüs)
            y: Y-Position (oberer Rand des Menüs)
            width: Breite des Menüs
            settings: Settings-Instanz für Speicherung
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = 250  # feste Höhe
        self.settings = settings if settings else Settings()
        self.is_active = False
        self.font = pygame.font.SysFont("Arial", 14)
        self.font_title = pygame.font.SysFont("Arial", 16, bold=True)
        
        # UI-Elemente Dimensionen
        self.padding = 15
        self.line_height = 30
        self.slider_width = 150
        self.slider_height = 10
        
        # Aktive Schieberegler
        self.active_slider = None  # "music" oder "effect"

    def toggle(self) -> None:
        """Schaltet das Menü ein/aus."""
        self.is_active = not self.is_active

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Behandelt Events für das Settings-Menü.
        Gibt True zurück, wenn das Event verbraucht wurde.
        """
        if not self.is_active:
            return False

        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Linksklick
                mouse_pos = pygame.mouse.get_pos()
                
                # Prüfe Sprachauswahl
                if self._is_language_clicked(mouse_pos):
                    # Sprache umschalten
                    new_lang = "de" if self.settings.language == "en" else "en"
                    self.settings.language = new_lang
                    return True
                
                # Prüfe Musik-Lautstärke Schieberegler
                if self._is_slider_clicked(mouse_pos, "music"):
                    self.active_slider = "music"
                    self._update_slider_value(mouse_pos, "music")
                    return True
                
                # Prüfe Effekt-Lautstärke Schieberegler
                if self._is_slider_clicked(mouse_pos, "effect"):
                    self.active_slider = "effect"
                    self._update_slider_value(mouse_pos, "effect")
                    return True
                
                # Klick außerhalb des Menüs = Menü schließen
                if not self._is_inside_menu(mouse_pos):
                    self.is_active = False
                    return True
                
                return True

            return False

        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.active_slider = None
            return False

        elif event.type == MOUSEMOTION:
            if self.active_slider and pygame.mouse.get_pressed()[0]:
                self._update_slider_value(pygame.mouse.get_pos(), self.active_slider)
                return True
            return False

        return False

    def _is_inside_menu(self, pos: tuple) -> bool:
        """Prüft, ob die Position innerhalb des Menüs ist."""
        return (self.x <= pos[0] <= self.x + self.width and
                self.y <= pos[1] <= self.y + self.height)

    def _is_language_clicked(self, pos: tuple) -> bool:
        """Prüft, ob die Sprachauswahl angeklickt wurde."""
        lang_x = self.x + self.padding
        lang_y = self.y + self.padding
        lang_width = self.width - 2 * self.padding
        lang_height = self.line_height
        return (lang_x <= pos[0] <= lang_x + lang_width and
                lang_y <= pos[1] <= lang_y + lang_height)

    def _is_slider_clicked(self, pos: tuple, slider_type: str) -> bool:
        """Prüft, ob ein Schieberegler angeklickt wurde."""
        if slider_type == "music":
            slider_y = self.y + self.padding + self.line_height * 2 + 10
        else:  # effect
            slider_y = self.y + self.padding + self.line_height * 4 + 10
        
        slider_x = self.x + self.padding
        return (slider_x <= pos[0] <= slider_x + self.slider_width and
                slider_y <= pos[1] <= slider_y + self.slider_height)

    def _update_slider_value(self, pos: tuple, slider_type: str) -> None:
        """Aktualisiert den Schieberegler-Wert basierend auf der Mausposition."""
        slider_x = self.x + self.padding
        # Berechne prozentualen Wert (0-100)
        relative_x = max(0, min(self.slider_width, pos[0] - slider_x))
        percentage = int((relative_x / self.slider_width) * 100)
        
        if slider_type == "music":
            self.settings.music_volume = percentage
        elif slider_type == "effect":
            self.settings.effect_volume = percentage

    def render(self, surface: pygame.Surface) -> None:
        """Zeichnet das Settings-Menü."""
        if not self.is_active:
            return

        # Menü-Hintergrund
        menu_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, COLORS["background"], menu_rect)
        pygame.draw.rect(surface, COLORS["primary"], menu_rect, 2)

        # Titel
        title = self.font_title.render("Settings", True, COLORS["highlight"])
        surface.blit(title, (self.x + self.padding, self.y + 5))

        # --- Sprache ---
        lang_y = self.y + self.padding + self.line_height
        lang_label = self.font.render("Language:", True, COLORS["text"])
        surface.blit(lang_label, (self.x + self.padding, lang_y))

        # Sprachauswahl (Deutsch/Englisch)
        lang_value = "German" if self.settings.language == "de" else "English"
        lang_value_text = self.font.render(lang_value, True, COLORS["highlight"])
        lang_value_x = self.x + self.width - self.padding - lang_value_text.get_width()
        surface.blit(lang_value_text, (lang_value_x, lang_y))

        # --- Musik-Lautstärke ---
        music_y = lang_y + self.line_height + 5
        music_label = self.font.render("Music Volume:", True, COLORS["text"])
        surface.blit(music_label, (self.x + self.padding, music_y))
        self._draw_slider(surface, self.x + self.padding, music_y + self.line_height - 5, 
                         self.settings.music_volume, "music")
        music_percent = self.font.render(f"{self.settings.music_volume}%", True, COLORS["text"])
        surface.blit(music_percent, (self.x + self.padding + self.slider_width + 10, music_y + 5))

        # --- Effekt-Lautstärke ---
        effect_y = music_y + self.line_height + 10
        effect_label = self.font.render("Effect Volume:", True, COLORS["text"])
        surface.blit(effect_label, (self.x + self.padding, effect_y))
        self._draw_slider(surface, self.x + self.padding, effect_y + self.line_height - 5,
                         self.settings.effect_volume, "effect")
        effect_percent = self.font.render(f"{self.settings.effect_volume}%", True, COLORS["text"])
        surface.blit(effect_percent, (self.x + self.padding + self.slider_width + 10, effect_y + 5))

    def _draw_slider(self, surface: pygame.Surface, x: int, y: int, value: int, slider_type: str) -> None:
        """Zeichnet einen Schieberegler."""
        # Hintergrund
        pygame.draw.rect(surface, COLORS["secondary"], 
                        (x, y, self.slider_width, self.slider_height), 0, 5)
        
        # Füllstand
        fill_width = int((value / 100) * self.slider_width)
        if fill_width > 0:
            pygame.draw.rect(surface, COLORS["primary"],
                           (x, y, fill_width, self.slider_height), 0, 5)
        
        # Regler-Knopf
        knob_x = x + fill_width - 5
        pygame.draw.circle(surface, COLORS["highlight"], (knob_x + 5, y + 5), 8)
