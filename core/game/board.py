"""
Board-Modul für Sturm auf Grayskull.
Verwaltet das Spielfeld mit expliziten Hex-IDs, dynamischer Sichtbarkeit,
und VOLLSTÄNDIGEN Nachbarn-Beziehungen (für Zeichnen und Spiel-Logik).

Refaktorisiert mit:
- BoardInitializer für Initialisierungs-Logik
- NeighborManager für Nachbarn-Beziehungen
- IdleManager für Idle-Kontrolle + Siegbedingungen
"""
from core.utils.hex_id import HexID
from typing import List, Dict, Set, Optional, TypeVar, TYPE_CHECKING
from core.entities.base_entity import BaseEntity
from core.entities.figure import Figure
from core.entities.location import Location
from core.entities.effect import Effect
from core.entities.vehicle import Vehicle
from core.game.board_initializer import BoardInitializer
from core.game.neighbor_manager import NeighborManager
from core.game.idle_manager import IdleManager

if TYPE_CHECKING:
    from core.entities.figure import Figure
    from core.entities.location import Location
    from core.entities.effect import Effect
    from core.entities.vehicle import Vehicle

T = TypeVar('T', BaseEntity, Figure, Location, Effect, Vehicle)


class Board:
    """
    Verwaltet das Spielfeld mit expliziten Hex-IDs, dynamischer Sichtbarkeit
    und vollständigen Nachbarn-Beziehungen für:
    - Spiel-Logik (Marsch, Might-Berechnung)
    - UI-Rendering (optische Nachbarn)
    
    Nutzt:
    - BoardInitializer für Initialisierung
    - NeighborManager für Nachbarn-Logik
    - IdleManager für Idle-Kontrolle
    """

    def __init__(self):
        """Initialisiert das Board mit Managern für verschiedene Verantwortlichkeiten."""
        # --- Initialisierung ---
        self._valid_hex_ids: Set[HexID] = BoardInitializer.initialize_valid_hex_ids()
        self._visibility: Dict[HexID, bool] = BoardInitializer.initialize_visibility(self._valid_hex_ids)
        
        # Nachbarn initialisieren
        logical_neighbors = BoardInitializer.initialize_logical_neighbors()
        optical_neighbors = BoardInitializer.initialize_optical_neighbors()
        idle_neighbors = BoardInitializer.initialize_idle_neighbors()
        
        # Manager erstellen
        self.neighbor_manager = NeighborManager(
            logical_neighbors=logical_neighbors,
            optical_neighbors=optical_neighbors,
            idle_neighbors=idle_neighbors
        )
        self.idle_manager = IdleManager()

        # Speichere Entities nach Typ pro Hexfeld
        self._figures: Dict[str, BaseEntity] = {}
        self._locations: Dict[str, BaseEntity] = {}
        self._effects: Dict[str, BaseEntity] = {}
        self._vehicles: Dict[str, BaseEntity] = {}

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
        """Gibt den aktuellen Sichtbarkeitsstatus eines Hexfelds zurück."""
        return self._visibility.get(hex_id, False)

    # --- Nachbarn-Abfrage (delegiert an NeighborManager) ---
    def get_neighbors(self, hex_id: HexID) -> List[BaseEntity]:
        """Gibt alle Entities auf den Nachbar-Feldern zurück."""
        neighbor_ids = self.neighbor_manager.get_logical_neighbors(hex_id)
        neighbors = []
        for nid in neighbor_ids:
            entities = self.get_entities_on_hex(nid)
            neighbors.extend(entities)
        return neighbors

    def get_neighbor_entities(self, hex_id: HexID) -> List[BaseEntity]:
        """Alias für get_neighbors() zur Kompatibilität mit MightCalculator."""
        return self.get_neighbors(hex_id)

    def get_opponent_entity(self, hex_id: HexID) -> Optional[BaseEntity]:
        """Gibt die Entity vom gegenüberliegenden Feld zurück."""
        opponent_field = self.get_opponent_field(hex_id)
        if opponent_field is None:
            return None
        return self.get_entity_at(opponent_field)

    def get_optical_neighbors(self, hex_id: HexID) -> List[HexID]:
        """Gibt alle optischen Nachbarn einer HexID zurück (für UI-Rendering)."""
        if not self.is_valid_position(hex_id):
            return []
        return self.neighbor_manager.get_optical_neighbors(hex_id)

    def get_idle_neighbors(self, hex_id: HexID) -> Dict[str, List[HexID]]:
        """Gibt die Player- und Opponent-Nachbarn eines Idle-Felds zurück."""
        return self.neighbor_manager.get_idle_neighbors(hex_id)

    def get_opponent_field(self, hex_id: HexID) -> Optional[HexID]:
        """Gibt das gegenüberliegende Feld zurück (gleiche Endnummer)."""
        return self.neighbor_manager.get_opponent_field(hex_id)

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
            return False

        return True

    def remove_entity(self, hex_id: HexID, entity_type: str) -> Optional[T]:
        """Entfernt eine Entity von einem Hexfeld."""
        if entity_type == "figure":
            return self._figures.pop(hex_id.raw_id, None)
        elif entity_type == "location":
            return self._locations.pop(hex_id.raw_id, None)
        elif entity_type == "effect":
            return self._effects.pop(hex_id.raw_id, None)
        elif entity_type == "vehicle":
            return self._vehicles.pop(hex_id.raw_id, None)
        return None

    def _is_occupied(self, hex_id: HexID) -> bool:
        """Prüft, ob ein Hexfeld belegt ist."""
        return (
            hex_id.raw_id in self._figures or
            hex_id.raw_id in self._locations or
            hex_id.raw_id in self._effects or
            hex_id.raw_id in self._vehicles
        )

    # --- Entity-Dict Hilfsfunktion ---
    def _get_entity_dicts(self) -> List[Dict[str, BaseEntity]]:
        """Gibt alle Entity-Dicts in Prioritätsreihenfolge zurück."""
        return [
            self._figures,
            self._locations,
            self._effects,
            self._vehicles
        ]

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
        """Gibt alle Entities auf einem Hexfeld zurück."""
        entities = []
        hex_id_str = hex_id.raw_id
        for entity_dict in self._get_entity_dicts():
            if hex_id_str in entity_dict:
                entities.append(entity_dict[hex_id_str])
        return entities

    def get_entity_at(self, hex_id: HexID) -> Optional[BaseEntity]:
        """
        Gibt die erste Entity auf einem Hexfeld zurück (für Abwärtskompatibilität).
        Priorität: Figur > Location > Effekt > Vehicle
        """
        hex_id_str = hex_id.raw_id
        for entity_dict in self._get_entity_dicts():
            if hex_id_str in entity_dict:
                return entity_dict[hex_id_str]
        return None

    # --- Idol-Kontrolle (delegiert an IdleManager) ---
    def get_idle_fields(self) -> List[HexID]:
        """Gibt alle Idle-Felder (3011, 3012, 3013) zurück."""
        return self.idle_manager.get_idle_fields()

    def set_idle_control(self, idle_id: HexID, controller: Optional[str]) -> None:
        """Setzt die Kontrolle über ein Idol-Feld (z. B. "player" oder "opponent")."""
        self.idle_manager.set_idle_control(idle_id, controller)

    def get_idle_controller(self, idle_id: HexID) -> Optional[str]:
        """Gibt den aktuellen Controller eines Idol-Felds zurück."""
        return self.idle_manager.get_idle_controller(idle_id)

    def get_player_idle_count(self) -> int:
        """Gibt die Anzahl der vom Spieler kontrollierten Idle-Felder zurück."""
        return self.idle_manager.get_player_idle_count()

    def get_opponent_idle_count(self) -> int:
        """Gibt die Anzahl der vom Gegner kontrollierten Idle-Felder zurück."""
        return self.idle_manager.get_opponent_idle_count()

    def check_victory(self) -> Optional[str]:
        """Prüft, ob eine Faction gewonnen hat (2 von 3 Idles)."""
        return self.idle_manager.check_victory()

    # --- Hilfsfunktionen ---
    def clear_board(self) -> None:
        """Löscht alle Entities vom Board."""
        self._figures.clear()
        self._locations.clear()
        self._effects.clear()
        self._vehicles.clear()
        self.idle_manager.reset()

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
        """Schaltet die Sichtbarkeit der Preview-Bereiche (4xxx, 5xxx) um."""
        for hex_id in self._valid_hex_ids:
            if hex_id.area == HexID.AREA_PREVIEW_PLAYER and player_preview:
                self._visibility[hex_id] = True
            elif hex_id.area == HexID.AREA_PREVIEW_OPPONENT and opponent_preview:
                self._visibility[hex_id] = True

    def set_backrow_visible(self, player_backrow: bool = True, opponent_backrow: bool = True) -> None:
        """Schaltet die Sichtbarkeit der Backrow-Bereiche (6xxx, 7xxx) um."""
        for hex_id in self._valid_hex_ids:
            if hex_id.area == HexID.AREA_BACK_PLAYER and player_backrow:
                self._visibility[hex_id] = True
            elif hex_id.area == HexID.AREA_BACK_OPPONENT and opponent_backrow:
                self._visibility[hex_id] = True

    def set_special_visible(self, hex_id: HexID, visible: bool = True) -> bool:
        """Schaltet die Sichtbarkeit eines Spezialfelds (8xxx, 9xxx) um."""
        if hex_id.area not in [8, 9]:
            return False
        self._visibility[hex_id] = visible
        return True
