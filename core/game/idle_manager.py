"""
Idle Manager - Verantwortlich für die Idle-Feld Kontrolle.
Verwaltet welche Faction die Idle-Felder kontrolliert und prüft Siegbedingungen.
"""

from typing import Dict, List, Optional
from core.utils.hex_id import HexID


class IdleManager:
    """Verwaltet die Kontrolle über Idle-Felder und Siegbedingungen."""

    def __init__(self):
        """Initialisiert die Idle-Kontrolle für alle 3 Idle-Felder."""
        self._idle_control: Dict[HexID, Optional[str]] = {
            HexID("3011"): None,
            HexID("3012"): None,
            HexID("3013"): None
        }

    def get_idle_fields(self) -> List[HexID]:
        """Gibt alle Idle-Felder (3011, 3012, 3013) zurück."""
        return list(self._idle_control.keys())

    def set_idle_control(self, idle_id: HexID, controller: Optional[str]) -> None:
        """Setzt die Kontrolle über ein Idol-Feld (z. B. "player" oder "opponent")."""
        if idle_id in self._idle_control:
            self._idle_control[idle_id] = controller

    def get_idle_controller(self, idle_id: HexID) -> Optional[str]:
        """Gibt den aktuellen Controller eines Idol-Felds zurück."""
        return self._idle_control.get(idle_id)

    def get_player_idle_count(self) -> int:
        """Gibt die Anzahl der vom Spieler kontrollierten Idle-Felder zurück."""
        return sum(1 for controller in self._idle_control.values() if controller == "player")

    def get_opponent_idle_count(self) -> int:
        """Gibt die Anzahl der vom Gegner kontrollierten Idle-Felder zurück."""
        return sum(1 for controller in self._idle_control.values() if controller == "opponent")

    def check_victory(self) -> Optional[str]:
        """
        Prüft, ob eine Faction gewonnen hat.
        Siegbedingung: Wer 2 von 3 Idles kontrolliert, gewinnt.
        
        Returns:
            "player" wenn Spieler gewonnen hat
            "opponent" wenn Gegner gewonnen hat
            None wenn noch kein Sieger
        """
        player_count = self.get_player_idle_count()
        opponent_count = self.get_opponent_idle_count()
        
        if player_count >= 2:
            return "player"
        elif opponent_count >= 2:
            return "opponent"
        return None

    def check_idle_control(self, idle_id: HexID) -> Optional[str]:
        """
        Prüft, wer ein bestimmtes Idle-Feld kontrolliert.
        
        Returns:
            "player", "opponent" oder None
        """
        return self.get_idle_controller(idle_id)

    def reset(self) -> None:
        """Setzt alle Idle-Kontrollen zurück."""
        for idle_id in self._idle_control:
            self._idle_control[idle_id] = None
