"""
Entity Loader für Sturm auf Grayskull.
Lädt Entities (Figuren, Locations, Effekte, Vehicles) aus JSON-Dateien.
"""

import json
from pathlib import Path
from typing import Dict, Union, List
from core.entities.figure import Figure
from core.entities.location import Location
from core.entities.effect import Effect
from core.entities.vehicle import Vehicle
from core.entities.base_entity import BaseEntity

class EntityLoader:
    """
    Lädt Entities aus JSON-Dateien und konvertiert sie in die entsprechenden Klassen.
    """

    # Mapping: Entity-Typ -> Klasse
    ENTITY_CLASSES = {
        "figure": Figure,
        "location": Location,
        "effect": Effect,
        "vehicle": Vehicle
    }

    @staticmethod
    def load_entities(file_path: Union[str, Path]) -> Dict[str, BaseEntity]:
        """
        Lädt alle Entities aus einer JSON-Datei.

        Args:
            file_path: Pfad zur JSON-Datei.

        Returns:
            Dict[str, BaseEntity]: Dictionary mit Entity-IDs als Keys.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        entities = {}
        for entity_id, entity_data in data.items():
            entity_data["id"] = entity_id  # ID aus dem Key übernehmen
            entity = EntityLoader._create_entity(entity_data)
            if entity:
                entities[entity_id] = entity
        return entities

    @staticmethod
    def _create_entity(data: dict) -> Union[Figure, Location, Effect, Vehicle, None]:
        """
        Erstellt eine Entity aus einem Dictionary basierend auf dem Typ.

        Args:
            data: Dictionary mit Entity-Daten.

        Returns:
            BaseEntity: Instanz der passenden Entity-Klasse.
        """
        entity_type = data.get("type", "figure")
        entity_class = EntityLoader.ENTITY_CLASSES.get(entity_type)

        if not entity_class:
            return None

        return entity_class.from_dict(data)

    @staticmethod
    def load_all_entities(data_dir: Union[str, Path] = "data") -> Dict[str, Dict[str, BaseEntity]]:
        """
        Lädt alle Entities aus dem data/-Verzeichnis.

        Args:
            data_dir: Pfad zum Datenverzeichnis.

        Returns:
            Dict[str, Dict[str, BaseEntity]]: Dictionary mit Dateinamen als Keys
            und Entity-Dictionaries als Values.
        """
        data_path = Path(data_dir)
        entities = {}

        # Lade alle JSON-Dateien im Verzeichnis
        for json_file in data_path.glob("*.json"):
            file_stem = json_file.stem
            entities[file_stem] = EntityLoader.load_entities(json_file)

        return entities