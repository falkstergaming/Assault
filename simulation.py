"""
Simulation.py für Sturm auf Grayskull - DEBUGGER-Modus
- Startet die Debug-Umgebung mit Pygame
- Ermöglicht manuelles Testen von Board, Might-Berechnung und Idle-Kontrolle
- Enthält Action- und Settings-Button
- JSON-Daten werden geladen für Entity-Erstellung
"""

import pygame
from pygame.locals import *
import json
import os
from pathlib import Path

# --- Imports für das Spiel ---
from core.game.board import Board
from core.game.debug_state import DebugState
from core.entities.figure import Figure
from core.entities.location import Location
from core.entities.effect import Effect
from core.entities.vehicle import Vehicle
from core.utils.hex_id import HexID
from core.utils.global_constants import COLORS, FIGURES_JSON, LOCATIONS_JSON, EFFECTS_JSON, VEHICLE_JSON
from core.utils.translations import TRANSLATIONS
from core.utils.settings import Settings
from interfaces.renderer.pygame.screen import Screen
from interfaces.renderer.pygame.components.button import HexButton
from interfaces.renderer.pygame.components.game_status import GameStatusDisplay
from interfaces.renderer.pygame.components.settings_menu import SettingsMenu
from interfaces.renderer.pygame.components.board_renderer import BoardRenderer

# --- JSON-Daten laden ---
base_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_dir, FIGURES_JSON), "r", encoding="utf-8") as f:
    figuren = json.load(f)
with open(os.path.join(base_dir, LOCATIONS_JSON), "r", encoding="utf-8") as f:
    eterniaorte = json.load(f)
with open(os.path.join(base_dir, EFFECTS_JSON), "r", encoding="utf-8") as f:
    effekte = json.load(f)
with open(os.path.join(base_dir, VEHICLE_JSON), "r", encoding="utf-8") as f:
    fahrzeuge = json.load(f)

# --- Dummy-Entitäten ---
dummy_figure = Figure.from_dict(figuren["0000"])
dummy_location = Location.from_dict(eterniaorte["0000"])
dummy_effect = Effect.from_dict(effekte["0000"])
dummy_vehicle = Vehicle.from_dict(fahrzeuge["0000"])


# --- Konsolenklasse ---
class InGameConsole:
    def __init__(self, x, y, width, height, max_lines=15):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_lines = max_lines
        self.lines = []
        self.font = pygame.font.SysFont("Courier New", 16)

    def log(self, text, color=COLORS["text"]):
        self.lines.append((text, color))
        if len(self.lines) > self.max_lines:
            self.lines.pop(0)

    def clear(self):
        self.lines = []

    def render(self, surface):
        pygame.draw.rect(surface, COLORS["background"], (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, COLORS["primary"], (self.x, self.y, self.width, self.height), 1)
        for i, (line, color) in enumerate(self.lines):
            text_surface = self.font.render(line, True, color)
            surface.blit(text_surface, (self.x + 10, self.y + 10 + i * 20))


# --- Debugger-Klasse ---
class BoardDebugger:
    """
    Debugger für das Board - ermöglicht manuelles Testen von:
    - Board-Erstellung
    - Entity-Platzierung
    - Might-Berechnung
    - Idle-Kontrolle
    """
    
    def __init__(self, board: Board, console: InGameConsole, game_status: GameStatusDisplay):
        self.board = board
        self.console = console
        self.game_status = game_status
        self.state = DebugState()
        
    def run_test(self, test_name: str, test_func):
        """Führt einen Test aus und loggt das Ergebnis."""
        self.state.set_test(test_name)
        self.console.log(f"=== {test_name} ===", COLORS["highlight"])
        try:
            test_func()
            self.console.log(f"✅ {test_name} abgeschlossen!", COLORS["highlight"])
        except Exception as e:
            self.console.log(f"❌ {test_name} FEHLGESCHLAGEN: {e}", COLORS["text"])
        finally:
            self.state.clear_test()

    def test_game_status_display(self):
        """Test 1: Spielstandsanzeige aktualisieren"""
        self.game_status.update(
            modus="Best of 4",
            match_count="2/4",
            round_count=3,
            phase="Marsch",
            player={"idle_count": 0, "might": 45, "matches_won": 1},
            opponent={"idle_count": 0, "might": 30, "matches_won": 0}
        )

    def test_create_all_hex_fields(self):
        """Test 2: Alle Hexfelder erstellen"""
        valid_ids = [h.raw_id for h in self.board._valid_hex_ids]
        self.console.log(f"Anzahl Hexfelder: {len(valid_ids)}", COLORS["text"])
        
        # Zeige alle Felder nach Bereich
        by_area = {}
        for hex_id in self.board._valid_hex_ids:
            area = hex_id.area
            if area not in by_area:
                by_area[area] = []
            by_area[area].append(hex_id.raw_id)
        
        for area, ids in sorted(by_area.items()):
            self.console.log(f"  Bereich {area}: {len(ids)} Felder", COLORS["text"])

    def test_toggle_board(self):
        """Test 3: Toggle board (000x - 3xxx) - wird über Taste 9 gesteuert"""
        self.console.log("Board-Rendering wird über Taste 9 gesteuert", COLORS["highlight"])

    def test_fill_with_entities(self):
        """Test 5: Fülle mit Faction Standard Entities"""
        # Board zurücksetzen
        self.board.clear_board()
        
        # Entities laden
        location_6666 = Location.from_dict(eterniaorte["6666"])
        figure_1999 = Figure.from_dict(figuren["1999"])
        figure_2999 = Figure.from_dict(figuren["2999"])
        
        # Felder definieren
        player_fields = ["1111", "1112", "1213", "1114", "1215", "1116", "1117"]
        opponent_fields = ["2111", "2112", "2213", "2114", "2215", "2116", "2117"]
        all_fields = player_fields + opponent_fields
        
        # Alle Felder mit Location 6666 füllen
        for field_id in all_fields:
            hex_id = HexID(field_id)
            self.board.place_entity(hex_id, location_6666)
        self.console.log(f"✅ {len(all_fields)} Locations (6666) platziert", COLORS["highlight"])
        
        # 1xxx Felder mit Figur 1999 füllen
        for field_id in player_fields:
            hex_id = HexID(field_id)
            self.board.place_entity(hex_id, figure_1999)
        self.console.log(f"✅ {len(player_fields)} Figuren (1999) auf 1xxx platziert", COLORS["highlight"])
        
        # 2xxx Felder mit Figur 2999 füllen
        for field_id in opponent_fields:
            hex_id = HexID(field_id)
            self.board.place_entity(hex_id, figure_2999)
        self.console.log(f"✅ {len(opponent_fields)} Figuren (2999) auf 2xxx platziert", COLORS["highlight"])
        
        # Might berechnen und Spielstand aktualisieren
        self._update_game_status_might()

    def test_calculate_might(self):
        """Test 6: Trigger calc might"""
        from core.managers.might_calculator import MightCalculator
        might_calc = MightCalculator(self.board)
        
        player_fields = ["1111", "1112", "1213", "1114", "1215", "1116", "1117"]
        opponent_fields = ["2111", "2112", "2213", "2114", "2215", "2116", "2117"]
        all_fields = player_fields + opponent_fields
        
        # Might für jedes Feld berechnen
        self.console.log("--- Might pro Hexfeld ---", COLORS["highlight"])
        for field in all_fields:
            hex_id = HexID(field)
            might = might_calc.calculate_might_for_hex(hex_id)
            split = might_calc.get_might_split(hex_id)
            self.console.log(f"{field}: Might={might:.1f}, Split={split}", COLORS["text"])
        
        # Spieler und Gegner Might summieren
        self._update_game_status_might()

    def test_calculate_idle_might(self):
        """Test 7: Trigger idle might"""
        from core.managers.might_calculator import MightCalculator
        might_calc = MightCalculator(self.board)
        
        self.console.log("--- Idle Might Berechnung ---", COLORS["highlight"])
        
        for idle_id in ["3011", "3012", "3013"]:
            idle_hex_id = HexID(idle_id)
            idle_neighbors = self.board.get_idle_neighbors(idle_hex_id)
            
            # Spieler-Seite
            player_fields = idle_neighbors.get("player", [])
            player_might_sum = sum(might_calc.calculate_might_for_hex(f) for f in player_fields)
            player_idle_might = round(player_might_sum * 0.5)
            
            # Gegner-Seite
            opponent_fields = idle_neighbors.get("opponent", [])
            opponent_might_sum = sum(might_calc.calculate_might_for_hex(f) for f in opponent_fields)
            opponent_idle_might = round(opponent_might_sum * 0.5)
            
            # Controller bestimmen
            if player_idle_might > opponent_idle_might:
                controller = "player"
            elif opponent_idle_might > player_idle_might:
                controller = "opponent"
            else:
                controller = "none"
            
            self.console.log(
                f"Idle {idle_id}: Spieler={player_idle_might}, Gegner={opponent_idle_might} → {controller}",
                COLORS["text"]
            )

    def test_idle_control(self):
        """Test 8: Check Idle Controll"""
        from core.managers.might_calculator import MightCalculator
        might_calc = MightCalculator(self.board)
        
        self.console.log("--- Idle Kontrolle setzen ---", COLORS["highlight"])
        
        for idle_id in ["3011", "3012", "3013"]:
            idle_hex_id = HexID(idle_id)
            idle_neighbors = self.board.get_idle_neighbors(idle_hex_id)
            
            # Spieler-Seite
            player_fields = idle_neighbors.get("player", [])
            player_might_sum = sum(might_calc.calculate_might_for_hex(f) for f in player_fields)
            player_idle_might = round(player_might_sum * 0.5)
            
            # Gegner-Seite
            opponent_fields = idle_neighbors.get("opponent", [])
            opponent_might_sum = sum(might_calc.calculate_might_for_hex(f) for f in opponent_fields)
            opponent_idle_might = round(opponent_might_sum * 0.5)
            
            # Controller bestimmen und setzen
            if player_idle_might > opponent_idle_might:
                self.board.set_idle_control(idle_hex_id, "player")
                controller = "player"
            elif opponent_idle_might > player_idle_might:
                self.board.set_idle_control(idle_hex_id, "opponent")
                controller = "opponent"
            else:
                self.board.set_idle_control(idle_hex_id, None)
                controller = "none"
            
            self.console.log(
                f"Idle {idle_id}: Spieler={player_idle_might}, Gegner={opponent_idle_might} → {controller}",
                COLORS["text"]
            )
        
        # Idle-Count aktualisieren
        self._update_game_status_might()

    def _update_game_status_might(self):
        """Aktualisiert den Spielstand mit Might und Idle-Count."""
        from core.managers.might_calculator import MightCalculator
        might_calc = MightCalculator(self.board)
        
        player_fields = ["1111", "1112", "1213", "1114", "1215", "1116", "1117"]
        opponent_fields = ["2111", "2112", "2213", "2114", "2215", "2116", "2117"]
        
        player_might = sum(might_calc.calculate_might_for_hex(HexID(field)) for field in player_fields)
        opponent_might = sum(might_calc.calculate_might_for_hex(HexID(field)) for field in opponent_fields)
        
        # Idle-Count
        player_idle_count = self.board.get_player_idle_count()
        opponent_idle_count = self.board.get_opponent_idle_count()
        
        self.game_status.update(
            player={"idle_count": player_idle_count, "might": int(player_might)},
            opponent={"idle_count": opponent_idle_count, "might": int(opponent_might)}
        )
        
        self.console.log(
            f"Spieler Might: {int(player_might)} | Gegner Might: {int(opponent_might)} | "
            f"Idles: Spieler={player_idle_count}, Gegner={opponent_idle_count}",
            COLORS["highlight"]
        )


# --- Hauptfunktion ---
def main():
    # --- Initialisierung ---
    pygame.init()

    # Bildschirmdimensionen
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    STATUS_HEIGHT = int(SCREEN_HEIGHT * 0.15)
    CONSOLE_HEIGHT = int(SCREEN_HEIGHT * 0.15)
    MARGIN_VERTICAL = 25
    MARGIN_HORIZONTAL = int(SCREEN_WIDTH * 0.1)

    # Einstellungen laden
    settings = Settings()

    # Board initialisieren
    board = Board()

    # BoardRenderer erstellen
    board_renderer = BoardRenderer(board, SCREEN_WIDTH, SCREEN_HEIGHT)
    board_renderer.create_hex_buttons()

    # Screen und Console erstellen
    screen = Screen(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Settings-Menü erstellen
    settings_menu = SettingsMenu(
        x=SCREEN_WIDTH - 25 - 250,
        y=STATUS_HEIGHT + MARGIN_VERTICAL + 5,
        settings=settings
    )

    # Spielstandsanzeige erstellen
    game_status = GameStatusDisplay(SCREEN_WIDTH, SCREEN_HEIGHT, settings=settings)
    
    # Console
    console = InGameConsole(
        x=MARGIN_HORIZONTAL,
        y=SCREEN_HEIGHT - CONSOLE_HEIGHT - MARGIN_VERTICAL,
        width=SCREEN_WIDTH - 2 * MARGIN_HORIZONTAL,
        height=CONSOLE_HEIGHT,
        max_lines=15
    )

    # --- Action- und Settings-Button ---
    action_button = HexButton(
        x=SCREEN_WIDTH - 100,
        y=SCREEN_HEIGHT // 2,
        size=80,
        color=COLORS["primary"],
        text=TRANSLATIONS[settings.language]["action"],
        callback=lambda: console.log("[ACTION] Action-Button geklickt!", COLORS["highlight"])
    )
    screen.add_button(action_button)

    settings_button = HexButton(
        x=SCREEN_WIDTH - 25 - 50,
        y=25,
        size=50,
        color=COLORS["primary"],
        text="⚙",
        hex_id=None,
        callback=lambda: settings_menu.toggle()
    )
    screen.add_button(settings_button)

    # --- Debugger initialisieren ---
    debugger = BoardDebugger(board, console, game_status)

    # --- Konsolenausgabe ---
    console.log("=== Sturm auf Grayskull - DEBUGGER ===", COLORS["highlight"])
    console.log("Drücke 1-8 für Tests, C zum Löschen, ESC zum Beenden", COLORS["primary"])
    console.log("Drücke 9 für Board-Toggle, 4 für Extra-Felder", COLORS["primary"])

    # --- Testbeschreibungen ---
    test_descriptions = [
        "1: Spielstandsanzeige testen",
        "2: Alle Hexfelder anzeigen",
        "3: Toggle board (000x - 3xxx)",
        "4: Toggle extra Hexfields (4xxx - 7xxx)",
        "5: Board mit Standard-Entities füllen",
        "6: Might pro Hexfeld berechnen",
        "7: Idle Might berechnen",
        "8: Idle Kontrolle setzen",
        "C: Konsole löschen | ESC: Beenden"
    ]

    # --- Hauptschleife ---
    running = True
    clock = pygame.time.Clock()

    while running:
        # --- Hintergrund und UI rendern ---
        screen.render()
        board_renderer.render(screen.get_surface())
        settings_menu.render(screen.get_surface())
        game_status.render(screen.get_surface())
        console.render(screen.get_surface())

        # --- Testbeschreibungen zeichnen ---
        for i, desc in enumerate(test_descriptions):
            screen.draw_text(desc, MARGIN_HORIZONTAL, STATUS_HEIGHT + MARGIN_VERTICAL + 20 + i * 25, COLORS["text"])

        # --- Eingabe verarbeiten ---
        for event in pygame.event.get():
            if settings_menu.handle_event(event):
                continue

            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_c:
                    console.clear()
                    console.log("Konsole gelöscht.", COLORS["primary"])
                # --- Tests 1-8 ---
                elif event.key == K_1:
                    debugger.run_test("Spielstandsanzeige", debugger.test_game_status_display)
                elif event.key == K_2:
                    debugger.run_test("Alle Hexfelder", debugger.test_create_all_hex_fields)
                elif event.key == K_3:
                    console.log("[DEBUG] Taste 3: Board-Toggle (verwende Taste 9)", COLORS["highlight"])
                elif event.key == K_4:
                    board_renderer.toggle_extra_fields()
                    board_renderer.create_hex_buttons()
                    board_renderer.update_button_texts()
                    status = "AKTIVIERT" if board_renderer.show_extra_fields else "DEAKTIVIERT"
                    console.log(f"Extra Hexfields (4xxx-7xxx): {status}", COLORS["highlight"])
                elif event.key == K_5:
                    debugger.run_test("Board mit Entities füllen", debugger.test_fill_with_entities)
                elif event.key == K_6:
                    debugger.run_test("Might berechnen", debugger.test_calculate_might)
                elif event.key == K_7:
                    debugger.run_test("Idle Might berechnen", debugger.test_calculate_idle_might)
                elif event.key == K_8:
                    debugger.run_test("Idle Kontrolle setzen", debugger.test_idle_control)
                # --- Taste 9: Board-Toggle ---
                elif event.key == K_9:
                    board_renderer.toggle_visibility()
                    board_renderer.update_button_texts()
                    status = "AKTIVIERT" if board_renderer.is_visible else "DEAKTIVIERT"
                    console.log(f"Board-Rendering (000x-3xxx): {status}", COLORS["highlight"])
            
            # --- Button-Events ---
            screen.handle_event(event)
            if board_renderer.is_visible:
                board_renderer.handle_event(event)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
