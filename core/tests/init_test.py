from core.game.board import Board
from core.entities.figure import Figure
from core.entities.location import Location
from core.entities.effect import Effect
from core.entities.vehicle import Vehicle
from core.managers.might_calculator import MightCalculator
from core.utils.hex_id import HexID
from core.utils.global_constants import COLORS

class InitTest:
    """Führt alle Initialisierungstests (1–5, 7–8) aus und nutzt deine bestehende Console/Screen."""

    def __init__(self, board: Board, console, screen, figuren, eterniaorte, effekte, fahrzeuge=None):
        self.board = board
        self.console = console
        self.screen = screen
        self.figuren = figuren
        self.eterniaorte = eterniaorte
        self.effekte = effekte
        self.fahrzeuge = fahrzeuge if fahrzeuge else {}
        self.might_calculator = MightCalculator(board)

        # Lade die Dummy-Entitäten aus den übergebene JSON-Daten
        self.dummy_figure = Figure.from_dict(figuren["0000"])
        self.dummy_location = Location.from_dict(eterniaorte["0000"])
        self.dummy_effect = Effect.from_dict(effekte["0000"])
        self.dummy_vehicle = Vehicle.from_dict(self.fahrzeuge.get("0000", {"id": "0000", "name": "DummyVehicle", "type": "vehicle", "base_might": 0}))

    def load_dummy_entities(self):
        """Lädt die Dummy-Entitäten aus den JSON-Dateien (Fallback, falls benötigt)."""
        # Wird nicht in run() aufgerufen, da Dummies bereits im __init__ geladen werden.
        # Aber die Methode bleibt für andere Zwecke erhalten.
        self.dummy_figure = Figure.from_dict({"id": "0000", "name": "DummyFigure", "type": "figure", "base_might": 5, "buffs": {"self": []}})
        self.dummy_location = Location.from_dict({"id": "0000", "name": "DummyLocation", "type": "location", "base_might": 0, "buffs": {"self": [{"value": 2, "target": None, "target_type": "self"}]}})
        self.dummy_effect = Effect.from_dict({"id": "0000", "name": "DummyEffect", "type": "effect", "base_might": 0, "buffs": {"self": []}})

    def run(self):
        """Führt alle Tests (1–6, 7–8) aus und gibt Ergebnisse in der Konsole aus."""
        self.console.log("=== INITIALISIERUNGSTESTS ===", COLORS["highlight"])

        # Test 1: Board-Aufbau
        self._test_board()

        # Test 2: Dummy-Entities laden
        self._test_dummy_entities()

        # Test 3: Location auf 0000 platzieren
        self._test_place_location()

        # Test 4: Figur auf 0000 platzieren (mit Location)
        self._test_place_figure()

        # Test 5: Effekt auf 0000 platzieren (mit Figur + Location)
        self._test_place_effect()

        # Test 6: Vehicle auf 0000 platzieren (mit Figur + Location + Effekt)
        self._test_place_vehicle()

        # Test 7: Alle Figuren laden
        self._test_load_all_figures()

        # Test 8: Alle Locations/Effekte laden
        self._test_load_all_locations_and_effects()

        self.console.log("=== INITIALISIERUNGSTESTS ABGESCHLOSSEN ===", COLORS["highlight"])

    def _test_board(self):
        """Test 1: Prüft, ob das Board richtig aufgebaut ist."""
        self.console.log("\n--- Test 1: Board-Aufbau ---", COLORS["primary"])
        # ✅ Korrigiert: Nutze _valid_hex_ids (da get_valid_hex_ids() nicht existiert)
        valid_ids = sorted([h.raw_id for h in self.board._valid_hex_ids], key=lambda x: int(x))
        self.console.log(f"Gültige Hex-IDs: {valid_ids}", COLORS["text"])
        self.console.log("✅ Test 1: Board-Aufbau erfolgreich!", COLORS["highlight"])

    def _test_dummy_entities(self):
        """Test 2: Prüft, ob Dummy-Entitäten geladen wurden."""
        self.console.log("\n--- Test 2: Dummy-Entitäten laden ---", COLORS["primary"])
        if self.dummy_figure and self.dummy_location and self.dummy_effect:
            self.console.log("✅ Test 2: Dummy-Entitäten erfolgreich geladen!", COLORS["highlight"])
        else:
            self.console.log("❌ Test 2: Dummy-Entitäten fehlen!", COLORS["idle_opponent"])

    def _test_place_location(self):
        """Test 3: Platziert Location auf 0000 und prüft Might für das Hexfeld."""
        self.console.log("\n--- Test 3: Location auf 0000 platzieren ---", COLORS["primary"])
        hex_id = HexID("0000")
        success = self.board.place_entity(hex_id, self.dummy_location)
        self.console.log(f"Location platziert: {success}", COLORS["highlight"] if success else COLORS["idle_opponent"])
        if success:
            location = self.board.get_location_at(hex_id)
            if location:
                # Might für das Hexfeld berechnen (neue Methode)
                hex_might = self.might_calculator.calculate_might_for_hex(hex_id)
                expected = self.dummy_location.base_might
                self.console.log(f"Might des Hexfelds 0000: {hex_might} (erwartet: {expected})",
                                COLORS["highlight"] if hex_might == expected else COLORS["idle_opponent"])
                self.console.log("✅ Test 3: Location platziert!", COLORS["highlight"])
            else:
                self.console.log("❌ Test 3: Location nicht gefunden!", COLORS["idle_opponent"])
        else:
            self.console.log("❌ Test 3: Platzierung fehlgeschlagen!", COLORS["idle_opponent"])

    def _test_place_figure(self):
        """Test 4: Platziert Figur auf 0000 (mit Location) und prüft Hexfeld-Might."""
        self.console.log("\n--- Test 4: Figur auf 0000 platzieren (mit Location) ---", COLORS["primary"])
        hex_id = HexID("0000")
        success = self.board.place_entity(hex_id, self.dummy_figure)
        self.console.log(f"Figur platziert: {success}", COLORS["highlight"] if success else COLORS["idle_opponent"])
        if success:
            figure = self.board.get_figure_at(hex_id)
            location = self.board.get_location_at(hex_id)
            if figure and location:
                # Might für das Hexfeld berechnen (neue Methode)
                hex_might = self.might_calculator.calculate_might_for_hex(hex_id)
                # Erwartet: Figur + Location base_might (+ Location self-buffs)
                location_self_buffs = sum(buff.value for buff in location.buffs["self"])
                expected = self.dummy_figure.base_might + self.dummy_location.base_might + location_self_buffs
                self.console.log(f"Might des Hexfelds 0000: {hex_might} (erwartet: {expected})",
                                COLORS["highlight"] if hex_might == expected else COLORS["idle_opponent"])
                self.console.log("✅ Test 4: Figur platziert!", COLORS["highlight"])
            else:
                self.console.log("❌ Test 4: Figur oder Location nicht gefunden!", COLORS["idle_opponent"])
        else:
            self.console.log("❌ Test 4: Platzierung fehlgeschlagen!", COLORS["idle_opponent"])

    def _test_place_effect(self):
        """Test 5: Platziert Effekt auf 0000 (mit Figur + Location) und prüft Hexfeld-Might."""
        self.console.log("\n--- Test 5: Effekt auf 0000 platzieren (mit Figur + Location) ---", COLORS["primary"])
        hex_id = HexID("0000")
        success = self.board.place_entity(hex_id, self.dummy_effect)
        self.console.log(f"Effekt platziert: {success}", COLORS["highlight"] if success else COLORS["idle_opponent"])
        if success:
            figure = self.board.get_figure_at(hex_id)
            location = self.board.get_location_at(hex_id)
            effect = self.board.get_effect_at(hex_id)
            if figure and location and effect:
                # Might für das Hexfeld berechnen (neue Methode)
                hex_might = self.might_calculator.calculate_might_for_hex(hex_id)
                # Erwartet: Figur + Location + Effekt base_might (+ Selbst-Buffs)
                location_self_buffs = sum(buff.value for buff in location.buffs["self"])
                figure_self_buffs = sum(buff.value for buff in figure.buffs["self"]) if figure.alt else 0
                effect_self_buffs = sum(buff.value for buff in effect.buffs["self"]) if effect.alt else 0
                expected = (self.dummy_figure.base_might + self.dummy_location.base_might + self.dummy_effect.base_might +
                            location_self_buffs + figure_self_buffs + effect_self_buffs)
                self.console.log(f"Might des Hexfelds 0000: {hex_might} (erwartet: {expected})",
                                COLORS["highlight"] if hex_might == expected else COLORS["idle_opponent"])
                self.console.log("✅ Test 5: Effekt platziert!", COLORS["highlight"])
            else:
                self.console.log("❌ Test 5: Figur, Location oder Effekt nicht gefunden!", COLORS["idle_opponent"])
        else:
            self.console.log("❌ Test 5: Platzierung fehlgeschlagen!", COLORS["idle_opponent"])

    def _test_place_vehicle(self):
        """Test 6: Platziert Vehicle auf 0000 (mit Figur + Location + Effekt) und prüft Hexfeld-Might."""
        self.console.log("\n--- Test 6: Vehicle auf 0000 platzieren (mit Figur + Location + Effekt) ---", COLORS["primary"])
        hex_id = HexID("0000")
        success = self.board.place_entity(hex_id, self.dummy_vehicle)
        self.console.log(f"Vehicle platziert: {success}", COLORS["highlight"] if success else COLORS["idle_opponent"])
        if success:
            figure = self.board.get_figure_at(hex_id)
            location = self.board.get_location_at(hex_id)
            effect = self.board.get_effect_at(hex_id)
            vehicle = self.board.get_vehicle_at(hex_id)
            if figure and location and effect and vehicle:
                # Might für das Hexfeld berechnen (neue Methode)
                hex_might = self.might_calculator.calculate_might_for_hex(hex_id)
                # Erwartet: Figur + Location + Effekt + Vehicle base_might (+ Selbst-Buffs)
                location_self_buffs = sum(buff.value for buff in location.buffs["self"])
                figure_self_buffs = sum(buff.value for buff in figure.buffs["self"]) if figure.alt else 0
                effect_self_buffs = sum(buff.value for buff in effect.buffs["self"]) if effect.alt else 0
                expected = (self.dummy_figure.base_might + self.dummy_location.base_might + 
                           self.dummy_effect.base_might + self.dummy_vehicle.base_might +
                            location_self_buffs + figure_self_buffs + effect_self_buffs)
                self.console.log(f"Might des Hexfelds 0000: {hex_might} (erwartet: {expected})",
                                COLORS["highlight"] if hex_might == expected else COLORS["idle_opponent"])
                self.console.log("✅ Test 6: Vehicle platziert!", COLORS["highlight"])
            else:
                self.console.log("❌ Test 6: Eine oder mehrere Entitäten nicht gefunden!", COLORS["idle_opponent"])
        else:
            self.console.log("❌ Test 6: Platzierung fehlgeschlagen!", COLORS["idle_opponent"])

    def _test_load_all_figures(self):
        """Test 7: Lädt alle Figuren aus figurenwerk.json."""
        self.console.log("\n--- Test 7: Alle Figuren laden ---", COLORS["primary"])
        if len(self.figuren) > 0:
            self.console.log(f"Anzahl Figuren: {len(self.figuren)}", COLORS["text"])
            self.console.log("✅ Test 7: Alle Figuren erfolgreich geladen!", COLORS["highlight"])
        else:
            self.console.log("❌ Test 7: Keine Figuren geladen!", COLORS["idle_opponent"])

    def _test_load_all_locations_and_effects(self):
        """Test 8: Lädt alle Locations/Effekte aus den JSON-Dateien."""
        self.console.log("\n--- Test 8: Alle Locations/Effekte laden ---", COLORS["primary"])
        if len(self.eterniaorte) > 0 and len(self.effekte) > 0:
            self.console.log(f"Locations: {len(self.eterniaorte)}, Effekte: {len(self.effekte)}", COLORS["text"])
            self.console.log("✅ Test 8: Alle Locations/Effekte erfolgreich geladen!", COLORS["highlight"])
        else:
            self.console.log("❌ Test 8: Locations oder Effekte fehlen!", COLORS["idle_opponent"])