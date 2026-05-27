"""
Testumgebung für Sturm auf Grayskull.
720p Konsolen-Fenster mit In-Game-Konsolenausgabe für Testergebnisse.
Nutzt globale Konstanten für Farben und UI-Komponenten.
"""

import pygame
import json
from pygame.locals import *
from core.game.board import Board
from core.entities.figure import Figure
from core.entities.location import Location
from core.entities.effect import Effect
from core.utils.hex_id import HexID
from core.utils.global_constants import COLORS
from interfaces.renderer.pygame.screen import Screen
from interfaces.renderer.pygame.components.console import Console
from interfaces.game_controller import GameController
from interfaces.renderer.pygame.audio import AudioManager

# --- JSON-Dateien laden ---
FIGURENWERK_PATH = "data/figurenwerk.json"
ETERNIAORTE_PATH = "data/eterniaorte.json"
EFFECTS_PATH = "data/effects.json"

with open(FIGURENWERK_PATH, "r", encoding="utf-8") as f:
    figuren = json.load(f)
with open(ETERNIAORTE_PATH, "r", encoding="utf-8") as f:
    orte = json.load(f)
with open(EFFECTS_PATH, "r", encoding="utf-8") as f:
    effekte = json.load(f)

# --- Test-Entities aus JSON (einmalig geladen) ---
adam = Figure.from_dict(figuren["1110"])          # Adam (ID 1110)
orko = Figure.from_dict(figuren["1111"])          # Orko (ID 1111)
vine_dschungel = Location.from_dict(orte["6002"])  # Vine Dschungel (ID 6002)
schlangenstab = Effect.from_dict(effekte["9212"]) # Schlangenstab (ID 9212)


def main():
    # --- Initialisierung der UI-Komponenten ---
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
    screen = Screen(SCREEN_WIDTH, SCREEN_HEIGHT)
    console = Console(20, 550, 1240, 150, max_lines=15)
    controller = GameController()
    audio = AudioManager()
    audio.play_music(loop=True)

    # --- Board initialisieren ---
    board = Board()

    # --- Testfunktionen (innerhalb von main() definiert) ---
    def test_board():
        """Test 1: Prüft, ob Hexfelder in Gruppen (0, 1xxx, 2xxx, 8xxx) erstellt wurden."""
        board.battle_init()  # ✅ Hexfelder erstellen (wie später im Spiel)

        valid_ids = [h.raw_id for h in board.get_valid_hex_ids()]
        groups = {
            "0 (Idle)": [h for h in valid_ids if h.startswith("30")],
            "1xxx (Spieler)": [h for h in valid_ids if h.startswith("1") or h.startswith("2")],
            "2xxx (Gegner)": [h for h in valid_ids if h.startswith("2")],
            "8xxx (Effekte)": [h for h in valid_ids if h.startswith("8")]
        }

        # Zusammenfassung ausgeben
        all_valid = True
        for group, ids in groups.items():
            if ids:
                console.log(f"{group}: {len(ids)} Felder (Beispiele: {ids[:3]}...)", COLORS["highlight"])
            else:
                console.log(f"{group}: ❌ Keine Felder gefunden!", COLORS["idle_opponent"])
                all_valid = False

        if all_valid:
            console.log(f"✅ Alle Gruppen valide! Gesamt: {len(valid_ids)} Hexfelder.", COLORS["highlight"])
        else:
            console.log("❌ Einige Gruppen fehlen!", COLORS["idle_opponent"])
            
    def test_figure_placement():
        """Test 2: Platziert Adam (1110) auf 1111."""
        success = board.place_entity(HexID("1111"), adam)
        console.log(f"Figur 'Adam' auf 1111 platziert: {success}", COLORS["highlight"] if success else COLORS["idle_opponent"])

    def test_location_placement():
        """Test 3: Platziert Vine Dschungel (6002) auf 1112."""
        success = board.place_entity(HexID("1112"), vine_dschungel)
        console.log(f"Location 'Vine Dschungel' auf 1112 platziert: {success}", COLORS["highlight"] if success else COLORS["idle_opponent"])

    def test_figure_and_location():
        """Test 4: Platziert Orko (1111) + Vine Dschungel (6002) auf 1112."""
        board.place_entity(HexID("1112"), orko)
        board.place_entity(HexID("1112"), vine_dschungel)
        loc = board.get_location_at(HexID("1112"))
        fig = board.get_figure_at(HexID("1112"))
        console.log(f"Location auf 1112: {loc.name if loc else 'None'}")
        console.log(f"Figur auf 1112: {fig.name if fig else 'None'}")

    def test_might_calculation():
        """Test 5: Berechnet Orko's Might (ohne Nachbarn/Location)."""
        neighbors = board.get_neighbors(HexID("1111"))
        might = orko.calculate_might(neighbors, opponent=None, location=None)
        console.log(f"Orko's Might (ohne Nachbarn/Location): {might}")

    def test_might_calculation_with_location():
        """Test 6: Berechnet Orko's Might mit Vine Dschungel auf 1112."""
        board.place_entity(HexID("1112"), orko)
        board.place_entity(HexID("1112"), vine_dschungel)
        neighbors = board.get_neighbors(HexID("1112"))
        location = board.get_location_at(HexID("1112"))
        might = orko.calculate_might(neighbors, opponent=None, location=location)
        console.log(f"Orko's Might (mit Vine Dschungel auf 1112): {might}")

    def test_effect_placement():
        """Test 7: Platziert Schlangenstab (9212) auf 8001."""
        success = board.place_entity(HexID("8001"), schlangenstab)
        console.log(f"Effekt 'Schlangenstab' auf 8001 platziert: {success}", COLORS["highlight"] if success else COLORS["idle_opponent"])

    def test_idle_control():
        """Test 8: Prüft Idle-Kontrolle (Might von Spieler/Gegner)."""
        for idle in board.get_idle_fields():
            player_might = sum(
                fig.calculate_might(board.get_neighbors(hex_id), opponent=None)
                for hex_id in board.get_idle_neighbors(idle)["player"]
                if (fig := board.get_figure_at(hex_id))
            )
            opponent_might = sum(
                fig.calculate_might(board.get_neighbors(hex_id), opponent=None)
                for hex_id in board.get_idle_neighbors(idle)["opponent"]
                if (fig := board.get_figure_at(hex_id))
            )
            controller_name = "Player" if player_might > opponent_might else "Opponent" if opponent_might > player_might else "None"
            console.log(f"Idle {idle.raw_id}: Player: {player_might}, Opponent: {opponent_might}, Controller: {controller_name}")

    # --- Testbeschreibungen ---
    test_descriptions = [
        "1: Board-Aufbau prüfen (gültige Hex-IDs)",
        "2: Figur Adam (1110) auf 1111 platzieren",
        "3: Location Vine Dschungel (6002) auf 1112 platzieren",
        "4: Figur Orko (1111) + Vine Dschungel auf 1112 platzieren",
        "5: Might-Berechnung (Orko ohne Nachbarn/Location)",
        "6: Might-Berechnung (Orko mit Vine Dschungel auf 1112)",
        "7: Effekt Schlangenstab (9212) auf 8001 platzieren",
        "8: Idle-Kontrolle (Might von angrenzenden Feldern)",
        "C: Konsole löschen | ESC: Beenden"
    ]

    # --- Konsolenausgabe im Fenster ---
    console.log("=== Sturm auf Grayskull - Kern-Tests ===", COLORS["highlight"])
    console.log("Drücke 1-8 für Tests, C zum Löschen, ESC zum Beenden", COLORS["primary"])

    # --- Hauptschleife ---
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
                elif event.key == K_1:
                    console.log("[USER] Taste 1 gedrückt.", COLORS["highlight"])
                    test_board()
                elif event.key == K_2:
                    console.log("[USER] Taste 2 gedrückt.", COLORS["highlight"])
                    test_figure_placement()
                elif event.key == K_3:
                    console.log("[USER] Taste 3 gedrückt.", COLORS["highlight"])
                    test_location_placement()
                elif event.key == K_4:
                    console.log("[USER] Taste 4 gedrückt.", COLORS["highlight"])
                    test_figure_and_location()
                elif event.key == K_5:
                    console.log("[USER] Taste 5 gedrückt.", COLORS["highlight"])
                    test_might_calculation()
                elif event.key == K_6:
                    console.log("[USER] Taste 6 gedrückt.", COLORS["highlight"])
                    test_might_calculation_with_location()
                elif event.key == K_7:
                    console.log("[USER] Taste 7 gedrückt.", COLORS["highlight"])
                    test_effect_placement()
                elif event.key == K_8:
                    console.log("[USER] Taste 8 gedrückt.", COLORS["highlight"])
                    test_idle_control()
            elif event.type == MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                console.log(f"[USER] Mausklick bei ({x}, {y})", COLORS["highlight"])

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()