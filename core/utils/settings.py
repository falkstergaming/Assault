"""
Settings-Modul für Sturm auf Grayskull.
Verwaltet Spracheinstellungen und Audio-Einstellungen (Musik/Effekte Lautstärke).
Einstellungen werden in settings.ini gespeichert und beim Programmstart geladen.
"""

import configparser
import os
from typing import Dict, Any, Optional

# Standardwerte
DEFAULT_SETTINGS = {
    "language": "en",
    "music_volume": 100,
    "effect_volume": 100,
    "music_enabled": True
}


class Settings:
    """
    Verwaltet die Spiel-Einstellungen.
    
    Einstellungen:
    - language: "de" oder "en"
    - music_volume: 0-100 (Integer)
    - effect_volume: 0-100 (Integer)
    - music_enabled: True/False
    """

    def __init__(self, settings_file: str = "settings.ini"):
        """
        Initialisiert die Settings.
        
        Args:
            settings_file: Pfad zur Settings-Datei
        """
        self.settings_file = settings_file
        self._settings: Dict[str, Any] = DEFAULT_SETTINGS.copy()
        self._load()

    def _load(self) -> None:
        """Lädt die Einstellungen aus der INI-Datei."""
        config = configparser.ConfigParser()
        
        # Standardwerte für neue Datei
        config["Language"] = {"lang": self._settings["language"]}
        config["Audio"] = {
            "music_volume": str(self._settings["music_volume"]),
            "effect_volume": str(self._settings["effect_volume"]),
            "music_enabled": str(self._settings["music_enabled"])
        }
        
        # Versuche, die Datei zu lesen
        if os.path.exists(self.settings_file):
            try:
                config.read(self.settings_file, encoding='utf-8')
                
                # Sprache laden
                if "Language" in config and "lang" in config["Language"]:
                    self._settings["language"] = config["Language"]["lang"]
                
                # Audio laden
                if "Audio" in config:
                    if "music_volume" in config["Audio"]:
                        self._settings["music_volume"] = int(config["Audio"]["music_volume"])
                    if "effect_volume" in config["Audio"]:
                        self._settings["effect_volume"] = int(config["Audio"]["effect_volume"])
                    if "music_enabled" in config["Audio"]:
                        self._settings["music_enabled"] = config["Audio"].getboolean("music_enabled")
            except Exception as e:
                print(f"[WARNING] Fehler beim Laden der Settings: {e}")
                # Behalte Standardwerte
        else:
            # Erstelle neue Settings-Datei mit Standardwerten
            self._save()

    def _save(self) -> None:
        """Speichert die Einstellungen in die INI-Datei."""
        config = configparser.ConfigParser()
        
        config["Language"] = {"lang": self._settings["language"]}
        config["Audio"] = {
            "music_volume": str(self._settings["music_volume"]),
            "effect_volume": str(self._settings["effect_volume"]),
            "music_enabled": str(self._settings["music_enabled"])
        }
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                config.write(f)
        except Exception as e:
            print(f"[WARNING] Fehler beim Speichern der Settings: {e}")

    def save(self) -> None:
        """Speichert die Einstellungen (öffentliche Methode)."""
        self._save()

    # --- Getter/Setter ---
    
    @property
    def language(self) -> str:
        """Gibt die aktuelle Sprache zurück ("de" oder "en")."""
        return self._settings["language"]
    
    @language.setter
    def language(self, value: str) -> None:
        """Setzt die Sprache und speichert die Einstellungen."""
        if value in ["de", "en"]:
            self._settings["language"] = value
            self._save()
    
    @property
    def music_volume(self) -> int:
        """Gibt die Musik-Lautstärke zurück (0-100)."""
        return self._settings["music_volume"]
    
    @music_volume.setter
    def music_volume(self, value: int) -> None:
        """Setzt die Musik-Lautstärke (0-100) und speichert die Einstellungen."""
        self._settings["music_volume"] = max(0, min(100, value))
        self._save()
    
    @property
    def effect_volume(self) -> int:
        """Gibt die Effekt-Lautstärke zurück (0-100)."""
        return self._settings["effect_volume"]
    
    @effect_volume.setter
    def effect_volume(self, value: int) -> None:
        """Setzt die Effekt-Lautstärke (0-100) und speichert die Einstellungen."""
        self._settings["effect_volume"] = max(0, min(100, value))
        self._save()
    
    @property
    def music_enabled(self) -> bool:
        """Gibt zurück, ob Musik aktiviert ist."""
        return self._settings["music_enabled"]
    
    @music_enabled.setter
    def music_enabled(self, value: bool) -> None:
        """Setzt, ob Musik aktiviert ist, und speichert die Einstellungen."""
        self._settings["music_enabled"] = value
        self._save()
    
    def get_all(self) -> Dict[str, Any]:
        """Gibt alle Einstellungen als Dictionary zurück."""
        return self._settings.copy()
