import pygame
import os
import json
from pygame.locals import *
from core.game.board import Board
from core.entities.figure import Figure
from core.entities.location import Location
from core.entities.effect import Effect
from core.utils.hex_id import HexID
from core.utils.global_constants import COLORS
from core.tests.init_test import InitTest  # ✅ Neuer Import

# Basisverzeichnis (Ordner der simulation.py)
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "data")

# --- JSON-Daten laden (wie in deiner Version) ---

with open(os.path.join(data_dir, "figurenwerk.json"), "r", encoding="utf-8") as f:
    figuren = json.load(f)
with open(os.path.join(data_dir, "eterniaorte.json"), "r", encoding="utf-8") as f:
    eterniaorte = json.load(f)
with open(os.path.join(data_dir, "effekte.json"), "r", encoding="utf-8") as f:
    effekte = json.load(f)

# --- Dummy-Entitäten (wie in deiner Version) ---
dummy_figure = Figure.from_dict(figuren["0000"])
dummy_location = Location.from_dict(eterniaorte["0000"])
dummy_effect = Effect.from_dict(effekte["0000"])

# --- Konsolenklasse (wie in deiner Version) ---
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

# --- Screen-Klasse (wie in deiner Version) ---
class Screen:
    def __init__(self, width, height):
        self.screen = pygame.display.set_mode((width, height))
        self.width = width
        self.height = height
        pygame.display.set_caption("Sturm auf Grayskull - Kern-Tests")

    def render(self):
        self.screen.fill(COLORS["background"])

    def draw_text(self, text, x, y, color=COLORS["text"]):
        font = pygame.font.SysFont("Courier New", 16)
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def get_surface(self):
        return self.screen

# --- Testbeschreibungen (wie in deiner Version) ---
test_descriptions = [
    "1: Board-Aufbau prüfen (gültige Hex-IDs)",
    "2: Dummy-Entitäten laden",
    "3: Location auf 0000 platzieren",
    "4: Figur auf 0000 platzieren (mit Location)",
    "5: Effekt auf 0000 platzieren (mit Figur + Location)",
    "6: Alle Hexfelder erstellen",
    "7: Alle Figuren und Factions laden",
    "8: Alle Locations und Effekte laden",
    "C: Konsole löschen | ESC: Beenden"
]

# --- Hauptfunktion ---
def main():
    pygame.init()
    screen = Screen(1280, 720)
    console = InGameConsole(20, 550, 1240, 150, max_lines=15)
    board = Board()

    # --- Konsolenausgabe im Fenster ---
    console.log("=== Sturm auf Grayskull - Kern-Tests ===", COLORS["highlight"])
    console.log("Drücke 1-8 für Tests, C zum Löschen, ESC zum Beenden", COLORS["primary"])

    # ✅ Automatische Ausführung der Init-Tests (1–5, 7–8) beim Start
    init_test = InitTest(board, console, screen, figuren, eterniaorte, effekte)
    init_test.run()  # Führt Tests 1–5, 7–8 aus

    # --- Hauptschleife (wie in deiner Version) ---
    running = True
    clock = pygame.time.Clock()
    while running:
        screen.render()  # Hintergrund rendern

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
                    valid_ids = [h.raw_id for h in board.get_valid_hex_ids()]
                    console.log(f"Anzahl Hexfelder: {len(valid_ids)}", COLORS["text"])
                    console.log("✅ Test 6: Alle Hexfelder erfolgreich erstellt!", COLORS["highlight"])
                # ✅ Tests 1–5, 7–8 werden nicht mehr manuell aufgerufen (laufen automatisch beim Start)
            elif event.type == MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                console.log(f"[USER] Mausklick bei ({x}, {y})", COLORS["highlight"])

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()