from core.entities.base_entity import BaseEntity
from typing import Optional, Dict, Any

class Vehicle(BaseEntity):
    """
    Repräsentiert ein Transportmittel im Spiel.
    Erbt von BaseEntity und fügt fahrzeugspezifische Attribute hinzu (z. B. Kapazität).
    """

    def __init__(self, *args, **kwargs):
        # Setze Default-Typ auf "vehicle"
        kwargs["type"] = "vehicle"
        # Fahrzeug-spezifische Attribute
        kwargs["capacity"] = kwargs.get("capacity", 1)
        super().__init__(*args, **kwargs)
        self.capacity = kwargs.get("capacity", 1)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vehicle':
        """Erstellt ein Vehicle aus einem Dictionary."""
        entity = super().from_dict(data)
        entity.__class__ = Vehicle
        entity.capacity = data.get("capacity", 1)
        return entity

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert das Vehicle in ein Dictionary."""
        data = super().to_dict()
        data["capacity"] = self.capacity
        return data