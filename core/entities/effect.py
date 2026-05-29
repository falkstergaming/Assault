from core.entities.base_entity import BaseEntity
from typing import Optional, Dict, Any

class Effect(BaseEntity):
    """Repräsentiert einen Effekt im Spiel."""

    def __init__(self, *args, **kwargs):
        kwargs["type"] = "effect"
        # Extrahiere effektspezifische Attribute
        duration = kwargs.pop("duration", None)
        super().__init__(*args, **kwargs)
        self.duration = duration

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Effect':
        entity = super().from_dict(data)
        entity.__class__ = Effect
        entity.duration = data.get("duration")
        return entity

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["duration"] = self.duration
        return data

    def activate(self, has_enough_ap: bool = True) -> bool:
        if not has_enough_ap:
            return False
        self.alt = True
        return True

    def deactivate(self) -> None:
        self.alt = False

    def is_active(self) -> bool:
        return self.alt