from core.entities.base_entity import BaseEntity
from typing import Optional, Dict, Any


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

    # --- Buff-Logik für Locations ---
    def calculate_might(self, neighbor_entities: list = None, opponent=None, location=None, hex_id: Optional[str] = None) -> int:
        """
        Berechnet den Might-Wert der Location.
        Self-Buffs wirken nur, wenn eine Figur auf der Location steht.
        """
        # Rufe die Basis-Methode auf, aber überscheibe die Self-Buff-Logik
        might = self.base_might
        neighbor_entities = neighbor_entities or []

        # Self-Buffs wirken nur, wenn eine Figur auf der Location steht
        if hex_id and self._is_figure_on_location(hex_id):
            for buff in self.buffs["self"]:
                might += buff.value

        # Neighbor-Buffs (von angrenzenden Entities)
        for neighbor in neighbor_entities:
            for buff in neighbor.buffs["neighbor"]:
                if (buff.target_type == "faction" and buff.target and buff.target in (self.faction or "")) or \
                   (buff.target_type == "tag" and buff.target in self.tags) or \
                   (buff.target_type == "id" and buff.target == self.id):
                    might += buff.value

        # Opponent-Buffs
        if opponent:
            for buff in opponent.buffs["opponent"]:
                might += buff.value

        # Faction-Buffs
        for buff in self.buffs["faction"]:
            if buff.target_type == "faction" and buff.target and buff.target in (self.faction or ""):
                might += buff.value

        # Targeted-Buffs
        for buff in self.buffs["targeted"]:
            might += buff.value

        return max(0, might)

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