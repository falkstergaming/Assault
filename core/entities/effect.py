from core.entities.base_entity import BaseEntity
from typing import Optional, Dict, Any


class Effect(BaseEntity):
    """
    Repräsentiert einen Effekt im Spiel.
    Erbt von BaseEntity und fügt effektspezifische Attribute/Methoden hinzu.
    """

    def __init__(self, *args, **kwargs):
        # Setze Default-Typ auf "effect"
        kwargs["type"] = "effect"
        # Effekt-spezifische Attribute
        kwargs["duration"] = kwargs.get("duration", None)  # None = dauerhaft
        super().__init__(*args, **kwargs)
        self.duration = kwargs.get("duration", None)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Effect':
        """Erstellt einen Effect aus einem Dictionary."""
        entity = super().from_dict(data)
        entity.__class__ = Effect
        entity.duration = data.get("duration")
        return entity

    # --- Alt-State für Effekte ---
    def activate(self, has_enough_ap: bool = True) -> bool:
        """
        Aktiviert den Alt-State des Effekts (nach Kauf).
        - Kosten: activation_cost (wird extern geprüft, z.B. im AP-Manager).
        - Gibt True zurück, wenn erfolgreich.
        """
        if not has_enough_ap:
            return False
        self.alt = True
        return True

    def deactivate(self) -> None:
        """Deaktiviert den Alt-State des Effekts."""
        self.alt = False

    def is_active(self) -> bool:
        """Prüft, ob der Effekt aktiv (Alt-State) ist."""
        return self.alt

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert den Effekt in ein Dictionary (erweitert BaseEntity.to_dict)."""
        data = super().to_dict()
        data["duration"] = self.duration
        return data