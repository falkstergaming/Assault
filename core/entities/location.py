from core.entities.base_entity import BaseEntity
from typing import Optional, Dict, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from core.game.board import Board  # Nur für Typ-Hints, nicht zur Laufzeit


class Location(BaseEntity):
    """
    Repräsentiert eine Location im Spiel.
    Erbt von BaseEntity und fügt locationsspezifische Logik hinzu.
    Self-Buffs wirken automatisch, wenn eine Figur auf der Location steht.
    """

    def __init__(self, *args, **kwargs):
        # Setze Default-Typ auf "location"
        kwargs["type"] = "location"
        super().__init__(*args, **kwargs)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        """Erstellt eine Location aus einem Dictionary."""
        entity = super().from_dict(data)
        entity.__class__ = Location
        return entity

    def _is_figure_on_location(self, hex_id: str) -> bool:
        """
        Hilfsfunktion: Prüft, ob eine Figur auf dieser Location steht.
        In einer echten Implementierung würde diese Methode das Board abfragen.
        """
        # Platzhalter - in echten Code würde man z.B. board.get_figure_at(hex_id) verwenden
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert die Location in ein Dictionary."""
        return super().to_dict()