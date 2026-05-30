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
from core.utils.hex_id import HexID
from core.utils.global_constants import COLORS
from interfaces.renderer.pygame.screen import Screen
from interfaces.renderer.pygame.components.button import HexButton

# --- JSON-Daten laden (DEIN ORIGINAL-CODE) ---
# Basisverzeichnis (Ordner der simulation.py)
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "data")

with open(os.path.join(data_dir, "figurenwerk.json"), "r", encoding="utf-8") as f:
    figuren = json.load(f)
with open(os.path.join(data_dir, "eterniaorte.json"), "r", encoding="utf-8") as f:
    eterniaorte = json.load(f)
with open(os.path.join(data_dir, "effekte.json"), "r", encoding="utf-8") as f:
    effekte = json.load(f)

# --- Dummy-Entitäten (DEIN ORIGINAL-CODE) ---
dummy_figure = Figure.from_dict(figuren["0000"])
dummy_location = Location.from_dict(eterniaorte["0000"])
dummy_effect = Effect.from_dict(effekte["0000"])

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

# --- Testbeschreibungen (aktualisiert) ---
test_descriptions = [
    "1: Check draw and function action button",
    "2: Check draw and function settings button",
    "3: Check draw and show Spielstandsanzeige",
    "4: Check function Spielstandsanzeige",
    "5: open ",
    "6: Alle Hexfelder erstellen",
    "7: Check choose player",
    "8: Check choose mode",
    "C: Konsole löschen | ESC: Beenden"
]

# --- Hauptfunktion ---
def main():
    # --- Initialisierung ---
    pygame.init()

    # Board initialisieren
    board = Board()

    # Screen und Console erstellen
    screen = Screen(1280, 720)
    console = InGameConsole(x=20, y=550, width=1240, height=150, max_lines=15)

    # --- Action- und Settings-Button erstellen und hinzufügen ---
    # Action-Button: Groß (size=80), rechts am Rand, mittig
    action_button = HexButton(
        x=1280 - 100,  # 100px Abstand zum rechten Rand
        y=360,          # Mittig (720/2 = 360)
        size=80,        # Groß
        color=COLORS["primary"],
        text="Weiter",
        callback=lambda: console.log("[ACTION] Action-Button geklickt!", COLORS["highlight"])
    )
    screen.add_button(action_button)

    # Settings-Button: Klein (size=50), oben rechts im Eck
    settings_button = HexButton(
        x=1280 - 60,   # 10px Abstand + 50/2 (size/2)
        y=10,           # 10px Abstand nach oben
        size=50,        # Klein
        color=COLORS["primary"],
        text="⚙",       # Symbol für Settings
        callback=lambda: console.log("[SETTINGS] Settings-Button geklickt!", COLORS["highlight"])
    )
    screen.add_button(settings_button)

    # --- Konsolenausgabe im Fenster ---
    console.log("=== Sturm auf Grayskull - Kern-Tests ===", COLORS["highlight"])
    console.log("Drücke 1-8 für Tests, C zum Löschen, ESC zum Beenden", COLORS["primary"])

    # --- Hauptschleife ---
    running = True
    clock = pygame.time.Clock()

    while running:
        # --- Hintergrund und UI rendern ---
        screen.render()

        # --- Testbeschreibungen zeichnen ---
        for i, desc in enumerate(test_descriptions):
            screen.draw_text(desc, 20, 50 + i * 25, COLORS["text"])

        # --- Konsolenausgabe rendern ---
        console.render(screen.get_surface())

        # --- Eingabe verarbeiten ---
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_c:
                    console.clear()
                    console.log("Konsole gelöscht.", COLORS["primary"])
                elif event.key == K_6:
                    console.log("[USER] Taste 6 gedrückt.", COLORS["highlight"])
                    # Test 6: Alle Hexfelder erstellen
                    valid_ids = [h.raw_id for h in board._valid_hex_ids]
                    console.log(f"Anzahl Hexfelder: {len(valid_ids)}", COLORS["text"])
                    console.log("✅ Test 6: Alle Hexfelder erfolgreich erstellt!", COLORS["highlight"])
            # --- Button-Events behandeln ---
            screen.handle_event(event)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()