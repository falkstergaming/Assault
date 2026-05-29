from core.entities.base_entity import BaseEntity
from typing import Optional, Dict, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from core.game.board import Board  # Nur für Typ-Hints, nicht zur Laufzeit

class Figure(BaseEntity):
    """Repräsentiert eine Figur im Spiel."""

    def __init__(self, *args, **kwargs):
        kwargs["type"] = "figure"
        # Extrahiere figurenspezifische Attribute
        self_alt_activation = kwargs.pop("self_alt_activation", False)
        super().__init__(*args, **kwargs)
        self.self_alt_activation = self_alt_activation

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Figure':
        entity = super().from_dict(data)
        entity.__class__ = Figure
        entity.self_alt_activation = data.get("self_alt_activation", False)
        return entity

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["self_alt_activation"] = self.self_alt_activation
        return data

    def activate_alt_state(self, has_enough_ap: bool = True) -> bool:
        if not self.self_alt_activation and not has_enough_ap:
            return False
        self.alt = not self.alt
        return True

    def can_activate_alt_state(self) -> bool:
        return self.self_alt_activation