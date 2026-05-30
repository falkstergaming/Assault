"""
Globale Konstanten für Sturm auf Grayskull.
Alle Konstanten sind hier zentral definiert, um Wartbarkeit zu erhöhen.
"""
# Hexfeld-Geometrie für die Wabenstruktur
HEX_SIZE = {
    "width": 80,    # eventuell kleiner machen
    "height": 80
}
HEX_SPACING = 10     # Größerer Abstand zwischen den Hexfeldern


# --- Might & Buffs ---
DEFAULT_MIGHT_SPLIT = [0.5, 0.5]  # Standard-Might-Aufteilung für Felder mit 2 Idles
MIN_MIGHT = 0                      # Minimale Might (keine Macht = keine Kontrolle)
MIGHTY_THRESHOLD = 20             # Ab diesem Might-Wert gilt eine Figur als "Mighty"

# Buff-Typen (für Immunitäten und Berechnungen)
BUFF_TYPES = [
    "self",
    "neighbor",
    "opponent",
    "faction",
    "targeted"
]

# Buff-Value-Typen (für Immunitäten)
BUFF_VALUE_TYPES = [
    "positive",
    "negative",
    "all"
]

# --- Hexfelder ---
HEX_AREA_PLAYER = 1
HEX_AREA_OPPONENT = 2
HEX_AREA_IDLE = 3
HEX_AREA_PREVIEW_PLAYER = 4
HEX_AREA_PREVIEW_OPPONENT = 5
HEX_AREA_BACK_PLAYER = 6
HEX_AREA_BACK_OPPONENT = 7
HEX_AREA_SPECIAL_PLAYER = 8
HEX_AREA_SPECIAL_OPPONENT = 9

# --- Runden & Phasen ---
TOTAL_ROUNDS = 7                  # Gesamtzahl der Runden (0-6)
ROUND_PHASES = [
    "figure_selection",      # Phase 1
    "march",                 # Phase 2
    "prelim_might_calc_1",   # Phase 3 (nach Marsch)
    "position_correction",   # Phase 4
    "prelim_might_calc_2",   # Phase 5 (nach Positionskorrektur)
    "buy_effects",           # Phase 6
    "apply_effects",         # Phase 7
    "final_might_calc",      # Phase 8
    "evaluate"               # Phase 9
]

# --- Assault Points (AP) ---
AP_PER_ROUND = {
    0: 0,  # Runde 0: 0 AP
    1: 1,  # Runde 1: +1 AP
    2: 2,  # Runde 2: +2 AP
    3: 3,
    4: 4,
    5: 5,
    6: 6   # Runde 6: +6 AP
}

# --- Factions ---
FACTIONS = [
    "Adam",     # Good
    "Skeletor", # Evil
    "Hordak",   # Evil (Horde)
    "Zodak"     # Neutral
]

# Faction-Pools (für Figurenauswahl)
FACTION_POOLS = {
    "Good": ["Adam"],
    "Evil": ["Skeletor", "Hordak"],
    "Neutral": ["Zodak"],
    "Horde": ["Hordak"]  # Spezialfall für Hordak
}

# --- UI & Rendering ---
# Farben (Beispielwerte, können angepasst werden)
COLORS = {
    "primary": (0, 100, 200),       # Blau
    "secondary": (200, 200, 200),   # Grau
    "background": (20, 20, 40),     # Dunkelblau
    "text": (255, 255, 255),        # Weiß
    "highlight": (255, 215, 0),     # Gold für Highlighting
    "idle_player": (0, 255, 0),     # Grün für Spieler-Idle
    "idle_opponent": (255, 0, 0),   # Rot für Gegner-Idle
    "idle_neutral": (200, 200, 0),  # Gelb für neutrale Idles
}
# Faction-Farben (RGB)
FACTION_COLORS = {
    "Adam": {
        "primary": (96, 145, 116),      # 🟩 Moos-Neon Grün
        "secondary": (255, 215, 0),    # Gold
    },
    "Skeletor": {
        "primary": (125, 98, 150),      # 🟪 Dusty Retro Violet
        "secondary": (0, 0, 0),        # Schwarz
    },
    "Hordak": {
        "primary": (154, 86, 92),      # 🟥 Ancient Crimson (Rot)
        "secondary": (192, 192, 192),  # Silber
    },
    "Zodak": {
        "primary": (190, 125, 84),     # 🟧 Faded Sunset Orange
        "secondary": (128, 128, 128),  # Grau
    }
}

# Faction-Themes (Musik & Hintergrund)
FACTION_THEMES = {
    "Adam": {
        "music": "artwork/music/adam_theme.mp3",
        "background": "artwork/background_adam.jpg"
    },
    "Skeletor": {
        "music": "artwork/music/skeletor_theme.mp3",
        "background": "artwork/background_skeletor.jpg"
    },
    "Hordak": {
        "music": "artwork/music/hordak_theme.mp3",
        "background": "artwork/background_hordak.jpg"
    },
    "Zodak": {
        "music": "artwork/music/zodak_theme.mp3",
        "background": "artwork/background_zodak.jpg"
    }
}
## Fonts
FONT_FAMILY = "Eurostile"  # Standard-Schriftart für das gesamte Spiel
FONT_TITLE = (FONT_FAMILY, 24)      # Titel (z. B. "Sturm auf Grayskull")
FONT_BODY = (FONT_FAMILY, 16)       # Standardtext (z. B. Menüpunkte)
FONT_CONSOLE = (FONT_FAMILY, 18)   # Konsolenschrift (20% kleiner als Body)
FONT_DESCRIPTION = (FONT_FAMILY, 14)  # Testbeschreibungen

# Highlighting-Stufen (für UI)
HIGHLIGHT_LEVELS = {
    "deactivated": 0,  # Ausgegraut, nicht anwählbar
    "non": 1,          # Standard
    "spotlight": 2,    # Wählbar + Indikator
    "selected": 3      # Angewählt
}

# --- Hexfeld-Größen & Hitboxen ---
# Alle Hexfelder haben die gleiche Größe (für JPG-Overlay).
HEX_FIELD_SIZE = (80, 80)  # Breite, Höhe (Pixel) - Platzhalter für Rendering

# --- Dateipfade ---
DATA_DIR = "data/"
FIGURES_JSON = f"{DATA_DIR}figurenwerk.json"
LOCATIONS_JSON = f"{DATA_DIR}eterniaorte.json"
EFFECTS_JSON = f"{DATA_DIR}effekte.json"
VEHICLE_JSON = f"{DATA_DIR}fahrzeuge.json"
FACTIONS_JSON = f"{DATA_DIR}factions.json"
SETTINGS_INI = "settings.ini"


