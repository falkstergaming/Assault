from core.entities.base_entity import BaseEntity
from typing import Optional, Dict, Any


class Figure(BaseEntity):
    """
    Repräsentiert eine Figur im Spiel.
    Erbt von BaseEntity und fügt figurenspezifische Attribute/Methoden hinzu.
    """

    def __init__(self, *args, **kwargs):
        # Setze Default-Typ auf "figure"
        kwargs["type"] = "figure"
        # Figur-spezifische Attribute
        kwargs["self_alt_activation"] = kwargs.get("self_alt_activation", False)
        super().__init__(*args, **kwargs)
        self.self_alt_activation = kwargs.get("self_alt_activation", False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Figure':
        """Erstellt eine Figure aus einem Dictionary."""
        entity = super().from_dict(data)
        entity.__class__ = Figure
        entity.self_alt_activation = data.get("self_alt_activation", False)
        return entity

    # --- Alt-State für Figuren ---
    def activate_alt_state(self, has_enough_ap: bool = True) -> bool:
        """
        Aktiviert/deaktiviert den Alt-State der Figur.
        - Nur möglich, wenn self_alt_activation = True.
        - Gibt True zurück, wenn erfolgreich.
        """
        if not self.self_alt_activation and not has_enough_ap:
            return False
        self.alt = not self.alt
        return True

    def can_activate_alt_state(self) -> bool:
        """Prüft, ob die Figur ihren Alt-State selbst aktivieren darf."""
        return self.self_alt_activation

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert die Figur in ein Dictionary (erweitert BaseEntity.to_dict)."""
        data = super().to_dict()
        data["self_alt_activation"] = self.self_alt_activation
        return data