""""
Simulation.py für Sturm auf Grayskull.
- Startet die Testumgebung mit Pygame.
- Zeigt Testbeschreibungen an und führt Tests aus.
- Enthält Action- und Settings-Button (HexButtons).
- Test 6 (Alle Hexfelder erstellen) bleibt manuell ausführbar (Taste 6).
- JSON-Daten werden wie von dir gewünscht geladen (mit base_dir und os.path.join).
"""

import pygame
from pygame.locals import *
import json
import os
from pathlib import Path

# --- Imports für das Spiel ---
from core.game.board import Board
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
from core.tests.init_test import InitTest
from interfaces.renderer.pygame.components.board_renderer import BoardRenderer

# --- JSON-Daten laden (mit globalen Konstanten) ---
# Basisverzeichnis (Ordner der simulation.py)
base_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_dir, FIGURES_JSON), "r", encoding="utf-8") as f:
    figuren = json.load(f)
with open(os.path.join(base_dir, LOCATIONS_JSON), "r", encoding="utf-8") as f:
    eterniaorte = json.load(f)
with open(os.path.join(base_dir, EFFECTS_JSON), "r", encoding="utf-8") as f:
    effekte = json.load(f)
with open(os.path.join(base_dir, VEHICLE_JSON), "r", encoding="utf-8") as f:
    fahrzeuge = json.load(f)
with open(os.path.join(base_dir, VEHICLE_JSON), "r", encoding="utf-8") as f:
    fahrzeuge = json.load(f)

# --- Dummy-Entitäten (DEIN ORIGINAL-CODE) ---
dummy_figure = Figure.from_dict(figuren["0000"])
dummy_location = Location.from_dict(eterniaorte["0000"])
dummy_effect = Effect.from_dict(effekte["0000"])
dummy_vehicle = Vehicle.from_dict(fahrzeuge["0000"])

# --- Konsolenklasse (bestehend) ---
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

# --- Testbeschreibungen (neu geordnet) ---
test_descriptions = [
    "1: Funktion Spielstandsanzeige",
    "2: Alle Hexfelder erstellen",
    "3: Toggle board (000x - 3xxx)",
    "4: Toggle extra Hexfields (4xxx - 9xxx)",
    "5: Fülle mit Faction Standard Entities",
    "6: Trigger calc might",
    "7: Trigger idle might",
    "8: Check Idle Controll",
    "C: Konsole löschen | ESC: Beenden"
]

# --- Hauptfunktion ---
def main():
    # --- Initialisierung ---
    pygame.init()

    # Bildschirmdimensionen
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    STATUS_HEIGHT = int(SCREEN_HEIGHT * 0.15)  # 15% für Spielstand
    CONSOLE_HEIGHT = int(SCREEN_HEIGHT * 0.15)  # 15% für Konsole
    MARGIN_VERTICAL = 25  # 25px Abstand zum Rand
    MARGIN_HORIZONTAL = int(SCREEN_WIDTH * 0.1)  # 10% Platz links/rechts

    # Einstellungen laden
    settings = Settings()

    # Board initialisieren
    board = Board()

    # BoardRenderer erstellen (erst später aktiviert mit Taste 9)
    board_renderer = BoardRenderer(board, SCREEN_WIDTH, SCREEN_HEIGHT)
    board_renderer.create_hex_buttons()

    # Screen und Console erstellen
    screen = Screen(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Settings-Menü erstellen (noch nicht aktiv) - rechtsbündig mit Button, unter dem Button
    settings_menu = SettingsMenu(
        x=SCREEN_WIDTH - 25 - 250,  # 25px Abstand zum rechten Rand (1280 - 25 - 250 = 1005)
        y=25 + 50 + 5,              # Unter dem Settings-Button (25 + 50 + 5px Abstand)
        settings=settings
    )

    # Settings-Menü erstellen (unter der Spielstandsanzeige, linksbündig mit Spielstand)
    # Spielstand: x=128, width=1024 → endet bei 1152
    # Menü: width=250 → beginnt bei 1152-250-5=897 (5px Abstand zum Spielstand)
    settings_menu = SettingsMenu(
        x=1152 - 250 - 5,         # Linksbündig: 1152-250-5=897 (5px Abstand zum Spielstand)
        y=STATUS_HEIGHT + 25 + 5,   # Unter der Spielstandsanzeige (108 + 25 + 5 = 138)
        settings=settings
    )

    # Spielstandsanzeige erstellen (mit Settings für Sprachauswahl)
    game_status = GameStatusDisplay(SCREEN_WIDTH, SCREEN_HEIGHT, settings=settings)
    
    # Console: 15% Höhe, 25px Abstand zum unteren Rand, 10% Rand links/rechts
    console = InGameConsole(
        x=MARGIN_HORIZONTAL,
        y=SCREEN_HEIGHT - CONSOLE_HEIGHT - MARGIN_VERTICAL,
        width=SCREEN_WIDTH - 2 * MARGIN_HORIZONTAL,
        height=CONSOLE_HEIGHT,
        max_lines=15
    )

    # --- Action- und Settings-Button erstellen und hinzufügen ---
    # Action-Button: Groß (size=80), rechts am Rand, mittig
    # Text je nach Sprache: EN="Action", DE="Weiter"
    action_button = HexButton(
        x=SCREEN_WIDTH - 100,  # 100px Abstand zum rechten Rand
        y=SCREEN_HEIGHT // 2,   # Mittig
        size=80,                # Groß
        color=COLORS["primary"],
        text=TRANSLATIONS[settings.language]["action"],
        callback=lambda: console.log("[ACTION] Action-Button geklickt!", COLORS["highlight"])
    )
    screen.add_button(action_button)

    # Settings-Button: Klein (size=50), oben rechts mit 25px Abstand zu Rand
    # hex_id=None und text="⚙" um sicherzustellen, dass nur das Symbol angezeigt wird
    settings_button = HexButton(
        x=SCREEN_WIDTH - 25 - 50,  # 25px Abstand zum rechten Rand (1280 - 25 - 50 = 1205)
        y=25,                      # 25px Abstand zum oberen Rand
        size=50,                  # Klein
        color=COLORS["primary"],
        text="⚙",                # Nur das Steuerrad-Symbol (kein numerischer Wert)
        hex_id=None,              # Keine hex_id - verhindert, dass "0" oder ID angezeigt wird
        callback=lambda: settings_menu.toggle()
    )
    screen.add_button(settings_button)

    # --- Konsolenausgabe im Fenster ---
    console.log("=== Sturm auf Grayskull - Kern-Tests ===", COLORS["highlight"])
    console.log("Drücke 1-8 für Tests, C zum Löschen, ESC zum Beenden", COLORS["primary"])

    # --- Init-Tests vorbereiten ---
    init_test = InitTest(board, console, screen, figuren, eterniaorte, effekte, fahrzeuge)
    init_tests_executed = False

    # --- Hauptschleife ---
    running = True
    clock = pygame.time.Clock()

    while running:
        # --- Hintergrund und UI rendern ---
        screen.render()

        # --- Board rendern (falls aktiviert mit Taste 9) ---
        board_renderer.render(screen.get_surface())

        # --- Settings-Menü rendern (falls aktiv) ---
        settings_menu.render(screen.get_surface())

        # --- Spielstandsanzeige rendern (ganz oben) ---
        game_status.render(screen.get_surface())

        # --- Testbeschreibungen zeichnen (unter der Statusleiste) ---
        for i, desc in enumerate(test_descriptions):
            screen.draw_text(desc, MARGIN_HORIZONTAL, STATUS_HEIGHT + MARGIN_VERTICAL + 20 + i * 25, COLORS["text"])

        # --- Konsolenausgabe rendern ---
        console.render(screen.get_surface())

        # --- Init-Tests ausführen (einmalig, zwischen Console und Eingabe) ---
        if not init_tests_executed:
            init_test.run()
            init_tests_executed = True

        # --- Eingabe verarbeiten ---
        for event in pygame.event.get():
            # --- Settings-Menü Events behandeln ---
            if settings_menu.handle_event(event):
                continue  # Event wurde vom Settings-Menü verbraucht

            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_c:
                    console.clear()
                    console.log("Konsole gelöscht.", COLORS["primary"])
                # --- Taste 1: Funktion Spielstandsanzeige (alter Test 4) ---
                elif event.key == K_1:
                    console.log("[USER] Taste 1 gedrückt: Funktion Spielstandsanzeige", COLORS["highlight"])
                    # Aktualisiere Spielstandsdaten
                    game_status.update(
                        modus="Best of 4",
                        match_count="2/4",
                        round_count=3,
                        phase="Marsch",
                        player={"idle_count": 2, "might": 45, "matches_won": 1},
                        opponent={"idle_count": 1, "might": 30, "matches_won": 0}
                    )
                    console.log("✅ Test 1: Spielstandsanzeige aktualisiert mit Testdaten!", COLORS["highlight"])
                # --- Taste 2: Alle Hexfelder erstellen (alter Test 6) ---
                elif event.key == K_2:
                    console.log("[USER] Taste 2 gedrückt: Alle Hexfelder erstellen", COLORS["highlight"])
                    valid_ids = [h.raw_id for h in board._valid_hex_ids]
                    console.log(f"Anzahl Hexfelder: {len(valid_ids)}", COLORS["text"])
                    console.log("✅ Test 2: Alle Hexfelder erfolgreich erstellt!", COLORS["highlight"])
                # --- Taste 3: Toggle board (000x - 3xxx) (alter Test 9) ---
                elif event.key == K_3:
                    console.log("[USER] Taste 3 gedrückt: Toggle board (000x - 3xxx)", COLORS["highlight"])
                    board_renderer.toggle_visibility()
                    status = "AKTIVIERT" if board_renderer.is_visible else "DEAKTIVIERT"
                    console.log(f"Board-Rendering (000x-3xxx): {status}", COLORS["highlight"])
                # --- Taste 4: Toggle extra Hexfields (4xxx - 9xxx) ---
                elif event.key == K_4:
                    console.log("[USER] Taste 4 gedrückt: Toggle extra Hexfields (4xxx - 9xxx)", COLORS["highlight"])
                    console.log("⚠️ Test 4: Funktion noch nicht implementiert", COLORS["text"])
                # --- Tasten 5-8: Platzhalter ---
                elif event.key == K_5:
                    console.log("[USER] Taste 5 gedrückt: Fülle mit Faction Standard Entities", COLORS["highlight"])
                    console.log("⚠️ Test 5: Funktion noch nicht implementiert", COLORS["text"])
                elif event.key == K_6:
                    console.log("[USER] Taste 6 gedrückt: Trigger calc might", COLORS["highlight"])
                    console.log("⚠️ Test 6: Funktion noch nicht implementiert", COLORS["text"])
                elif event.key == K_7:
                    console.log("[USER] Taste 7 gedrückt: Trigger idle might", COLORS["highlight"])
                    console.log("⚠️ Test 7: Funktion noch nicht implementiert", COLORS["text"])
                elif event.key == K_8:
                    console.log("[USER] Taste 8 gedrückt: Check Idle Controll", COLORS["highlight"])
                    console.log("⚠️ Test 8: Funktion noch nicht implementiert", COLORS["text"])
            # --- Button-Events behandeln ---
            screen.handle_event(event)
            # Board-Button Events
            board_renderer.handle_event(event)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()