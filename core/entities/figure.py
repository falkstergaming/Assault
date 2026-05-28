"""
Figure Entity Class für Sturm auf Grayskull.
Erbt von BaseEntity und fügt figurenspezifische Logik hinzu.
"""

from core.entities.base_entity import BaseEntity

class Figure(BaseEntity):
    """
    Repräsentiert eine Figur im Spiel.
    Erbt alle Attribute von BaseEntity und fügt figurenspezifische Methoden hinzu.
    """

    def __init__(self, *args, **kwargs):
        # Setze Default-Typ auf "figure"
        kwargs["type"] = "figure"
        super().__init__(*args, **kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> 'Figure':
        """Erstellt eine Figure aus einem Dictionary."""
        entity = super().from_dict(data)
        entity.__class__ = Figure
        return entity