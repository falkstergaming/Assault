"""
Location Entity Class für Sturm auf Grayskull.
Erbt von BaseEntity und fügt locationsspezifische Logik hinzu.
"""

from core.entities.base_entity import BaseEntity

class Location(BaseEntity):
    """
    Repräsentiert eine Location im Spiel (z. B. Idle-Felder).
    Erbt alle Attribute von BaseEntity.
    """

    def __init__(self, *args, **kwargs):
        # Setze Default-Typ auf "location"
        kwargs["type"] = "location"
        super().__init__(*args, **kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> 'Location':
        """Erstellt eine Location aus einem Dictionary."""
        entity = super().from_dict(data)
        entity.__class__ = Location
        return entity