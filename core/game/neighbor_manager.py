"""
Neighbor Manager - Verantwortlich für alle Nachbarn-Beziehungen.
Enthält Logik für logische Nachbarn, optische Nachbarn und Idle-Nachbarn.
"""

from typing import Dict, List, Optional
from core.utils.hex_id import HexID


class NeighborManager:
    """Verwaltet alle Nachbarn-Beziehungen für das Board."""

    def __init__(
        self,
        logical_neighbors: Dict[HexID, List[HexID]],
        optical_neighbors: Dict[HexID, List[HexID]],
        idle_neighbors: Dict[HexID, Dict[str, List[HexID]]]
    ):
        self._logical_neighbors = logical_neighbors
        self._optical_neighbors = optical_neighbors
        self._idle_neighbors = idle_neighbors

    def get_logical_neighbors(self, hex_id: HexID) -> List[HexID]:
        """Gibt die logischen Nachbarn für Spiel-Logik zurück."""
        return self._logical_neighbors.get(hex_id, [])

    def get_optical_neighbors(self, hex_id: HexID) -> List[HexID]:
        """Gibt die optischen Nachbarn für UI-Rendering zurück."""
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
        if hex_id.area == HexID.AREA_PLAYER:
            return HexID(f"2{hex_id.idle_count}{hex_id.number:02d}")
        elif hex_id.area == HexID.AREA_OPPONENT:
            return HexID(f"1{hex_id.idle_count}{hex_id.number:02d}")
        else:
            return None
