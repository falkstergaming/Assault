"""
Base Entity Class für Sturm auf Grayskull.
Enthält gemeinsame Attribute und Methoden für alle Entities (Figuren, Locations, Effekte, Vehicles).
Inkl. JSON-Ladefunktionalität.
"""

from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, field, asdict
import json
from pathlib import Path

# --- Buff-Struktur ---
@dataclass
class Buff:
    """Repräsentiert einen Buff mit Wert, Ziel und Ziel-Typ."""
    value: int                  # Buff-Value (positiv/negativ)
    target: Optional[str] = None  # Ziel: "self", "Good", "Evil", "Felslinge", ID, etc.
    target_type: Optional[str] = None  # Typ: "self", "faction", "pool", "tag", "id"

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Buff in Dictionary für JSON-Serialisierung."""
        return {
            "value": self.value,
            "target": self.target,
            "target_type": self.target_type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Buff':
        """Erstellt Buff aus Dictionary (JSON-Deserialisierung)."""
        return cls(
            value=data.get("value", 0),
            target=data.get("target"),
            target_type=data.get("target_type")
        )

# --- Immunitäts-Struktur ---
@dataclass
class Immunity:
    """Repräsentiert Immunitäten gegen bestimmte Buffs."""
    buff_types: List[str] = field(default_factory=list)  # ["targeted_buff", "faction_buff"]
    buff_targets: List[str] = field(default_factory=list)  # ["Spy", "Felslinge", "Evil"]
    buff_values: Optional[str] = None  # "negative", "positive", None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "buff_types": self.buff_types,
            "buff_targets": self.buff_targets,
            "buff_values": self.buff_values
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Immunity':
        return cls(
            buff_types=data.get("buff_types", []),
            buff_targets=data.get("buff_targets", []),
            buff_values=data.get("buff_values")
        )

# --- Mobility-Struktur ---
@dataclass
class Mobility:
    """Repräsentiert Bewegungs-Eigenschaften."""
    type: str = "ground"  # "ground", "flying", "special"
    range: int = 1        # Anzahl Hexfelder pro Marsch
    ignores_idle_split: bool = False  # Ignoriert Might-Teilung bei 2 Idles?

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "range": self.range,
            "ignores_idle_split": self.ignores_idle_split
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Mobility':
        return cls(
            type=data.get("type", "ground"),
            range=data.get("range", 1),
            ignores_idle_split=data.get("ignores_idle_split", False)
        )

# --- Special Abilities-Struktur ---
@dataclass
class SpecialAbilities:
    """Repräsentiert spezielle Fähigkeiten."""
    placing: bool = False           # Darf Positionen anderer Figuren ändern?
    self_alt_activation: bool = False  # Kann Alt-State selbst aktivieren?
    credit: int = 0                # Kredit für AP-Überziehung

    def to_dict(self) -> Dict[str, Any]:
        return {
            "placing": self.placing,
            "self_alt_activation": self.self_alt_activation,
            "credit": self.credit
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpecialAbilities':
        return cls(
            placing=data.get("placing", False),
            self_alt_activation=data.get("self_alt_activation", False),
            credit=data.get("credit", 0)
        )

class BaseEntity:
    """
    Basis-Klasse für alle Entities (Figuren, Locations, Effekte, Vehicles).
    Enthält gemeinsame Attribute und Methoden für Might-Berechnung, Buffs, Immunitäten, etc.
    """

    def __init__(
        self,
        id: str,
        name: str,
        type: str,
        base_might: int = 0,
        alt: bool = False,
        alt_entity: Optional[str] = None,
        might_split: List[float] = None,
        mighty_threshold: int = 20,
        immunity: Optional[Immunity] = None,
        buffs: Optional[Dict[str, List[Buff]]] = None,
        tags: List[str] = None,
        mobility: Optional[Mobility] = None,
        scout_vision: int = 1,
        special_abilities: Optional[SpecialAbilities] = None
    ):
        self.id = id
        self.name = name
        self.type = type
        self.base_might = base_might
        self.alt = alt
        self.alt_entity = alt_entity
        self.might_split = might_split if might_split is not None else [0.5, 0.5]
        self.mighty_threshold = mighty_threshold
        self.immunity = immunity if immunity is not None else Immunity()
        self.buffs = buffs if buffs is not None else {
            "self": [],
            "neighbor": [],
            "opponent": [],
            "faction": [],
            "targeted": []
        }
        self.tags = tags if tags is not None else []
        self.mobility = mobility if mobility is not None else Mobility()
        self.scout_vision = scout_vision
        self.special_abilities = special_abilities if special_abilities is not None else SpecialAbilities()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEntity':
        """
        Erstellt eine BaseEntity aus einem Dictionary (JSON-Deserialisierung).
        """
        buffs = {}
        if "buffs" in data:
            for buff_type, buff_list in data["buffs"].items():
                buffs[buff_type] = [Buff.from_dict(b) for b in buff_list]

        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            type=data.get("type", "figure"),
            base_might=data.get("base_might", 0),
            alt=data.get("alt", False),
            alt_entity=data.get("alt_entity"),
            might_split=data.get("might_split", [0.5, 0.5]),
            mighty_threshold=data.get("mighty_threshold", 20),
            immunity=Immunity.from_dict(data.get("immunity", {})),
            buffs=buffs,
            tags=data.get("tags", []),
            mobility=Mobility.from_dict(data.get("mobility", {})),
            scout_vision=data.get("scout_vision", 1),
            special_abilities=SpecialAbilities.from_dict(data.get("special_abilities", {}))
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert die Entity in ein Dictionary (JSON-Serialisierung).
        """
        buffs = {}
        for buff_type, buff_list in self.buffs.items():
            buffs[buff_type] = [b.to_dict() for b in buff_list]

        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "base_might": self.base_might,
            "alt": self.alt,
            "alt_entity": self.alt_entity,
            "might_split": self.might_split,
            "mighty_threshold": self.mighty_threshold,
            "immunity": self.immunity.to_dict(),
            "buffs": buffs,
            "tags": self.tags,
            "mobility": self.mobility.to_dict(),
            "scout_vision": self.scout_vision,
            "special_abilities": self.special_abilities.to_dict()
        }

    def save_to_json(self, file_path: Union[str, Path]) -> None:
        """Speichert die Entity als JSON-Datei."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_from_json(file_path: Union[str, Path]) -> 'BaseEntity':
        """Lädt eine Entity aus einer JSON-Datei."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return BaseEntity.from_dict(data)

    # --- Might-Berechnung ---
    def calculate_might(self, neighbor_entities: List['BaseEntity'], opponent=None, location=None) -> int:
        """
        Berechnet den Might-Wert der Entity inkl. aller Buffs, Immunitäten und Might-Split.
        Folgt der strikten Prioritäten-Reihenfolge:
        1. Base Might
        2. Self-Buffs
        3. Neighbor-Buffs
        4. Opponent-Buffs
        5. Faction-Buffs
        6. Targeted-Buffs
        7. Location-Buffs (falls location übergeben)
        """
        from core.utils.global_constants import MIN_MIGHT

        might = self.base_might

        # 1. Self-Buffs
        for buff in self.buffs.get("self", []):
            might += buff.value  # ✅ buff.value statt buff["value"]

        # 2. Neighbor-Buffs (jetzt mit Entities)
        for neighbor in neighbor_entities:
            if hasattr(neighbor, 'buffs'):  # ✅ Prüft, ob das Objekt Buffs hat (alle Entities haben buffs)
                for buff in neighbor.buffs.get("neighbor", []):
                    # Prüfe Target-Einschränkungen (falls vorhanden)
                    if buff.get("target_type") is None or buff.get("target_type") == "self" or buff.get("target") == self.faction:
                        might += buff.value  # ✅ buff.value statt buff["value"]

        # 3. Opponent-Buffs (von gegenüberliegender Entity)
        if opponent:
            for buff in opponent.buffs["opponent"]:
                if self._matches_buff_target(buff):
                    if not self._is_immune(buff):
                        might += buff.value

        # 4. Faction-Buffs (globale Buffs auf Faction/Tag)
        for buff in self.buffs["faction"]:
            if self._matches_buff_target(buff):
                if not self._is_immune(buff):
                    might += buff.value

        # 5. Targeted-Buffs (spezifische Buffs)
        for buff in self.buffs["targeted"]:
            if self._matches_buff_target(buff):
                if not self._is_immune(buff):
                    might += buff.value

        # 6. Location-Buffs (falls auf einer Location)
        if location:
            for buff in location.buffs["self"]:
                if self._matches_buff_target(buff):
                    if not self._is_immune(buff):
                        might += buff.value

        # Minimum: 0
        return max(MIN_MIGHT, might)

    def _is_immune(self, buff: Buff) -> bool:
        """
        Prüft, ob die Entity immun gegen einen Buff ist.
        """
        # 1. Immunität gegen Buff-Typ
        if buff.target_type in self.immunity.buff_types:
            return True

        # 2. Immunität gegen Buff-Target
        if buff.target in self.immunity.buff_targets:
            return True

        # 3. Immunität gegen Buff-Value (negativ/positiv)
        if self.immunity.buff_values == "negative" and buff.value < 0:
            return True
        if self.immunity.buff_values == "positive" and buff.value > 0:
            return True
        if self.immunity.buff_values == "all":
            return True

        return False

    def _matches_buff_target(self, buff: Buff) -> bool:
        """
        Prüft, ob ein Buff auf diese Entity zutrifft.
        """
        if buff.target is None and buff.target_type is None:
            return True  # Buff wirkt auf alle

        if buff.target_type == "self":
            return True  # Selbst-Referenz

        if buff.target_type == "faction":
            return buff.target in self.tags or buff.target == self.name

        if buff.target_type == "tag":
            return buff.target in self.tags

        if buff.target_type == "id":
            return buff.target == self.id

        return False

    def is_mighty(self, current_might: Optional[int] = None) -> bool:
        """
        Prüft, ob die Entity "Mighty" ist.
        """
        if current_might is None:
            current_might = self.calculate_might(neighbors=[], opponent=None)
        return current_might >= self.mighty_threshold

    def activate_alt_state(self) -> None:
        """Aktiviert/deaktiviert den Alt-State (falls freigeschaltet)."""
        self.alt = not self.alt

    def get_might_split(self) -> List[float]:
        """Gibt den Might-Split zurück."""
        return self.might_split