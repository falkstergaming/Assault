from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class Buff:
    """Repräsentiert einen Buff mit Wert, Ziel und Ziel-Typ."""
    value: int                  # Buff-Value (positiv/negativ)
    target: Optional[str] = None  # Ziel: "self", "Good", "Evil", "Felslinge", ID, etc.
    target_type: Optional[str] = None  # Typ: "self", "faction", "pool", "tag", "id"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "target": self.target,
            "target_type": self.target_type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Buff':
        return cls(
            value=data.get("value", 0),
            target=data.get("target"),
            target_type=data.get("target_type")
        )



class BaseEntity:
    """
    Basis-Klasse für alle Entities (Figuren, Locations, Effekte, Vehicles).
    Minimalistische Version mit gemeinsamen Attributen.
    """

    def __init__(
        self,
        id: str,
        name: str,
        type: str,
        base_might: int = 0,
        # Gemeinsame Attribute für alle Entities
        display_name_en: Optional[str] = None,
        display_name_de: Optional[str] = None,
        description: Optional[str] = None,
        faction: Optional[str] = None,
        rarity: Optional[str] = None,
        mobility: str = "ground",  # "ground", "flying", "ether"
        range: str = "melee",      # "melee", "ranged"
        vision: int = 1,
        placing: bool = False,
        AP_credit: int = 0,
        buffs: Optional[Dict[str, List[Buff]]] = None,
        tags: Optional[List[str]] = None,
        might_split: Optional[List[float]] = None,
        # Standardwerte für might_split (nur für Figuren relevant)
    ):
        self.id = id
        self.name = name
        self.type = type
        self.base_might = base_might
        
        # Gemeinsame Attribute
        self.display_name_en = display_name_en
        self.display_name_de = display_name_de
        self.description = description
        self.faction = faction
        self.rarity = rarity
        self.mobility = mobility
        self.range = range
        self.vision = vision
        self.placing = placing
        self.AP_credit = AP_credit
        
        # Buffs und Tags
        self.buffs = buffs if buffs is not None else {
            "self": [],
            "neighbor": [],
            "opponent": [],
            "faction": [],
            "targeted": []
        }
        self.tags = tags if tags is not None else []
        
        # Might-Split (Standard für Figuren: [0.5, 0.5])
        self.might_split = might_split if might_split is not None else [0.5, 0.5]

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
            display_name_en=data.get("display_name_en"),
            display_name_de=data.get("display_name_de"),
            description=data.get("description"),
            faction=data.get("faction"),
            rarity=data.get("rarity"),
            mobility=data.get("mobility", "ground"),
            range=data.get("range", "melee"),
            vision=data.get("vision", 1),
            placing=data.get("placing", False),
            AP_credit=data.get("AP_credit", 0),
            buffs=buffs,
            tags=data.get("tags", []),
            might_split=data.get("might_split", [0.5, 0.5])
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
            "display_name_en": self.display_name_en,
            "display_name_de": self.display_name_de,
            "description": self.description,
            "faction": self.faction,
            "rarity": self.rarity,
            "mobility": self.mobility,
            "range": self.range,
            "vision": self.vision,
            "placing": self.placing,
            "AP_credit": self.AP_credit,
            "buffs": buffs,
            "tags": self.tags,
            "might_split": self.might_split
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