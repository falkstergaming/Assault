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
    Final mit Alt-State, Kosten, und Buff-Logik.
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
        mobility: str = "ground",
        range: str = "melee",
        vision: int = 1,
        placing: bool = False,
        buffs: Optional[Dict[str, List[Buff]]] = None,
        tags: Optional[List[str]] = None,
        might_split: Optional[List[float]] = None,
        # Alt-State Attribute
        alt: bool = False,
        alt_entity: Optional[str] = None,
        mighty_threshold: int = 20,
        # Kostenattribute
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
        
        # Might-Split (Standard für alle Entities: [0.5, 0.5])
        self.might_split = might_split if might_split is not None else [0.5, 0.5]
        
        # Alt-State Attribute
        self.alt = alt
        self.alt_entity = alt_entity
        self.mighty_threshold = mighty_threshold
        
        # Kostenattribute
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
        """Aktiviert/deaktiviert den Alt-State. Gibt True zurück, wenn erfolgreich."""
        self.alt = not self.alt
        return True

    def is_alt_active(self) -> bool:
        """Prüft, ob der Alt-State aktiv ist."""
        return self.alt

    # --- Might-Berechnung ---
    def calculate_might(self, neighbor_entities: List['BaseEntity'] = None, opponent=None, location=None, hex_id: Optional[str] = None) -> int:
        """
        Berechnet den Might-Wert der Entity inkl. aller Buffs.
        Self-Buffs wirken nur, wenn:
        - Figur/Effekt: alt_state aktiv ist (self.alt = True)
        - Location: Eine Figur auf der Location steht
        """
        might = self.base_might
        neighbor_entities = neighbor_entities or []

        # 1. Self-Buffs (nur wenn Alt-State aktiv ODER Location mit Figur)
        should_apply_self_buffs = (
            self.alt or 
            (self.type == "location" and hex_id and self._is_figure_on_location(hex_id))
        )
        if should_apply_self_buffs:
            for buff in self.buffs["self"]:
                might += buff.value

        # 2. Neighbor-Buffs (von angrenzenden Entities)
        for neighbor in neighbor_entities:
            for buff in neighbor.buffs["neighbor"]:
                if (buff.target_type == "faction" and buff.target and buff.target in (self.faction or "")) or \
                   (buff.target_type == "tag" and buff.target in self.tags) or \
                   (buff.target_type == "id" and buff.target == self.id):
                    might += buff.value

        # 3. Opponent-Buffs (von gegenüberliegender Entity)
        if opponent:
            for buff in opponent.buffs["opponent"]:
                might += buff.value

        # 4. Faction-Buffs (globale Buffs für die Faction)
        for buff in self.buffs["faction"]:
            if buff.target_type == "faction" and buff.target and buff.target in (self.faction or ""):
                might += buff.value

        # 5. Targeted-Buffs (spezifische Buffs für diese Entity)
        for buff in self.buffs["targeted"]:
            might += buff.value

        # 6. Location-Buffs (wenn Figur auf Location steht)
        if location and self.type == "figure":
            for buff in location.buffs["self"]:
                might += buff.value

        return max(0, might)

    def _is_figure_on_location(self, hex_id: str) -> bool:
        """Hilfsfunktion: Prüft, ob eine Figur auf dieser Location steht (nur für Locations relevant)."""
        # Diese Methode würde in einer echten Implementierung das Board abfragen
        # Hier nur ein Platzhalter
        return False

    def is_mighty(self, current_might: Optional[int] = None) -> bool:
        """Prüft, ob die Entity 'Mighty' ist."""
        if current_might is None:
            current_might = self.calculate_might()
        return current_might >= self.mighty_threshold

    def get_might_split(self) -> List[float]:
        """Gibt den Might-Split zurück."""
        return self.might_split