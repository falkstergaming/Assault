"""
Zentrale Übersetzungen für Sturm auf Grayskull.
Enthält alle sprachabhängigen Texte für DE/EN.

Hinweis: Entity-Namen kommen aus JSON-Dateien und werden hier NICHT übersetzt.
"""

from typing import Dict, Any

# --- Übersetzungen (DE/EN) ---
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # Titel
        "game_title": "Assault on Grayskull",
        "stats_title": "Game Stats",
        
        # Spielbegriffe
        "mode": "Mode",
        "match": "Match",
        "round": "Round",
        "phase": "Phase",
        "player": "Player",
        "opponent": "Opponent",
        "idle": "Idle",
        "might": "Might",
        "wins": "Wins",
        
        # Buttons
        "action": "Action",
        "settings": "Settings",
        
        # Settings-Menü
        "language": "Language",
        "music_volume": "Music Volume",
        "effect_volume": "Effect Volume",
        "german": "German",
        "english": "English",
    },
    "de": {
        # Titel
        "game_title": "Sturm auf Grayskull",
        "stats_title": "Spielstand",
        
        # Spielbegriffe
        "mode": "Modus",
        "match": "Match",
        "round": "Runde",
        "phase": "Phase",
        "player": "Spieler",
        "opponent": "Gegner",
        "idle": "Idle",
        "might": "Might",
        "wins": "Siege",
        
        # Buttons
        "action": "Weiter",
        "settings": "Einstellungen",
        
        # Settings-Menü
        "language": "Sprache",
        "music_volume": "Musik-Lautstärke",
        "effect_volume": "Effekt-Lautstärke",
        "german": "Deutsch",
        "english": "Englisch",
    }
}


def get_translation(key: str, lang: str = "en") -> str:
    """
    Gibt die Übersetzung für einen Schlüssel zurück.
    
    Args:
        key: Schlüssel im TRANSLATIONS-Dictionary
        lang: Sprachcode ("de" oder "en")
    
    Returns:
        Übersetzter Text, oder der Schlüssel selbst falls nicht gefunden
    """
    return TRANSLATIONS.get(lang, {}).get(key, key)
