from typing import List, Dict, Optional, Union, Any
import json
from pathlib import Path
from core.entities.buff import Buff  # Importiere Buff aus buff.py


class BaseEntity:
    """
    Basis-Klasse für alle Entities (Figuren, Locations, Effekte, Vehicles).
    
    --- Gemeinsame Attribute (für alle Entities) ---
    - id, name, type, base_might
    - display_name_en/de, description, faction, rarity
    - mobility, range, vision, placing
    - buffs, might_split, cost, AP_credit
    
    --- Figur-exklusive Attribute (können aber für alle Entities gesetzt werden, mit Default-Werten) ---
    - alt_state, mighty_threshold, activation_cost
    
    --- Abgeleitete Logik für Hexfelder ---
    - might_split: Maximaler might_split-Wert aller Entities auf dem Hexfeld.
    - AP_credit: Summe aller AP_credit-Werte auf dem Hexfeld.
    - placing: True, wenn mindestens eine Entity auf dem Feld placing=True hat.
    - vision: Maximaler vision-Wert aller Entities (nur relevant, wenn eine Figur auf dem Feld steht).
    - display_name: display_name der Figur (falls vorhanden), sonst None.
    """

    def __init__(
        self,
        id: str,
        name: str,
        type: str,  # "figure", "location", "effect", "vehicle"
        base_might: int = 0,
        # Anzeige & Metadaten
        display_name_en: Optional[str] = None,
        display_name_de: Optional[str] = None,
        description: Optional[str] = None,
        faction: Optional[str] = None,
        rarity: Optional[str] = None,
        # Spielmechaniken
        mobility: str = "ground",  # "ground", "flying", "ether"
        range: str = "melee",      # "melee", "long_range", "astral"
        vision: int = 1,
        placing: bool = False,
        buffs: Optional[Dict[str, List[Buff]]] = None,
        might_split: Optional[List[float]] = None,
        # Kosten
        cost: int = 0,
        AP_credit: int = 0,
        # Figur-spezifisch (können für alle Entities gesetzt werden, aber nur für Figuren/Effekte relevant)
        alt_state: bool = False,
        mighty_threshold: int = 20,
        activation_cost: int = 0,
    ):
        # --- Pflichtattribute ---
        self.id = id
        self.name = name
        self.type = type
        self.base_might = base_might

        # --- Anzeige & Metadaten ---
        self.display_name_en = display_name_en
        self.display_name_de = display_name_de
        self.description = description
        self.faction = faction
        self.rarity = rarity

        # --- Spielmechaniken ---
        self.mobility = mobility
        self.range = range
        self.vision = vision
        self.placing = placing

        # --- Buffs & Might-Split ---
        self.buffs = buffs if buffs is not None else {
            "self": [],
            "neighbor": [],
            "opponent": [],
            "faction": [],
            "targeted": []
        }
        self.might_split = might_split if might_split is not None else [0.5, 0.5]

        # --- Kosten ---
        self.cost = cost
        self.AP_credit = AP_credit

        # --- Figur-spezifisch (Default-Werte für alle Entities) ---
        self.alt_state = alt_state
        self.mighty_threshold = mighty_threshold
        self.activation_cost = activation_cost

    # --- Serialisierung ---
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
            might_split=data.get("might_split", [0.5, 0.5]),
            cost=data.get("cost", 0),
            AP_credit=data.get("AP_credit", 0),
            alt_state=data.get("alt_state", False),
            mighty_threshold=data.get("mighty_threshold", 20),
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
            "might_split": self.might_split,
            "cost": self.cost,
            "AP_credit": self.AP_credit,
            "alt_state": self.alt_state,
            "mighty_threshold": self.mighty_threshold,
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
        self.alt_state = not self.alt_state
        return True

    def is_alt_active(self) -> bool:
        """Prüft, ob der Alt-State aktiv ist."""
        return self.alt_state

    def is_mighty(self, current_might: int) -> bool:
        """Prüft, ob die Entity 'Mighty' ist (braucht current_might als Parameter!)."""
        return current_might >= self.mighty_threshold

    def get_might_split(self) -> List[float]:
        """Gibt den Might-Split zurück."""
        return self.might_split