from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass
from core.entities.buff import Buff
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
    Enthält nur Attribute und Hilfsmethoden – KEINE Might-Berechnungslogik!
    """

    def __init__(
        self,
        id: str,
        name: str,
        type: str,
        base_might: int = 0,
        # Gemeinsame Attribute
        display_name_en: Optional[str] = None,
        display_name_de: Optional[str] = None,
        description: Optional[str] = None,
        faction: Optional[str] = None,
        rarity: Optional[str] = None,
        mobility: str = "ground",
        range: str = "melee",
        vision: int = 1,
        placing: bool = False,
        buffs: Optional[Dict[str, List[Buff]]] = None,
        tags: Optional[List[str]] = None,
        # Might-Split
        might_split: Optional[List[float]] = None,
        # Alt-State
        alt: bool = False,
        alt_entity: Optional[str] = None,
        mighty_threshold: int = 20,
        # Kosten
        cost: int = 0,
        activation_cost: int = 0,
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

        # Buffs und Tags
        self.buffs = buffs if buffs is not None else {
            "self": [],
            "neighbor": [],
            "opponent": [],
            "faction": [],
            "targeted": []
        }
        self.tags = tags if tags is not None else []

        # Might-Split (Standard: [0.5, 0.5])
        self.might_split = might_split if might_split is not None else [0.5, 0.5]

        # Alt-State
        self.alt = alt
        self.alt_entity = alt_entity
        self.mighty_threshold = mighty_threshold

        # Kosten
        self.cost = cost
        self.activation_cost = activation_cost

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEntity':
        """Erstellt eine BaseEntity aus einem Dictionary (JSON-Deserialisierung)."""
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
            buffs=buffs,
            tags=data.get("tags", []),
            might_split=data.get("might_split", [0.5, 0.5]),
            alt=data.get("alt", False),
            alt_entity=data.get("alt_entity"),
            mighty_threshold=data.get("mighty_threshold", 20),
            cost=data.get("cost", 0),
            activation_cost=data.get("activation_cost", 0)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert die Entity in ein Dictionary (JSON-Serialisierung)."""
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
            "buffs": buffs,
            "tags": self.tags,
            "might_split": self.might_split,
            "alt": self.alt,
            "alt_entity": self.alt_entity,
            "mighty_threshold": self.mighty_threshold,
            "cost": self.cost,
            "activation_cost": self.activation_cost
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

    # --- Alt-State ---
    def activate_alt_state(self) -> bool:
        """Aktiviert/deaktiviert den Alt-State. Gibt True zurück."""
        self.alt = not self.alt
        return True

    def is_alt_active(self) -> bool:
        """Prüft, ob der Alt-State aktiv ist."""
        return self.alt

    # --- Hilfsmethoden für Might-Berechnung (werden vom MightCalculator genutzt) ---
    def is_mighty(self, current_might: int) -> bool:
        """Prüft, ob die Entity 'Mighty' ist (braucht current_might als Parameter!)."""
        return current_might >= self.mighty_threshold

    def get_might_split(self) -> List[float]:
        """Gibt den Might-Split zurück."""
        return self.might_split