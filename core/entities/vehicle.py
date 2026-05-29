from core.entities.base_entity import BaseEntity
from typing import Optional, Dict, Any

class Vehicle(BaseEntity):
    """Repräsentiert ein Transportmittel im Spiel."""

    def __init__(self, *args, **kwargs):
        kwargs["type"] = "vehicle"
        # Extrahiere fahrzeugspezifische Attribute
        capacity = kwargs.pop("capacity", 1)
        super().__init__(*args, **kwargs)
        self.capacity = capacity

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vehicle':
        entity = super().from_dict(data)
        entity.__class__ = Vehicle
        entity.capacity = data.get("capacity", 1)
        return entity

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["capacity"] = self.capacity
        return data