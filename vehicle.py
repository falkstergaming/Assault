"""
Vehicle Entity Class für Sturm auf Grayskull.
Erbt von BaseEntity und fügt fahrzeugspezifische Attribute hinzu (z. B. Kapazität).
"""

from core.entities.base_entity import BaseEntity

class Vehicle(BaseEntity):
    """
    Repräsentiert ein Transportmittel im Spiel.
    Enthält zusätzliche Attribute wie Kapazität.
    """

    def __init__(self, *args, capacity: int = 1, **kwargs):
        # Setze Default-Typ auf "vehicle"
        kwargs["type"] = "vehicle"
        super().__init__(*args, **kwargs)
        self.capacity = capacity  # Max. Anzahl Figuren

    @classmethod
    def from_dict(cls, data: dict) -> 'Vehicle':
        """Erstellt ein Vehicle aus einem Dictionary."""
        entity = super().from_dict(data)
        entity.__class__ = Vehicle
        entity.capacity = data.get("capacity", 1)
        return entity

    def to_dict(self) -> dict:
        """Konvertiert das Vehicle in ein Dictionary."""
        data = super().to_dict()
        data["capacity"] = self.capacity
        return data