"""
Effect Entity Class für Sturm auf Grayskull.
Erbt von BaseEntity und fügt effektspezifische Attribute hinzu (z. B. Kosten, Dauer).
"""

from core.entities.base_entity import BaseEntity
from typing import Optional

class Effect(BaseEntity):
    """
    Repräsentiert einen Effekt im Spiel.
    Enthält zusätzliche Attribute wie Kosten und Dauer.
    """

    def __init__(
        self,
        *args,
        cost: int = 0,
        activation_cost: int = 0,
        duration: str = "once",
        bonus_ap: int = 0,
        **kwargs
    ):
        # Setze Default-Typ auf "effect"
        kwargs["type"] = "effect"
        super().__init__(*args, **kwargs)
        self.cost = cost
        self.activation_cost = activation_cost
        self.duration = duration  # "once" oder "per_round"
        self.bonus_ap = bonus_ap

    @classmethod
    def from_dict(cls, data: dict) -> 'Effect':
        """Erstellt einen Effect aus einem Dictionary."""
        entity = super().from_dict(data)
        entity.__class__ = Effect
        entity.cost = data.get("cost", 0)
        entity.activation_cost = data.get("activation_cost", 0)
        entity.duration = data.get("duration", "once")
        entity.bonus_ap = data.get("bonus_ap", 0)
        return entity

    def to_dict(self) -> dict:
        """Konvertiert den Effect in ein Dictionary."""
        data = super().to_dict()
        data.update({
            "cost": self.cost,
            "activation_cost": self.activation_cost,
            "duration": self.duration,
            "bonus_ap": self.bonus_ap
        })
        return data