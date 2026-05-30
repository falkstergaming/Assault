"""
GameStatusDisplay - Komponente für die Spielstandsanzeige.
Zeigt Modus, Match-Zähler, Runden-Zähler, Phase und Spielerstats an.
Reserviert die oberen 15% des Bildschirms mit 25px Rand und 10% Platz links/rechts.
"""

import pygame
from typing import Optional, Dict, Any, TYPE_CHECKING
from core.utils.global_constants import COLORS
from core.utils.translations import TRANSLATIONS, get_translation

if TYPE_CHECKING:
    from core.utils.settings import Settings


class GameStatusDisplay:
    """
    Anzeige für den aktuellen Spielstand.
    
    Position: Obere 15% des Screens, 25px Abstand zum Rand, 10% Platz links/rechts
    Inhalt:
    - Modus (String), Match-Count (Int), Round-Count (Int), Phase (String)
    - Spieler: idle_count, might, matches_won
    - Gegner: idle_count, might, matches_won
    
    Layout:
    [Leer für Buttons][   SPIELSTAND   ][Leer für Buttons]
    """

    def __init__(self, width: int, height: int, settings: Optional['Settings'] = None):
        """
        Initialisiert die Spielstandsanzeige.
        
        Args:
            width: Bildschirmbreite
            height: Bildschirmhöhe
            settings: Settings-Instanz für Sprachauswahl
        """
        self.width = width
        self.height = height
        self.status_height = int(height * 0.15)  # 15% der Höhe
        self.y = 25  # 25px Abstand zum oberen Rand
        self.margin_left = int(width * 0.1)  # 10% Platz links
        self.display_width = width - 2 * self.margin_left  # 80% der Breite
        self.x = self.margin_left
        self.settings = settings
        
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
        
        Layout:
        - Zeile 1: Titel + Spielstandsbezeichnung (z.B. "Sturm auf Grayskull // Spielstand")
        - Zeile 2: Modus, Match, Runde, Phase
        - Zeile 3: Gegner-Stats (oben)
        - Zeile 4: Spieler-Stats (unten)
        
        Args:
            surface: Pygame-Oberfläche zum Zeichnen
        """
        # Hintergrund der Statusleiste (mit Randabstand)
        status_rect = pygame.Rect(
            self.x,
            self.y,
            self.display_width,
            self.status_height
        )
        pygame.draw.rect(surface, COLORS["background"], status_rect)
        pygame.draw.rect(surface, COLORS["primary"], status_rect, 1)
        
        # --- Sprache festlegen ---
        lang = self.settings.language if self.settings else "en"
        t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
        
        # --- Zeile 1: Titel + Spielstandsbezeichnung ---
        # Kombinierter Text: "Sturm auf Grayskull // Spielstand"
        title_text = f"{t['game_title']} // {t['stats_title']}"
        title_surface = self.title_font.render(title_text, True, COLORS["highlight"])
        title_x = self.x + 10
        title_y = self.y + 5
        surface.blit(title_surface, (title_x, title_y))
        
        # --- Zeile 2: Modus, Match, Runde, Phase ---
        line2_parts = [
            f"{t['mode']}: {self.game_data['modus']}",
            f"{t['match']}: {self.game_data['match_count']}",
            f"{t['round']}: {self.game_data['round_count']}",
            f"{t['phase']}: {self.game_data['phase']}"
        ]
        line2_text = " | ".join(line2_parts)
        line2_surface = self.stat_font.render(line2_text, True, COLORS["text"])
        line2_x = self.x + 20
        line2_y = title_y + 25
        surface.blit(line2_surface, (line2_x, line2_y))
        
        # --- Zeile 3: GegnerStats (oben) ---
        opponent_text = (f"{t['opponent']}: {t['idle']}={self.game_data['opponent']['idle_count']} | "
                       f"{t['might']}={self.game_data['opponent']['might']} | "
                       f"{t['wins']}={self.game_data['opponent']['matches_won']}")
        opponent_surface = self.stat_font.render(opponent_text, True, COLORS["text"])
        opponent_x = self.x + 20
        opponent_y = line2_y + 25
        surface.blit(opponent_surface, (opponent_x, opponent_y))
        
        # --- Zeile 4: SpielerStats (unten) ---
        player_text = (f"{t['player']}: {t['idle']}={self.game_data['player']['idle_count']} | "
                      f"{t['might']}={self.game_data['player']['might']} | "
                      f"{t['wins']}={self.game_data['player']['matches_won']}")
        player_surface = self.stat_font.render(player_text, True, COLORS["text"])
        player_x = self.x + 20
        player_y = opponent_y + 25
        surface.blit(player_surface, (player_x, player_y))
