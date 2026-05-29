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
from core.entities.vehicle import Vehicle
from core.utils.hex_id import HexID
from core.utils.global_constants import COLORS
from interfaces.renderer.pygame.screen import Screen
from interfaces.renderer.pygame.components.console import Console
from interfaces.game_controller import GameController
from interfaces.renderer.pygame.audio import AudioManager

# --- JSON-Dateien laden ---
FIGURENWERK_PATH = "data/figurenwerk.json"
ETERNIAORTE_PATH = "data/eterniaorte.json"
EFFEKTE_PATH = "data/effekte.json"
FAHRZEUGE_PATH = "data/fahrzeuge.json"

with open(FIGURENWERK_PATH, "r", encoding="utf-8") as f:
    figuren = json.load(f)
with open(ETERNIAORTE_PATH, "r", encoding="utf-8") as f:
    orte = json.load(f)
with open(EFFEKTE_PATH, "r", encoding="utf-8") as f:
    effekte = json.load(f)
# In simulation.py:
with open("data/fahrzeuge.json", "r", encoding="utf-8") as f:
    vehicles = json.load(f)


# --- Dummy-Entities (ID 0000) ---
dummy_figure = Figure.from_dict(figuren["0000"])      # Dummy-Figur (ID 0000)
dummy_location = Location.from_dict(orte["0000"])    # Dummy-Location (ID 0000)
dummy_effect = Effect.from_dict(effekte["0000"])      # Dummy-Effekt (ID 0000)
dummy_vehicle = Vehicle.from_dict(vehicles["0000"])

# --- Bestehende Test-Entities (für Kompatibilität) ---
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
    def test_hex_id_0000():
        """Test 1: Erstelle das Hexfeld 0000 (Avatar-Feld)."""
        console.log("--- Test 1: Hexfeld 0000 ---", COLORS["highlight"])

        # 1. HexID erstellen
        try:
            hex_id = HexID("0000")
            console.log(f"✅ HexID '0000' erstellt: {hex_id.raw_id}", COLORS["highlight"])
        except ValueError as e:
            console.log(f"❌ Fehler bei HexID-Erstellung: {e}", COLORS["idle_opponent"])
            return

        # 2. Prüfen, ob HexID auf dem Board existiert
        if board.is_valid_position(hex_id):
            console.log(f"✅ HexID '0000' existiert auf dem Board.", COLORS["highlight"])
        else:
            console.log(f"❌ HexID '0000' existiert NICHT auf dem Board.", COLORS["idle_opponent"])
            return

        # 3. Nachbarn prüfen (sollte leer sein)
        neighbors = board.get_optical_neighbors(hex_id)
        if len(neighbors) == 0:
            console.log(f"✅ HexID '0000' hat keine Nachbarn (erwartet).", COLORS["highlight"])
        else:
            console.log(f"❌ HexID '0000' hat Nachbarn: {neighbors} (unerwartet).", COLORS["idle_opponent"])

        # 4. Sichtbarkeit prüfen
        if board.is_visible(hex_id):
            console.log(f"✅ HexID '0000' ist sichtbar.", COLORS["highlight"])
        else:
            console.log(f"❌ HexID '0000' ist NICHT sichtbar.", COLORS["idle_opponent"])

    def test_load_entities():
        """Test 2: Lade Dummy-Entities (Figur 0000, Location 0000, Effekt 0000)."""
        console.log("--- Test 2: Entities laden ---", COLORS["highlight"])

        # 1. Dummy-Figur laden
        console.log(f"✅ Dummy-Figur geladen: {dummy_figure.name} (ID: {dummy_figure.id}, Might: {dummy_figure.base_might})", COLORS["highlight"])

        # 2. Dummy-Location laden
        console.log(f"✅ Dummy-Location geladen: {dummy_location.name} (ID: {dummy_location.id}, Buffs: {len(dummy_location.buffs['self'])})", COLORS["highlight"])

        # 3. Dummy-Effekt laden
        console.log(f"✅ Dummy-Effekt geladen: {dummy_effect.name} (ID: {dummy_effect.id}, Cost: {dummy_effect.cost})", COLORS["highlight"])

    def test_place_location():
        """Test 3: Lege Dummy-Location (0000) auf Feld 0000 (Might ohne Figur)."""
        console.log("--- Test 3: Location auf 0000 platzieren ---", COLORS["highlight"])

        hex_id = HexID("0000")

        # 1. Location platzieren
        success = board.place_entity(hex_id, dummy_location)
        console.log(f"Location '{dummy_location.name}' auf {hex_id.raw_id} platziert: {success}", COLORS["highlight"] if success else COLORS["idle_opponent"])

        if not success:
            return

        # 2. Might der Location berechnen (ohne Figur)
        location = board.get_location_at(hex_id)
        if location:
            # Might = base_might + self-buffs (hier: 0 + 2 = 2)
            might = location.calculate_might(board.get_neighbors(hex_id), opponent=None, location=None)
            console.log(f"Might der Location (ohne Figur): {might} (erwartet: 2)", COLORS["highlight"] if might == 2 else COLORS["idle_opponent"])
        else:
            console.log(f"❌ Location auf {hex_id.raw_id} nicht gefunden!", COLORS["idle_opponent"])

    def test_place_figure():
        """Test 4: Stelle Dummy-Figur (0000) auf Feld 0000 (Might mit Figur + Location)."""
        console.log("--- Test 4: Figur auf 0000 platzieren ---", COLORS["highlight"])

        hex_id = HexID("0000")

        # 1. Figur platzieren (überschreibt Location nicht, da verschiedene Typen)
        success = board.place_entity(hex_id, dummy_figure)
        console.log(f"Figur '{dummy_figure.name}' auf {hex_id.raw_id} platziert: {success}", COLORS["highlight"] if success else COLORS["idle_opponent"])

        if not success:
            return

        # 2. Might der Figur berechnen (mit Location)
        figure = board.get_figure_at(hex_id)
        location = board.get_location_at(hex_id)
        if figure and location:
            # Might = base_might (5) + location.self-buffs (2) = 7
            might = figure.calculate_might(board.get_neighbors(hex_id), opponent=None, location=location)
            console.log(f"Might der Figur (mit Location): {might} (erwartet: 7)", COLORS["highlight"] if might == 7 else COLORS["idle_opponent"])
        else:
            console.log(f"❌ Figur oder Location auf {hex_id.raw_id} nicht gefunden!", COLORS["idle_opponent"])

    def test_place_effect():
        """Test 5: Lege Dummy-Effekt (0000) auf Feld 0000 (Might mit Figur + Location + Effekt)."""
        console.log("--- Test 5: Effekt auf 0000 platzieren ---", COLORS["highlight"])

        hex_id = HexID("0000")

        # 1. Effekt platzieren
        success = board.place_entity(hex_id, dummy_effect)
        console.log(f"Effekt '{dummy_effect.name}' auf {hex_id.raw_id} platziert: {success}", COLORS["highlight"] if success else COLORS["idle_opponent"])

        if not success:
            return

        # 2. Might der Figur berechnen (mit Location + Effekt)
        figure = board.get_figure_at(hex_id)
        location = board.get_location_at(hex_id)
        effect = board.get_effect_at(hex_id)

        if figure and location and effect:
            # Might = base_might (5) + location.self-buffs (2) + effect.self-buffs (0) = 7
            might = figure.calculate_might(board.get_neighbors(hex_id), opponent=None, location=location)
            console.log(f"Might der Figur (mit Location + Effekt): {might} (erwartet: 7)", COLORS["highlight"] if might == 7 else COLORS["idle_opponent"])
        else:
            console.log(f"❌ Figur, Location oder Effekt auf {hex_id.raw_id} nicht gefunden!", COLORS["idle_opponent"])

    def test_board():
        """Test 6: Prüft, ob Hexfelder in Gruppen (0, 1xxx, 2xxx, 8xxx) erstellt wurden."""
        board.battle_init()  # Hexfelder erstellen

        valid_ids = [h.raw_id for h in board.get_valid_hex_ids()]
        groups = {
            "0 (Avatar)": [h for h in valid_ids if h.startswith("00")],
            "1xxx (Spieler)": [h for h in valid_ids if h.startswith("1")],
            "2xxx (Gegner)": [h for h in valid_ids if h.startswith("2")],
            "3xxx (Idle)": [h for h in valid_ids if h.startswith("3")],
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

    def test_load_figures_and_factions():
        """Test 7: Lade alle Figuren und Faction-Pools."""
        console.log("--- Test 7: Figuren & Faction-Pools laden ---", COLORS["highlight"])

        # 1. Alle Figuren laden
        figures_loaded = len(figuren)
        console.log(f"✅ {figures_loaded} Figuren geladen (inkl. Dummy-Figur 0000).", COLORS["highlight"])

        # 2. Faction-Pools laden
        with open("data/factions.json", "r", encoding="utf-8") as f:
            factions = json.load(f)
        console.log(f"✅ Faction-Pools geladen: {list(factions.keys())}", COLORS["highlight"])

    def test_load_locations_and_effects():
        """Test 8: Lade alle Locations und Effekte."""
        console.log("--- Test 8: Locations & Effekte laden ---", COLORS["highlight"])

        # 1. Alle Locations laden
        locations_loaded = len(orte)
        console.log(f"✅ {locations_loaded} Locations geladen (inkl. Dummy-Location 0000).", COLORS["highlight"])

        # 2. Alle Effekte laden
        effects_loaded = len(effekte)
        console.log(f"✅ {effects_loaded} Effekte geladen (inkl. Dummy-Effekt 0000).", COLORS["highlight"])

    # --- Testbeschreibungen ---
    test_descriptions = [
        "1: Hexfeld 0000 erstellen",
        "2: Dummy-Entities (Figur, Location, Effekt) laden",
        "3: Dummy-Location auf 0000 platzieren (Might ohne Figur)",
        "4: Dummy-Figur auf 0000 platzieren (Might mit Figur + Location)",
        "5: Dummy-Effekt auf 0000 platzieren (Might mit Figur + Location + Effekt)",
        "6: Alle HexFelder erstellen",
        "7: Figuren & Faction-Pools laden",
        "8: Locations & Effekte laden",
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
                    test_hex_id_0000()
                elif event.key == K_2:
                    console.log("[USER] Taste 2 gedrückt.", COLORS["highlight"])
                    test_load_entities()
                elif event.key == K_3:
                    console.log("[USER] Taste 3 gedrückt.", COLORS["highlight"])
                    test_place_location()
                elif event.key == K_4:
                    console.log("[USER] Taste 4 gedrückt.", COLORS["highlight"])
                    test_place_figure()
                elif event.key == K_5:
                    console.log("[USER] Taste 5 gedrückt.", COLORS["highlight"])
                    test_place_effect()
                elif event.key == K_6:
                    console.log("[USER] Taste 6 gedrückt.", COLORS["highlight"])
                    test_board()
                elif event.key == K_7:
                    console.log("[USER] Taste 7 gedrückt.", COLORS["highlight"])
                    test_load_figures_and_factions()
                elif event.key == K_8:
                    console.log("[USER] Taste 8 gedrückt.", COLORS["highlight"])
                    test_load_locations_and_effects()
            elif event.type == MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                console.log(f"[USER] Mausklick bei ({x}, {y})", COLORS["highlight"])

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
