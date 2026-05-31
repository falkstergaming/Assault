"""
Board Initializer - Verantwortlich für die Initialisierung des Spielfelds.
Enthält alle Methoden zur Erstellung von Hex-IDs, Sichtbarkeit und Nachbarn.
"""

from typing import Dict, List, Set
from core.utils.hex_id import HexID


class BoardInitializer:
    """Hilfsklasse für die Initialisierung des Board-States."""

    @staticmethod
    def initialize_valid_hex_ids() -> Set[HexID]:
        """
        Initialisiert die Menge der gültigen Hex-IDs.
        Enthält EXAKT die Felder:
        - Idle-Felder (3xxx): 3011, 3012, 3013
        - Player-Felder (1xxx): 1111, 1112, 1213, 1114, 1215, 1116, 1117
        - AI-Felder (2xxx): 2111, 2112, 2213, 2114, 2215, 2116, 2117
        - Preview-Spieler (4xxx): 4000-4007
        - Preview-Gegner (5xxx): 5000-5007
        - Avatare (0xxx): 0000, 0001, 0002
        - Back-Spieler (6xxx): 6000-6007
        - Back-Gegner (7xxx): 7000-7007
        - Spezial-Spieler (8xxx): 8000-8007
        - Spezial-Gegner (9xxx): 9000-9007
        """
        hex_ids = set()

        # --- Idle-Felder (3xxx) ---
        hex_ids.update({HexID("3011"), HexID("3012"), HexID("3013")})

        # --- Player-Felder (1xxx): 7 Felder ---
        hex_ids.update({
            HexID("1111"), HexID("1112"), HexID("1213"),
            HexID("1114"), HexID("1215"), HexID("1116"), HexID("1117")
        })

        # --- Gegner-Felder (2xxx): 7 Felder ---
        hex_ids.update({
            HexID("2111"), HexID("2112"), HexID("2213"),
            HexID("2114"), HexID("2215"), HexID("2116"), HexID("2117")
        })

        # --- Preview-Spieler (4xxx): 4000-4007 ---
        hex_ids.update(HexID(f"40{num:02d}") for num in range(0, 8))

        # --- Preview-Gegner (5xxx): 5000-5007 ---
        hex_ids.update(HexID(f"50{num:02d}") for num in range(0, 8))

        # --- Avatare (0xxx) ---
        hex_ids.update({HexID("0000"), HexID("0001"), HexID("0002")})

        # --- Back-Spieler (6xxx): 6000-6007 ---
        hex_ids.update(HexID(f"60{num:02d}") for num in range(0, 8))

        # --- Back-Gegner (7xxx): 7000-7007 ---
        hex_ids.update(HexID(f"70{num:02d}") for num in range(0, 8))

        # --- Spezial-Spieler (8xxx): 8000-8007 ---
        hex_ids.update(HexID(f"80{num:02d}") for num in range(0, 8))

        # --- Spezial-Gegner (9xxx): 9000-9007 ---
        hex_ids.update(HexID(f"90{num:02d}") for num in range(0, 8))

        return hex_ids

    @staticmethod
    def initialize_visibility(valid_hex_ids: Set[HexID]) -> Dict[HexID, bool]:
        """
        Initialisiert den Sichtbarkeitsstatus für alle Hex-IDs.
        Regel:
        - Spielbrett-Felder (1xxx, 2xxx, 3xxx, 0xxx) → sichtbar.
        - Preview-Felder (4xxx, 5xxx) → anfangs unsichtbar.
        - Backrows (6xxx, 7xxx) und Special (8xxx, 9xxx) → immer unsichtbar.
        """
        visibility = {}
        for hex_id in valid_hex_ids:
            # Spielbrett-Felder (1xxx, 2xxx, 3xxx, 0xxx) sind sichtbar
            if hex_id.area in [0, 1, 2, 3]:
                visibility[hex_id] = True
            # Preview-Felder (4xxx, 5xxx) sind anfangs unsichtbar
            elif hex_id.area in [4, 5]:
                visibility[hex_id] = False
            # Backrows (6xxx, 7xxx) und Special (8xxx, 9xxx) sind immer unsichtbar
            else:
                visibility[hex_id] = False
        return visibility

    @staticmethod
    def initialize_idle_neighbors() -> Dict[HexID, Dict[str, List[HexID]]]:
        """
        Initialisiert die Nachbarn der Idle-Felder für Spieler und Gegner.
        Basierend auf:
        - 3011: Player = [1111, 1112, 1213], AI = [2111, 2112, 2213]
        - 3012: Player = [1213, 1114, 1215], AI = [2213, 2114, 2215]
        - 3013: Player = [1215, 1116, 1117], AI = [2215, 2116, 2117]
        """
        return {
            HexID("3011"): {
                "player": [HexID("1111"), HexID("1112"), HexID("1213")],
                "opponent": [HexID("2111"), HexID("2112"), HexID("2213")]
            },
            HexID("3012"): {
                "player": [HexID("1213"), HexID("1114"), HexID("1215")],
                "opponent": [HexID("2213"), HexID("2114"), HexID("2215")]
            },
            HexID("3013"): {
                "player": [HexID("1215"), HexID("1116"), HexID("1117")],
                "opponent": [HexID("2215"), HexID("2116"), HexID("2117")]
            }
        }

    @staticmethod
    def initialize_logical_neighbors() -> Dict[HexID, List[HexID]]:
        """
        Initialisiert die logischen Nachbarn für die Spiel-Logik (Marsch, Might-Berechnung).
        Basierend auf horizontaler Kette:
        - 1111 ↔ 1112 ↔ 1213 ↔ 1114 ↔ 1215 ↔ 1116 ↔ 1117
        - 2111 ↔ 2112 ↔ 2213 ↔ 2114 ↔ 2215 ↔ 2116 ↔ 2117
        """
        return {
            # Spieler-Lane (horizontale Kette)
            HexID("1111"): [HexID("1112")],
            HexID("1112"): [HexID("1111"), HexID("1213")],
            HexID("1213"): [HexID("1112"), HexID("1114")],
            HexID("1114"): [HexID("1213"), HexID("1215")],
            HexID("1215"): [HexID("1114"), HexID("1116")],
            HexID("1116"): [HexID("1215"), HexID("1117")],
            HexID("1117"): [HexID("1116")],
            # Gegner-Lane (horizontale Kette)
            HexID("2111"): [HexID("2112")],
            HexID("2112"): [HexID("2111"), HexID("2213")],
            HexID("2213"): [HexID("2112"), HexID("2114")],
            HexID("2114"): [HexID("2213"), HexID("2215")],
            HexID("2215"): [HexID("2114"), HexID("2116")],
            HexID("2116"): [HexID("2215"), HexID("2117")],
            HexID("2117"): [HexID("2116")],
        }

    @staticmethod
    def initialize_optical_neighbors() -> Dict[HexID, List[HexID]]:
        """
        Initialisiert die OPTISCHEN Nachbarn für das UI-Rendering.
        Enthält ALLE sichtbar verbundenen Felder, inkl. Backrows und Preview.
        """
        logical = BoardInitializer.initialize_logical_neighbors()
        optical_neighbors = {}

        # --- Logische Nachbarn (aus initialize_logical_neighbors) ---
        for hex_id, neighbors in logical.items():
            optical_neighbors[hex_id] = neighbors.copy()

        # --- Backrow-Spieler (6xxx): Nachbarn zu Spieler-Lane (1xxx) ---
        optical_neighbors[HexID("6000")] = [HexID("1111")]
        optical_neighbors[HexID("6001")] = [HexID("1111")]
        optical_neighbors[HexID("6002")] = [HexID("1111"), HexID("1112")]
        optical_neighbors[HexID("6003")] = [HexID("1112"), HexID("1213")]
        optical_neighbors[HexID("6004")] = [HexID("1213"), HexID("1114")]
        optical_neighbors[HexID("6005")] = [HexID("1114"), HexID("1215")]
        optical_neighbors[HexID("6006")] = [HexID("1215"), HexID("1116")]
        optical_neighbors[HexID("6007")] = [HexID("1116"), HexID("1117")]

        # --- Backrow-Gegner (7xxx): Nachbarn zu Gegner-Lane (2xxx) ---
        optical_neighbors[HexID("7000")] = [HexID("2111")]
        optical_neighbors[HexID("7001")] = [HexID("2111")]
        optical_neighbors[HexID("7002")] = [HexID("2111"), HexID("2112")]
        optical_neighbors[HexID("7003")] = [HexID("2112"), HexID("2213")]
        optical_neighbors[HexID("7004")] = [HexID("2213"), HexID("2114")]
        optical_neighbors[HexID("7005")] = [HexID("2114"), HexID("2215")]
        optical_neighbors[HexID("7006")] = [HexID("2215"), HexID("2116")]
        optical_neighbors[HexID("7007")] = [HexID("2116"), HexID("2117")]

        # --- Preview-Spieler (4xxx): Nachbarn zu Spieler-Lane (1xxx) ---
        optical_neighbors[HexID("4000")] = [HexID("1111"), HexID("4001")]
        optical_neighbors[HexID("4001")] = [HexID("1111"), HexID("4000"), HexID("4002")]
        optical_neighbors[HexID("4002")] = [HexID("1111"), HexID("1112"), HexID("4001"), HexID("4003")]
        optical_neighbors[HexID("4003")] = [HexID("1112"), HexID("1213"), HexID("4002"), HexID("4004")]
        optical_neighbors[HexID("4004")] = [HexID("1213"), HexID("1114"), HexID("4003"), HexID("4005")]
        optical_neighbors[HexID("4005")] = [HexID("1114"), HexID("1215"), HexID("4004"), HexID("4006")]
        optical_neighbors[HexID("4006")] = [HexID("1215"), HexID("1116"), HexID("4005"), HexID("4007")]
        optical_neighbors[HexID("4007")] = [HexID("1116"), HexID("1117"), HexID("4006")]

        # --- Preview-Gegner (5xxx): Nachbarn zu Gegner-Lane (2xxx) ---
        optical_neighbors[HexID("5000")] = [HexID("2111"), HexID("5001")]
        optical_neighbors[HexID("5001")] = [HexID("2111"), HexID("5000"), HexID("5002")]
        optical_neighbors[HexID("5002")] = [HexID("2111"), HexID("2112"), HexID("5001"), HexID("5003")]
        optical_neighbors[HexID("5003")] = [HexID("2112"), HexID("2213"), HexID("5002"), HexID("5004")]
        optical_neighbors[HexID("5004")] = [HexID("2213"), HexID("2114"), HexID("5003"), HexID("5005")]
        optical_neighbors[HexID("5005")] = [HexID("2114"), HexID("2215"), HexID("5004"), HexID("5006")]
        optical_neighbors[HexID("5006")] = [HexID("2215"), HexID("2116"), HexID("5005"), HexID("5007")]
        optical_neighbors[HexID("5007")] = [HexID("2116"), HexID("2117"), HexID("5006")]

        return optical_neighbors
