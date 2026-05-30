"""
Board-Modul für Sturm auf Grayskull.
Verwaltet das Spielfeld mit expliziten Hex-IDs, dynamischer Sichtbarkeit,
und VOLLSTÄNDIGEN Nachbarn-Beziehungen (für Zeichnen und Spiel-Logik).
"""
from core.utils.hex_id import HexID
from typing import List, Dict, Set, Optional, TypeVar, TYPE_CHECKING
from core.entities.base_entity import BaseEntity
from core.entities.figure import Figure      # ✅ Importiere die Klassen
from core.entities.location import Location  # ✅
from core.entities.effect import Effect        # ✅
from core.entities.vehicle import Vehicle      # ✅ Vehicle-Unterstützung

if TYPE_CHECKING:  # Vermeidet Zirkelimports zur Laufzeit
    from core.entities.figure import Figure
    from core.entities.location import Location
    from core.entities.effect import Effect
    from core.entities.vehicle import Vehicle

T = TypeVar('T', BaseEntity, Figure, Location, Effect, Vehicle)  # Generischer Typ für Entities

class Board:
    """
    Verwaltet das Spielfeld mit expliziten Hex-IDs, dynamischer Sichtbarkeit
    und vollständigen Nachbarn-Beziehungen für:
    - Spiel-Logik (Marsch, Might-Berechnung)
    - UI-Rendering (optische Nachbarn)
    """

    def __init__(self):
        """Initialisiert das Board mit gültigen Hex-IDs, Sichtbarkeit und Nachbarn."""
        self._valid_hex_ids: Set[HexID] = self._initialize_valid_hex_ids()
        self._visibility: Dict[HexID, bool] = self._initialize_visibility()
        self._idle_neighbors: Dict[HexID, Dict[str, List[HexID]]] = self._initialize_idle_neighbors()
        self._logical_neighbors: Dict[HexID, List[HexID]] = self._initialize_logical_neighbors()  # Für Spiel-Logik (Marsch)
        self._optical_neighbors: Dict[HexID, List[HexID]] = self._initialize_optical_neighbors()  # Für UI-Rendering

        # Speichere Entities nach Typ pro Hexfeld
        self._figures: Dict[str, BaseEntity] = {}      # {hex_id: Figure}
        self._locations: Dict[str, BaseEntity] = {}   # {hex_id: Location}
        self._effects: Dict[str, BaseEntity] = {}     # {hex_id: Effect}
        self._vehicles: Dict[str, BaseEntity] = {}     # {hex_id: Vehicle}

        # Idol-Kontrolle (für Siegbedingungen)
        self._idle_control: Dict[HexID, Optional[str]] = {
            HexID("3011"): None,
            HexID("3012"): None,
            HexID("3013"): None
        }

    # --- Initialisierung der Hex-IDs ---
    def _initialize_valid_hex_ids(self) -> Set[HexID]:
        """
        Initialisiert die Menge der gültigen Hex-IDs.
        Enthält EXAKT die Felder aus deinem alten Code:
        - Idle-Felder (3xxx): 3011, 3012, 3013
        - Player-Felder (1xxx): 1111, 1112, 1213, 1114, 1215, 1116, 1117
        - AI-Felder (2xxx): 2111, 2112, 2213, 2114, 2215, 2116, 2117
        - Preview-Spieler (4xxx): 4000-4007
        - Preview-Gegner (5xxx): 5000-5007
        - Avatare (0xxx): 0000, 0001, 0002
        - Back-Spieler (6xxx): 6000-6007
        - Back-Gegner (7xxx): 7000-7007
        - Spezial-Spieler (8xxx): 8000-8007
        - Spezial-Gegner (9xxx): 9000-9007
        """
        hex_ids = set()

        # --- Idle-Felder (3xxx) ---
        hex_ids.update({HexID("3011"), HexID("3012"), HexID("3013")})

        # --- Player-Felder (1xxx): 7 Felder ---
        hex_ids.update({
            HexID("1111"), HexID("1112"), HexID("1213"),
            HexID("1114"), HexID("1215"), HexID("1116"), HexID("1117")
        })

        # --- Gegner-Felder (2xxx): 7 Felder ---
        hex_ids.update({
            HexID("2111"), HexID("2112"), HexID("2213"),
            HexID("2114"), HexID("2215"), HexID("2116"), HexID("2117")
        })

        # --- Preview-Spieler (4xxx): 4000-4007 ---
        hex_ids.update(HexID(f"40{num:02d}") for num in range(0, 8))

        # --- Preview-Gegner (5xxx): 5000-5007 ---
        hex_ids.update(HexID(f"50{num:02d}") for num in range(0, 8))

        # --- Avatare (0xxx) ---
        hex_ids.update({HexID("0000"), HexID("0001"), HexID("0002")})

        # --- Back-Spieler (6xxx): 6000-6007 ---
        hex_ids.update(HexID(f"60{num:02d}") for num in range(0, 8))

        # --- Back-Gegner (7xxx): 7000-7007 ---
        hex_ids.update(HexID(f"70{num:02d}") for num in range(0, 8))

        # --- Spezial-Spieler (8xxx): 8000-8007 ---
        hex_ids.update(HexID(f"80{num:02d}") for num in range(0, 8))

        # --- Spezial-Gegner (9xxx): 9000-9007 ---
        hex_ids.update(HexID(f"90{num:02d}") for num in range(0, 8))

        return hex_ids

    def _initialize_visibility(self) -> Dict[HexID, bool]:
        """
        Initialisiert den Sichtbarkeitsstatus für alle Hex-IDs.
        Regel:
        - Spielbrett-Felder (1xxx, 2xxx, 3xxx, 0xxx) → sichtbar.
        - Preview-Felder (4xxx, 5xxx) → anfangs unsichtbar (werden in Runde 0 sichtbar).
        - Backrows (6xxx, 7xxx) und Special (8xxx, 9xxx) → immer unsichtbar.
        """
        visibility = {}
        for hex_id in self._valid_hex_ids:
            # Spielbrett-Felder (1xxx, 2xxx, 3xxx, 0xxx) sind sichtbar
            if hex_id.area in [0, 1, 2, 3]:
                visibility[hex_id] = True
            # Preview-Felder (4xxx, 5xxx) sind anfangs unsichtbar
            elif hex_id.area in [4, 5]:
                visibility[hex_id] = False
            # Backrows (6xxx, 7xxx) und Special (8xxx, 9xxx) sind immer unsichtbar
            else:
                visibility[hex_id] = False
        return visibility

    def _initialize_idle_neighbors(self) -> Dict[HexID, Dict[str, List[HexID]]]:
        """
        Initialisiert die Nachbarn der Idle-Felder für Spieler und Gegner.
        Basierend auf deinem alten Code:
        - 3011: Player = [1111, 1112, 1213], AI = [2111, 2112, 2213]
        - 3012: Player = [1213, 1114, 1215], AI = [2213, 2114, 2215]
        - 3013: Player = [1215, 1116, 1117], AI = [2215, 2116, 2117]
        """
        return {
            HexID("3011"): {
                "player": [HexID("1111"), HexID("1112"), HexID("1213")],
                "opponent": [HexID("2111"), HexID("2112"), HexID("2213")]
            },
            HexID("3012"): {
                "player": [HexID("1213"), HexID("1114"), HexID("1215")],
                "opponent": [HexID("2213"), HexID("2114"), HexID("2215")]
            },
            HexID("3013"): {
                "player": [HexID("1215"), HexID("1116"), HexID("1117")],
                "opponent": [HexID("2215"), HexID("2116"), HexID("2117")]
            }
        }

    def _initialize_logical_neighbors(self) -> Dict[HexID, List[HexID]]:
        """
        Initialisiert die logischen Nachbarn für die Spiel-Logik (Marsch, Might-Berechnung).
        Basierend auf deinem alten Code (horizontale Kette):
        - 1111 ↔ 1112 ↔ 1213 ↔ 1114 ↔ 1215 ↔ 1116 ↔ 1117
        - 2111 ↔ 2112 ↔ 2213 ↔ 2114 ↔ 2215 ↔ 2116 ↔ 2117
        """
        return {
            # Spieler-Lane (horizontale Kette)
            HexID("1111"): [HexID("1112")],
            HexID("1112"): [HexID("1111"), HexID("1213")],
            HexID("1213"): [HexID("1112"), HexID("1114")],
            HexID("1114"): [HexID("1213"), HexID("1215")],
            HexID("1215"): [HexID("1114"), HexID("1116")],
            HexID("1116"): [HexID("1215"), HexID("1117")],
            HexID("1117"): [HexID("1116")],
            # Gegner-Lane (horizontale Kette)
            HexID("2111"): [HexID("2112")],
            HexID("2112"): [HexID("2111"), HexID("2213")],
            HexID("2213"): [HexID("2112"), HexID("2114")],
            HexID("2114"): [HexID("2213"), HexID("2215")],
            HexID("2215"): [HexID("2114"), HexID("2116")],
            HexID("2116"): [HexID("2215"), HexID("2117")],
            HexID("2117"): [HexID("2116")],
        }

    def _initialize_optical_neighbors(self) -> Dict[HexID, List[HexID]]:
        """
        Initialisiert die OPTISCHEN Nachbarn für das UI-Rendering.
        Enthält ALLE sichtbar verbundenen Felder, inkl. Backrows und Preview.
        Basierend auf deinen Anforderungen:
        - Backrow 6000: grenzt an 1111
        - Backrow 6001: grenzt an 1111
        - Backrow 6002: grenzt an 1111 und 1112
        - Backrow 6003: grenzt an 1112 und 1213
        - Backrow 6004: grenzt an 1213 und 1114
        - Backrow 6005: grenzt an 1114 und 1215
        - Backrow 6006: grenzt an 1215 und 1116
        - Backrow 6007: grenzt an 1116 und 1117
        - Preview 4000: grenzt an 1111 und 4001
        - Preview 4001: grenzt an 1111, 4000 und 4002
        - Preview 4002: grenzt an 1111, 1112, 4001 und 4003
        - Preview 4003: grenzt an 1112, 1213, 4002 und 4004
        - Preview 4004: grenzt an 1213, 1114, 4003 und 4005
        - Preview 4005: grenzt an 1114, 1215, 4004 und 4006
        - Preview 4006: grenzt an 1215, 1116, 4005 und 4007
        - Preview 4007: grenzt an 1116, 1117, 4006
        - Analog für Gegner (5xxx, 7xxx).
        """
        optical_neighbors = {}

        # --- Logische Nachbarn (aus _initialize_logical_neighbors) ---
        logical = self._initialize_logical_neighbors()
        for hex_id, neighbors in logical.items():
            optical_neighbors[hex_id] = neighbors.copy()

        # --- Backrow-Spieler (6xxx): Nachbarn zu Spieler-Lane (1xxx) ---
        optical_neighbors[HexID("6000")] = [HexID("1111")]
        optical_neighbors[HexID("6001")] = [HexID("1111")]
        optical_neighbors[HexID("6002")] = [HexID("1111"), HexID("1112")]
        optical_neighbors[HexID("6003")] = [HexID("1112"), HexID("1213")]
        optical_neighbors[HexID("6004")] = [HexID("1213"), HexID("1114")]
        optical_neighbors[HexID("6005")] = [HexID("1114"), HexID("1215")]
        optical_neighbors[HexID("6006")] = [HexID("1215"), HexID("1116")]
        optical_neighbors[HexID("6007")] = [HexID("1116"), HexID("1117")]

        # --- Backrow-Gegner (7xxx): Nachbarn zu Gegner-Lane (2xxx) ---
        optical_neighbors[HexID("7000")] = [HexID("2111")]
        optical_neighbors[HexID("7001")] = [HexID("2111")]
        optical_neighbors[HexID("7002")] = [HexID("2111"), HexID("2112")]
        optical_neighbors[HexID("7003")] = [HexID("2112"), HexID("2213")]
        optical_neighbors[HexID("7004")] = [HexID("2213"), HexID("2114")]
        optical_neighbors[HexID("7005")] = [HexID("2114"), HexID("2215")]
        optical_neighbors[HexID("7006")] = [HexID("2215"), HexID("2116")]
        optical_neighbors[HexID("7007")] = [HexID("2116"), HexID("2117")]

        # --- Preview-Spieler (4xxx): Nachbarn zu Spieler-Lane (1xxx) ---
        optical_neighbors[HexID("4000")] = [HexID("1111"), HexID("4001")]
        optical_neighbors[HexID("4001")] = [HexID("1111"), HexID("4000"), HexID("4002")]
        optical_neighbors[HexID("4002")] = [HexID("1111"), HexID("1112"), HexID("4001"), HexID("4003")]
        optical_neighbors[HexID("4003")] = [HexID("1112"), HexID("1213"), HexID("4002"), HexID("4004")]
        optical_neighbors[HexID("4004")] = [HexID("1213"), HexID("1114"), HexID("4003"), HexID("4005")]
        optical_neighbors[HexID("4005")] = [HexID("1114"), HexID("1215"), HexID("4004"), HexID("4006")]
        optical_neighbors[HexID("4006")] = [HexID("1215"), HexID("1116"), HexID("4005"), HexID("4007")]
        optical_neighbors[HexID("4007")] = [HexID("1116"), HexID("1117"), HexID("4006")]

        # --- Preview-Gegner (5xxx): Nachbarn zu Gegner-Lane (2xxx) ---
        optical_neighbors[HexID("5000")] = [HexID("2111"), HexID("5001")]
        optical_neighbors[HexID("5001")] = [HexID("2111"), HexID("5000"), HexID("5002")]
        optical_neighbors[HexID("5002")] = [HexID("2111"), HexID("2112"), HexID("5001"), HexID("5003")]
        optical_neighbors[HexID("5003")] = [HexID("2112"), HexID("2213"), HexID("5002"), HexID("5004")]
        optical_neighbors[HexID("5004")] = [HexID("2213"), HexID("2114"), HexID("5003"), HexID("5005")]
        optical_neighbors[HexID("5005")] = [HexID("2114"), HexID("2215"), HexID("5004"), HexID("5006")]
        optical_neighbors[HexID("5006")] = [HexID("2215"), HexID("2116"), HexID("5005"), HexID("5007")]
        optical_neighbors[HexID("5007")] = [HexID("2116"), HexID("2117"), HexID("5006")]

        # --- Spezialfelder (8xxx, 9xxx): Keine optischen Nachbarn (können später ergänzt werden) ---
        # Diese Felder haben erst Einfluss, wenn ein Effekt/Transporter platziert wird.
        # Fürs Zeichnen können sie zunächst ohne Nachbarn bleiben.

        return optical_neighbors

    # --- Validierung ---
    def is_valid_position(self, hex_id: HexID) -> bool:
        """Prüft, ob eine HexID auf diesem Board existiert."""
        return hex_id in self._valid_hex_ids

    def is_visible(self, hex_id: HexID) -> bool:
        """
        Prüft, ob ein Hexfeld für den Spieler sichtbar ist.
        Der Status kann dynamisch geändert werden (z. B. durch Scout-Vision).
        """
        if not self.is_valid_position(hex_id):
            return False
        return self._visibility.get(hex_id, False)

    def set_visibility(self, hex_id: HexID, visible: bool) -> bool:
        """
        Setzt den Sichtbarkeitsstatus eines Hexfelds dynamisch.
        Beispiel: Preview-Felder werden in Runde 0 sichtbar geschaltet.
        """
        if not self.is_valid_position(hex_id):
            return False
        self._visibility[hex_id] = visible
        return True

    def get_visibility(self, hex_id: HexID) -> bool:
        """
        Gibt den aktuellen Sichtbarkeitsstatus eines Hexfelds zurück.
        """
        return self._visibility.get(hex_id, False)

    # --- Nachbarn-Abfrage ---
    def get_neighbors(self, hex_id: HexID) -> List[BaseEntity]:
        """Gibt alle Entities (Figuren, Locations, Effekte, Vehicles) auf den Nachbar-Feldern zurück."""
        neighbor_ids = self._logical_neighbors.get(hex_id, [])  # ✅ HexID-Objekt als Key!
        neighbors = []
        for nid in neighbor_ids:
            # Hole alle Entities auf dem Nachbar-Feld
            entities = self.get_entities_on_hex(nid)
            neighbors.extend(entities)
        return neighbors

    def get_neighbor_entities(self, hex_id: HexID) -> List[BaseEntity]:
        """
        Gibt alle Entities auf den logischen Nachbar-Feldern zurück.
        Alias für get_neighbors() zur Kompatibilität mit MightCalculator.
        """
        return self.get_neighbors(hex_id)

    def get_opponent_entity(self, hex_id: HexID) -> Optional[BaseEntity]:
        """
        Gibt die Entity vom gegenüberliegenden Feld zurück.
        Nur relevant für Spieler- (1xxx) und Gegner-Felder (2xxx).
        """
        opponent_field = self.get_opponent_field(hex_id)
        if opponent_field is None:
            return None
        # Es kann nur eine Entity pro Typ geben, wir geben die erste zurück
        # (Priorität: Figur > Location > Effekt > Vehicle)
        return self.get_entity_at(opponent_field)

    def get_optical_neighbors(self, hex_id: HexID) -> List[HexID]:
        """
        Gibt alle **optischen Nachbarn** einer HexID zurück (für UI-Rendering).
        Enthält ALLE sichtbar verbundenen Felder, inkl. Backrows und Preview.
        """
        if not self.is_valid_position(hex_id):
            return []
        return self._optical_neighbors.get(hex_id, [])

    def get_idle_neighbors(self, hex_id: HexID) -> Dict[str, List[HexID]]:
        """
        Gibt die Player- und Opponent-Nachbarn eines Idle-Felds zurück.
        Beispiel: 3011 → {"player": [1111, 1112, 1213], "opponent": [2111, 2112, 2213]}
        """
        if hex_id not in self._idle_neighbors:
            return {"player": [], "opponent": []}
        return self._idle_neighbors[hex_id]

    def get_opponent_field(self, hex_id: HexID) -> Optional[HexID]:
        """
        Gibt das gegenüberliegende Feld zurück (gleiche Endnummer).
        Beispiel: 1213 → 2213
        """
        if not self.is_valid_position(hex_id):
            return None

        if hex_id.area == HexID.AREA_PLAYER:
            return HexID(f"2{hex_id.idle_count}{hex_id.number:02d}")
        elif hex_id.area == HexID.AREA_OPPONENT:
            return HexID(f"1{hex_id.idle_count}{hex_id.number:02d}")
        else:
            return None  # Kein gegenüberliegendes Feld für andere Bereiche

    # --- Platzierung von Entities ---
    def place_entity(self, hex_id: HexID, entity: BaseEntity) -> bool:
        """Platziert eine Entity auf einem Hexfeld. Erlaubt 1 Figur + 1 Location + 1 Effekt + 1 Vehicle pro Feld."""
        if not self.is_valid_position(hex_id):
            return False

        if entity.type == "figure":
            self._figures[hex_id.raw_id] = entity
        elif entity.type == "location":
            self._locations[hex_id.raw_id] = entity
        elif entity.type == "effect":
            self._effects[hex_id.raw_id] = entity
        elif entity.type == "vehicle":
            self._vehicles[hex_id.raw_id] = entity
        else:
            return False  # Unbekannter Typ

        return True

    def remove_entity(self, hex_id: HexID, entity_type: str) -> Optional[T]:
        """Entfernt eine Entity von einem Hexfeld."""
        if entity_type == "figure":
            return self._figures.pop(hex_id, None)
        elif entity_type == "location":
            return self._locations.pop(hex_id, None)
        elif entity_type == "effect":
            return self._effects.pop(hex_id, None)
        elif entity_type == "vehicle":
            return self._vehicles.pop(hex_id, None)
        return None

    def _is_occupied(self, hex_id: HexID) -> bool:
        """Prüft, ob ein Hexfeld belegt ist."""
        return (
            hex_id in self._figures or
            hex_id in self._locations or
            hex_id in self._effects or
            hex_id in self._vehicles
        )

    # --- Abfrage von Entities ---
    def get_figure_at(self, hex_id: HexID) -> Optional[BaseEntity]:
        return self._figures.get(hex_id.raw_id)

    def get_location_at(self, hex_id: HexID) -> Optional[BaseEntity]:
        return self._locations.get(hex_id.raw_id)

    def get_effect_at(self, hex_id: HexID) -> Optional[BaseEntity]:
        return self._effects.get(hex_id.raw_id)

    def get_vehicle_at(self, hex_id: HexID) -> Optional[BaseEntity]:
        return self._vehicles.get(hex_id.raw_id)

    def get_entities_on_hex(self, hex_id: HexID) -> List[BaseEntity]:
        """Gibt alle Entities (Figuren, Locations, Effekte, Vehicles) auf einem Hexfeld zurück."""
        entities = []
        if hex_id.raw_id in self._figures:
            entities.append(self._figures[hex_id.raw_id])
        if hex_id.raw_id in self._locations:
            entities.append(self._locations[hex_id.raw_id])
        if hex_id.raw_id in self._effects:
            entities.append(self._effects[hex_id.raw_id])
        if hex_id.raw_id in self._vehicles:
            entities.append(self._vehicles[hex_id.raw_id])
        return entities

    def get_entity_at(self, hex_id: HexID) -> Optional[BaseEntity]:
        """
        Gibt die erste Entity auf einem Hexfeld zurück (für Abwärtskompatibilität).
        Falls mehrere Entities vorhanden sind, wird die Priorität: Figur > Location > Effekt > Vehicle verwendet.
        """
        if hex_id.raw_id in self._figures:
            return self._figures[hex_id.raw_id]
        elif hex_id.raw_id in self._locations:
            return self._locations[hex_id.raw_id]
        elif hex_id.raw_id in self._effects:
            return self._effects[hex_id.raw_id]
        elif hex_id.raw_id in self._vehicles:
            return self._vehicles[hex_id.raw_id]
        return None

    # --- Idol-Kontrolle ---
    def get_idle_fields(self) -> List[HexID]:
        """Gibt alle Idle-Felder (3011, 3012, 3013) zurück."""
        return [HexID("3011"), HexID("3012"), HexID("3013")]

    def set_idle_control(self, idle_id: HexID, controller: Optional[str]) -> None:
        """
        Setzt die Kontrolle über ein Idol-Feld (z. B. "player" oder "opponent").
        """
        if idle_id in self._idle_control:
            self._idle_control[idle_id] = controller

    def get_idle_controller(self, idle_id: HexID) -> Optional[str]:
        """Gibt den aktuellen Controller eines Idol-Felds zurück."""
        return self._idle_control.get(idle_id)

    # --- Hilfsfunktionen ---
    def clear_board(self) -> None:
        """Löscht alle Entities vom Board."""
        self._figures.clear()
        self._locations.clear()
        self._effects.clear()
        self._vehicles.clear()
        for idle_id in self._idle_control:
            self._idle_control[idle_id] = None

    def get_all_figures(self) -> List[Figure]:
        """Gibt alle Figuren auf dem Board zurück."""
        return list(self._figures.values())

    def get_all_locations(self) -> List[Location]:
        """Gibt alle Locations auf dem Board zurück."""
        return list(self._locations.values())

    def get_all_effects(self) -> List[Effect]:
        """Gibt alle Effekte auf dem Board zurück."""
        return list(self._effects.values())

    def get_all_vehicles(self) -> List[Vehicle]:
        """Gibt alle Vehicles auf dem Board zurück."""
        return list(self._vehicles.values())

    def is_field_occupied(self, hex_id: HexID) -> bool:
        """Prüft, ob ein Feld belegt ist."""
        return self._is_occupied(hex_id)

    # --- Dynamische Sichtbarkeitssteuerung ---
    def set_preview_visible(self, player_preview: bool = True, opponent_preview: bool = True) -> None:
        """
        Schaltet die Sichtbarkeit der Preview-Bereiche (4xxx, 5xxx) um.
        Wird z. B. in Runde 0 aufgerufen, um Preview-Felder sichtbar zu machen.
        """
        for hex_id in self._valid_hex_ids:
            if hex_id.area == HexID.AREA_PREVIEW_PLAYER and player_preview:
                self._visibility[hex_id] = True
            elif hex_id.area == HexID.AREA_PREVIEW_OPPONENT and opponent_preview:
                self._visibility[hex_id] = True

    def set_backrow_visible(self, player_backrow: bool = True, opponent_backrow: bool = True) -> None:
        """
        Schaltet die Sichtbarkeit der Backrow-Bereiche (6xxx, 7xxx) um.
        Wird z. B. genutzt, wenn ein Effekt/Transporter platziert wird.
        """
        for hex_id in self._valid_hex_ids:
            if hex_id.area == HexID.AREA_BACK_PLAYER and player_backrow:
                self._visibility[hex_id] = True
            elif hex_id.area == HexID.AREA_BACK_OPPONENT and opponent_backrow:
                self._visibility[hex_id] = True

    def set_special_visible(self, hex_id: HexID, visible: bool = True) -> bool:
        """
        Schaltet die Sichtbarkeit eines Spezialfelds (8xxx, 9xxx) um.
        Wird z. B. genutzt, wenn ein Effektfeld aktiviert wird.
        """
        if hex_id.area not in [8, 9]:
            return False
        self._visibility[hex_id] = visible
        return True