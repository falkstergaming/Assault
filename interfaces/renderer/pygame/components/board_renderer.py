"""
BoardRenderer - Komponente für das Rendern des Spielfelds.
Zeichnet HexButtons für alle Board-Felder mit korrekten Positionen.

Positionen basieren auf dem alten POC (GlobalConstants.BOARD_POSITIONS).
"""

import pygame
from typing import Dict, Optional, Tuple
from core.game.board import Board
from core.utils.hex_id import HexID
from core.utils.global_constants import (
    COLORS, 
    FACTION_COLORS,
    HEX_SIZE,
    HEX_SPACING
)
from interfaces.renderer.pygame.components.button import HexButton


class BoardRenderer:
    """
    Rendert das Spielfeld mit HexButtons für alle Felder.
    
    - Erstellt HexButtons für 000x, 1xxx, 2xxx, 3xxx Felder
    - Zeigt Faction-Namen auf 0001/0002 an (Default: Adam/Skeletor)
    - Zeichnet Idle-Rahmen in Faction-Farbe wenn kontrolliert
    """

    # Relative Positionen (vom Zentrum aus) - aus altem POC
    # HEX_HORIZ_DISTANCE = 80 * 1.5 = 120
    # VERT_OFFSET = 80 * 0.25 = 20
    # BOARD_CENTER = (600, 400) für 1200x800 Screen
    # Für 1280x720 Screen: BOARD_CENTER = (640, 360)
    
    BOARD_POSITIONS = {
        # Faction Indicator (000x)
        "0001": {"x": -4.3, "y": 2.2},   # Spieler-Faction (links neben Spieler-Lane)
        "0002": {"x": -4.3, "y": -2.2},  # Gegner-Faction (links neben Gegner-Lane)
        
        # Idle-Felder (mittlere Reihe)
        "3011": {"x": -0.8, "y": 0},
        "3012": {"x": 0.4, "y": 0},
        "3013": {"x": 1.6, "y": 0},
        
        # Gegner-Felder (2xxx)
        "2111": {"x": -1.4, "y": -2.2},   # unten
        "2112": {"x": -0.8, "y": -4.3},   # oben
        "2213": {"x": -0.2, "y": -2.2},   # unten
        "2114": {"x": 0.4, "y": -4.3},    # oben
        "2215": {"x": 1.0, "y": -2.2},   # unten
        "2116": {"x": 1.6, "y": -4.3},    # oben
        "2117": {"x": 2.2, "y": -2.2},   # unten
        
        # Spieler-Felder (1xxx)
        "1111": {"x": -1.4, "y": 2.2},    # unten
        "1112": {"x": -0.8, "y": 4.3},    # oben
        "1213": {"x": -0.2, "y": 2.2},    # unten
        "1114": {"x": 0.4, "y": 4.3},     # oben
        "1215": {"x": 1.0, "y": 2.2},    # unten
        "1116": {"x": 1.6, "y": 4.3},     # oben
        "1117": {"x": 2.2, "y": 2.2},    # unten
        
        # Preview-Spieler (4xxx)
        "4001": {"x": -2.0, "y": 4.3},     # oben
        "4002": {"x": -1.4, "y": 6.4},     # unten
        "4003": {"x": -0.8, "y": 8.5},     # oben
        "4004": {"x": -0.2, "y": 6.4},     # unten
        "4005": {"x": 0.4, "y": 8.5},      # oben
        "4006": {"x": 1.0, "y": 6.4},      # unten
        "4007": {"x": 1.6, "y": 8.5},      # oben
        "4008": {"x": 2.2, "y": 6.4},      # unten
        
        # Preview-Gegner (5xxx)
        "5001": {"x": -2.0, "y": -4.3},    # oben
        "5002": {"x": -1.4, "y": -6.4},    # unten
        "5003": {"x": -0.8, "y": -8.5},    # oben
        "5004": {"x": -0.2, "y": -6.4},    # unten
        "5005": {"x": 0.4, "y": -8.5},     # oben
        "5006": {"x": 1.0, "y": -6.4},     # unten
        "5007": {"x": 1.6, "y": -8.5},     # oben
        "5008": {"x": 2.2, "y": -6.4},     # unten
        
        # Back-Spieler (6xxx)
        "6001": {"x": -3.7, "y": 4.3},     # unten
        "6002": {"x": -4.3, "y": 6.4},     # oben
        "6003": {"x": -3.7, "y": 8.5},     # unten
        "6004": {"x": -4.3, "y": 6.4},     # oben (Duplikat?)
        
        # Back-Gegner (7xxx)
        "7002": {"x": -3.7, "y": -4.3},    # unten
        "7003": {"x": -4.3, "y": -6.4},    # oben
        "7004": {"x": -3.7, "y": -8.5},    # unten
    }

    def __init__(self, board: Board, screen_width: int = 1280, screen_height: int = 720):
        """
        Initialisiert den BoardRenderer.
        
        Args:
            board: Das Board-Objekt
            screen_width: Bildschirmbreite (default 1280)
            screen_height: Bildschirmhöhe (default 720)
        """
        self.board = board
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.hex_buttons: Dict[str, HexButton] = {}
        self.is_visible = False
        self.show_extra_fields = False  # Für 4xxx-9xxx Felder
        self.show_might_values = True  # Might-Werte auf 1xxx/2xxx Feldern anzeigen
        
        # Berechne Board-Zentrum
        self.board_center_x = screen_width // 2
        self.board_center_y = screen_height // 2
        
        # Berechne Distanzen
        self.hex_horiz_distance = HEX_SIZE["width"] * 1.5  # 120
        self.vert_offset = HEX_SIZE["height"] * 0.25     # 20
        
        # Default Factions für 0001/0002
        self.player_faction = "Adam"
        self.opponent_faction = "Skeletor"
        
        # MightCalculator für Might-Berechnungen
        from core.managers.might_calculator import MightCalculator
        self.might_calc = MightCalculator(board)

    def toggle_visibility(self) -> None:
        """Schaltet die Sichtbarkeit des Boards um."""
        self.is_visible = not self.is_visible

    def toggle_extra_fields(self) -> None:
        """Schaltet die Anzeige der extra Felder (4xxx-9xxx) um."""
        self.show_extra_fields = not self.show_extra_fields

    def set_factions(self, player_faction: str, opponent_faction: str) -> None:
        """Setzt die Factions für die Anzeige auf 0001/0002."""
        self.player_faction = player_faction
        self.opponent_faction = opponent_faction
        # Aktualisiere die HexButtons für 0001/0002
        self._update_faction_buttons()

    def _update_faction_buttons(self) -> None:
        """Aktualisiert die Text-Beschriftung der Faction-Hexfelder."""
        if "0001" in self.hex_buttons:
            self.hex_buttons["0001"].text = self.player_faction
        if "0002" in self.hex_buttons:
            self.hex_buttons["0002"].text = self.opponent_faction

    def _calculate_absolute_position(self, hex_id: HexID) -> Tuple[int, int]:
        """
        Berechnet die absolute (x, y)-Position für ein Hexfeld.
        
        Args:
            hex_id: Die HexID
            
        Returns:
            Tuple (x, y) in Pixel-Koordinaten
        """
        rel_pos = self.BOARD_POSITIONS.get(hex_id.raw_id)
        if rel_pos is None:
            # Standard-Position falls nicht definiert
            return (0, 0)
        
        x = self.board_center_x + rel_pos["x"] * self.hex_horiz_distance
        y = self.board_center_y + rel_pos["y"] * self.vert_offset
        
        return (int(x), int(y))

    def _get_field_color(self, hex_id: HexID) -> Tuple[int, int, int]:
        """
        Bestimmt die Farbe eines Hexfelds basierend auf seinem Bereich.
        
        Args:
            hex_id: Die HexID
            
        Returns:
            RGB-Farbtuple
        """
        # Faction Indicator (0001/0002) - nutzen Faction-Farben
        if hex_id.raw_id == "0001":
            return FACTION_COLORS.get(self.player_faction, {}).get("primary", COLORS["primary"])
        elif hex_id.raw_id == "0002":
            return FACTION_COLORS.get(self.opponent_faction, {}).get("primary", COLORS["primary"])
        
        # Idle-Felder (3xxx)
        elif hex_id.area == 3:
            return COLORS.get("idle_neutral", (200, 200, 0))
        
        # Spieler-Felder (1xxx, 4xxx, 6xxx, 8xxx)
        elif hex_id.area in [1, 4, 6, 8]:
            return FACTION_COLORS.get(self.player_faction, {}).get("primary", (0, 255, 0))
        
        # Gegner-Felder (2xxx, 5xxx, 7xxx, 9xxx)
        elif hex_id.area in [2, 5, 7, 9]:
            return FACTION_COLORS.get(self.opponent_faction, {}).get("primary", (128, 0, 128))
        
        # Default
        return COLORS["background"]

    def _get_field_text(self, hex_id: HexID) -> str:
        """
        Bestimmt den Text für ein Hexfeld.
        
        Args:
            hex_id: Die HexID
            
        Returns:
            Text-String (kann Zeilenumbrüche enthalten)
        """
        # Faction Indicator zeigen Faction-Namen
        if hex_id.raw_id == "0001":
            return self.player_faction
        elif hex_id.raw_id == "0002":
            return self.opponent_faction
        
        # Für 1xxx und 2xxx Felder: Hex-ID + Might anzeigen (falls Entities vorhanden)
        if hex_id.area in [1, 2] and self.show_might_values:
            entities = self.board.get_entities_on_hex(hex_id)
            if entities:
                might = self.might_calc.calculate_might_for_hex(hex_id)
                return f"{hex_id.raw_id}\nM:{might:.0f}"
        
        # Andere Felder zeigen Hex-ID (kurz)
        return hex_id.raw_id

    def create_hex_buttons(self) -> None:
        """Erstellt HexButtons für alle relevanten Board-Felder."""
        for hex_id in self.board._valid_hex_ids:
            # Standardmäßig: 000x, 1xxx, 2xxx, 3xxx Felder rendern
            if hex_id.area not in [0, 1, 2, 3]:
                # Extra Felder (4xxx-9xxx) nur wenn aktiviert
                if not self.show_extra_fields:
                    continue
                # Nur 4xxx-7xxx für jetzt (8xxx, 9xxx haben keine Positionen)
                if hex_id.area not in [4, 5, 6, 7]:
                    continue
            
            # Nur wenn Position definiert ist
            if hex_id.raw_id not in self.BOARD_POSITIONS:
                continue
            
            x, y = self._calculate_absolute_position(hex_id)
            color = self._get_field_color(hex_id)
            text = self._get_field_text(hex_id)
            
            # HexButton erstellen (Größe = HEX_SIZE["width"])
            button = HexButton(
                x=x - HEX_SIZE["width"] // 2,  # Zentrieren
                y=y - HEX_SIZE["height"] // 2,
                size=HEX_SIZE["width"],
                color=color,
                text=text,
                hex_id=hex_id.raw_id,
                text_color=(0, 0, 0),  # Schwarz für bessere Sichtbarkeit
                font_size=14  # Kleinere Schrift für mehrzeiligen Text
            )
            self.hex_buttons[hex_id.raw_id] = button

    def update_button_texts(self) -> None:
        """Aktualisiert die Texte aller HexButtons (z. B. nach Might-Änderungen)."""
        for hex_id_str, button in self.hex_buttons.items():
            hex_id = HexID(hex_id_str)
            button.text = self._get_field_text(hex_id)

    def render(self, surface: pygame.Surface) -> None:
        """
        Rendert alle HexButtons auf die Oberfläche.
        
        Args:
            surface: Pygame-Oberfläche
        """
        if not self.is_visible:
            return
        
        # Alle HexButtons zeichnen
        for button in self.hex_buttons.values():
            button.render(surface)
        
        # Idle-Rahmen zeichnen (falls kontrolliert)
        self._draw_idle_controls(surface)

    def _draw_idle_controls(self, surface: pygame.Surface) -> None:
        """Zeichnet farbige Rahmen um kontrollierte Idle-Felder."""
        for idle_id in ["3011", "3012", "3013"]:
            controller = self.board.get_idle_controller(HexID(idle_id))
            if controller and idle_id in self.hex_buttons:
                button = self.hex_buttons[idle_id]
                faction_color = FACTION_COLORS.get(controller, {}).get("primary", COLORS["highlight"])
                # Rahmen um das Hexagon zeichnen
                pygame.draw.polygon(surface, faction_color, button.points, 3)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Behandelt Events für HexButtons.
        Gibt True zurück, wenn ein Button geklickt wurde.
        """
        if not self.is_visible:
            return False
        
        for button in self.hex_buttons.values():
            if button.handle_event(event):
                return True
        return False

    def get_button(self, hex_id: str) -> Optional[HexButton]:
        """Gibt den HexButton für eine Hex-ID zurück."""
        return self.hex_buttons.get(hex_id)
