"""
GameStatusDisplay - Komponente für die Spielstandsanzeige.
Zeigt Modus, Match-Zähler, Runden-Zähler, Phase und Spielerstats an.
Reserviert die oberen 10% des Bildschirms.
"""

import pygame
from typing import Optional, Dict, Any
from core.utils.global_constants import COLORS


class GameStatusDisplay:
    """
    Anzeige für den aktuellen Spielstand.
    
    Position: Obere 10% des Screens
    Inhalt:
    - Modus (String), Match-Count (Int), Round-Count (Int), Phase (String)
    - Spieler: idle_count, might, matches_won
    - Gegner: idle_count, might, matches_won
    
    Layout:
    [Leer für Buttons][   SPIELSTAND   ][Leer für Buttons]
    """

    def __init__(self, width: int, height: int):
        """
        Initialisiert die Spielstandsanzeige.
        
        Args:
            width: Bildschirmbreite
            height: Bildschirmhöhe
        """
        self.width = width
        self.height = height
        self.status_height = int(height * 0.1)  # 10% der Höhe
        self.y = 0  #Beginnt ganz oben
        
        # Standardwerte
        self.game_data = {
            "modus": "Single Match",
            "match_count": "1/1",
            "round_count": 0,
            "phase": "Initialisierung",
            "player": {
                "idle_count": 0,
                "might": 0,
                "matches_won": 0
            },
            "opponent": {
                "idle_count": 0,
                "might": 0,
                "matches_won": 0
            }
        }
        
        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 20, bold=True)
        self.stat_font = pygame.font.SysFont("Courier New", 16)
        
        # Abstände
        self.margin = 10
        self.settings_button_width = 60  # Platz für Settings-Button rechts
        self.action_button_width = 100  # Platz für Action-Button rechts

    def update(self, **kwargs) -> None:
        """
        Aktualisiert die Spielstandsdaten.
        
        Args:
            modus: String (z.B. "Single Match", "Best of 4")
            match_count: String (z.B. "1/4")
            round_count: Integer
            phase: String
            player: Dict mit idle_count, might, matches_won
            opponent: Dict mit idle_count, might, matches_won
        """
        for key, value in kwargs.items():
            if key in self.game_data:
                self.game_data[key] = value
            elif key in ["player", "opponent"] and isinstance(value, dict):
                self.game_data[key].update(value)

    def render(self, surface: pygame.Surface) -> None:
        """
        Rendert die Spielstandsanzeige auf der Oberfläche.
        
        Args:
            surface: Pygame-Oberfläche zum Zeichnen
        """
        # Hintergrund der Statusleiste
        status_rect = pygame.Rect(
            0, 
            self.y, 
            self.width, 
            self.status_height
        )
        pygame.draw.rect(surface, COLORS["background"], status_rect)
        pygame.draw.rect(surface, COLORS["primary"], status_rect, 1)
        
        # Berechne verfügbare Breite (ohne Button-Bereiche links/rechts)
        # Links: 10px Margin, Rechts: Platz für Buttons
        left_margin = self.margin
        right_margin = self.margin + self.settings_button_width + self.action_button_width
        available_width = self.width - left_margin - right_margin
        
        # --- Titel "SPIELSTAND" zentriert oben ---
        title_text = "SPIELSTAND"
        title_surface = self.title_font.render(title_text, True, COLORS["highlight"])
        title_x = self.width // 2 - title_surface.get_width() // 2
        surface.blit(title_surface, (title_x, self.y + 5))
        
        # --- Erste Zeile: Modus, Match, Runde, Phase ---
        line1_parts = [
            f"Modus: {self.game_data['modus']}",
            f"Match: {self.game_data['match_count']}",
            f"Runde: {self.game_data['round_count']}",
            f"Phase: {self.game_data['phase']}"
        ]
        line1_text = " | ".join(line1_parts)
        line1_surface = self.stat_font.render(line1_text, True, COLORS["text"])
        line1_x = left_margin + 10
        line1_y = self.y + 30
        surface.blit(line1_surface, (line1_x, line1_y))
        
        # --- Zweite Zeile: SpielerStats ---
        player_text = (f"Spieler: Idle={self.game_data['player']['idle_count']} | "
                      f"Might={self.game_data['player']['might']} | "
                      f"Siege={self.game_data['player']['matches_won']}")
        player_surface = self.stat_font.render(player_text, True, COLORS["text"])
        player_x = left_margin + 10
        player_y = line1_y + 20
        surface.blit(player_surface, (player_x, player_y))
        
        # --- Dritte Zeile: GegnerStats ---
        opponent_text = (f"Gegner:  Idle={self.game_data['opponent']['idle_count']} | "
                       f"Might={self.game_data['opponent']['might']} | "
                       f"Siege={self.game_data['opponent']['matches_won']}")
        opponent_surface = self.stat_font.render(opponent_text, True, COLORS["text"])
        opponent_x = left_margin + 10
        opponent_y = player_y + 20
        surface.blit(opponent_surface, (opponent_x, opponent_y))
