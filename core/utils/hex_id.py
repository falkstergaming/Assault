from typing import List, Dict, Optional, Tuple

class HexID:
    """
    Repräsentiert ein Hexfeld mit 4-stelliger Codierung.
    Format: ABCD, wobei:
    - A (1. Ziffer): Bereich (0-9)
        0: AREA_AVATAR (Avatar-Felder, ohne Einfluss)
        1: AREA_PLAYER (Spieler-Lane)
        2: AREA_OPPONENT (Gegner-Lane)
        3: AREA_IDLE (Idle-Felder)
        4: AREA_PREVIEW_PLAYER (Preview-Bereich Spieler)
        5: AREA_PREVIEW_OPPONENT (Preview-Bereich Gegner)
        6: AREA_BACK_PLAYER (Back-Spieler)
        7: AREA_BACK_OPPONENT (Back-Gegner)
        8: AREA_SPECIAL_PLAYER (Spezialfelder links für Spieler-Effekte)
        9: AREA_SPECIAL_OPPONENT (Spezialfelder links für Gegner-Effekte)
    - B (2. Ziffer): Anzahl angrenzender Idle-Felder (0-2 für alle Bereiche außer Idle)
    - CD (3.-4. Ziffer): Fortlaufende Nummer (00-99)

    Wichtige Regeln:
    - Nur die formale Gültigkeit (Länge, Bereich, Idle-Count, Nummer) wird hier geprüft.
    - Ob ein Hexfeld tatsächlich auf dem Board existiert (z. B. 3001-3003, 1001-1007),
      wird im Board-Modul geprüft (z. B. über Board.is_valid_position()).
    """

    # Bereichs-Konstanten
    AREA_AVATAR = 0       # Avatar-Felder (ohne Einfluss)
    AREA_PLAYER = 1
    AREA_OPPONENT = 2
    AREA_IDLE = 3
    AREA_PREVIEW_PLAYER = 4
    AREA_PREVIEW_OPPONENT = 5
    AREA_BACK_PLAYER = 6
    AREA_BACK_OPPONENT = 7
    AREA_SPECIAL_PLAYER = 8
    AREA_SPECIAL_OPPONENT = 9

    # Mapping: Bereich -> Liste der möglichen Idle-Anzahlen
    VALID_IDLE_COUNTS: Dict[int, List[int]] = {
        AREA_AVATAR: [0],                # Avatar: keine Idle-Nachbarn
        AREA_PLAYER: [0, 1, 2],          # Spieler-Lane: 0-2 Idles angrenzend
        AREA_OPPONENT: [0, 1, 2],        # Gegner-Lane: 0-2 Idles angrenzend
        AREA_IDLE: [0],                  # Idle-Felder: IMMER 0
        AREA_PREVIEW_PLAYER: [0],        # Preview-Spieler: keine Idle-Nachbarn
        AREA_PREVIEW_OPPONENT: [0],      # Preview-Gegner: keine Idle-Nachbarn
        AREA_BACK_PLAYER: [0, 1, 2],      # Back-Spieler: 0-2 Idles angrenzend
        AREA_BACK_OPPONENT: [0, 1, 2],    # Back-Gegner: 0-2 Idles angrenzend
        AREA_SPECIAL_PLAYER: [0, 1, 2],   # Spezial-Spieler: 0-2 Idles angrenzend
        AREA_SPECIAL_OPPONENT: [0, 1, 2]  # Spezial-Gegner: 0-2 Idles angrenzend
    }

    def __init__(self, hex_id: str):
        """
        Initialisiert ein HexID-Objekt aus einer 4-stelligen String-ID.

        Args:
            hex_id (str): 4-stellige HexID (z. B. "1205" oder "3001").

        Raises:
            ValueError: Wenn die ID ungültig ist (Länge != 4, ungültiger Bereich/Idle-Count/Nummer).
        """
        if len(hex_id) != 4:
            raise ValueError(f"HexID must be 4 digits, got '{hex_id}' (length: {len(hex_id)})")

        self._raw_id = hex_id
        self.area = int(hex_id[0])
        self.idle_count = int(hex_id[1])
        self.number = int(hex_id[2:])

        self._validate()

    def _validate(self) -> None:
        """Validiert die HexID gegen die formalen Regeln (nicht Board-spezifisch!)."""
        if self.area not in self.VALID_IDLE_COUNTS:
            raise ValueError(f"Invalid area: {self.area} (must be 0-9)")
        if self.idle_count not in self.VALID_IDLE_COUNTS[self.area]:
            raise ValueError(
                f"Invalid idle_count: {self.idle_count} for area {self.area}. "
                f"Valid values: {self.VALID_IDLE_COUNTS[self.area]}"
            )
        if not (0 <= self.number <= 99):
            raise ValueError(f"Invalid number: {self.number} (must be 00-99)")

    # Rest der Klasse bleibt unverändert (get_neighbors, from_coordinates, etc.)
    @property
    def raw_id(self) -> str:
        """Gibt die ursprüngliche 4-stellige ID zurück."""
        return self._raw_id

    def __repr__(self) -> str:
        return f"HexID('{self._raw_id}')"

    def __eq__(self, other: object) -> bool:
        """Vergleicht zwei HexIDs."""
        if not isinstance(other, HexID):
            return False
        return self._raw_id == other._raw_id

    def __hash__(self) -> int:
        """Ermöglicht die Verwendung in Sets/Dicts."""
        return hash(self._raw_id)

    def get_neighbors(self) -> List['HexID']:
        """
        Gibt alle angrenzenden Hexfelder zurück.
        Berücksichtigt die Bereichslogik:
        - Spieler/Gegner-Felder (1/2) → Idle-Felder (3xxx) mit gleicher Nummer.
        - Idle-Felder (3) → Spieler- (1xxx) und Gegnerfelder (2xxx) mit gleicher Nummer.
        - Spezialfelder (8/9) → Idle-Felder (3xxx) + Spieler-/Gegner-Lane (1/2).
        - Back-Bereiche (6/7) → Idle-Felder (3xxx) + Spezialfelder (8/9).
        - Avatar-Felder (0) → Keine Nachbarn.
        """
        neighbors = []

        if self.area == self.AREA_AVATAR:
            # Avatar-Felder haben keine Nachbarn
            pass

        elif self.area == self.AREA_PLAYER:
            # Spieler-Lane: Nachbarn sind Idle-Felder (3xxx) mit gleicher Nummer
            neighbors.append(HexID(f"3{self.idle_count}{self.number:02d}"))

        elif self.area == self.AREA_OPPONENT:
            # Gegner-Lane: Nachbarn sind Idle-Felder (3xxx) mit gleicher Nummer
            neighbors.append(HexID(f"3{self.idle_count}{self.number:02d}"))

        elif self.area == self.AREA_IDLE:
            # Idle-Felder: Nachbarn sind Spieler- (1xxx) und Gegnerfelder (2xxx) mit gleicher Nummer
            neighbors.append(HexID(f"10{self.number:02d}"))  # Spieler
            neighbors.append(HexID(f"20{self.number:02d}"))  # Gegner

        elif self.area == self.AREA_PREVIEW_PLAYER:
            # Preview-Spieler: Keine Nachbarn
            pass

        elif self.area == self.AREA_PREVIEW_OPPONENT:
            # Preview-Gegner: Keine Nachbarn
            pass

        elif self.area == self.AREA_BACK_PLAYER:
            # Back-Spieler: Nachbarn sind Idle-Felder (3xxx) und Spezialfelder (8xxx)
            neighbors.append(HexID(f"3{self.idle_count}{self.number:02d}"))
            neighbors.append(HexID(f"80{self.number:02d}"))

        elif self.area == self.AREA_BACK_OPPONENT:
            # Back-Gegner: Nachbarn sind Idle-Felder (3xxx) und Spezialfelder (9xxx)
            neighbors.append(HexID(f"3{self.idle_count}{self.number:02d}"))
            neighbors.append(HexID(f"90{self.number:02d}"))

        elif self.area == self.AREA_SPECIAL_PLAYER:
            # Spezial-Spieler: Nachbarn sind Idle-Felder (3xxx) und Spieler-Lane (1xxx)
            neighbors.append(HexID(f"3{self.idle_count}{self.number:02d}"))
            neighbors.append(HexID(f"10{self.number:02d}"))

        elif self.area == self.AREA_SPECIAL_OPPONENT:
            # Spezial-Gegner: Nachbarn sind Idle-Felder (3xxx) und Gegner-Lane (2xxx)
            neighbors.append(HexID(f"3{self.idle_count}{self.number:02d}"))
            neighbors.append(HexID(f"20{self.number:02d}"))

        return neighbors

    def is_adjacent_to(self, other: 'HexID') -> bool:
        """Prüft, ob dieses Hexfeld an `other` angrenzt."""
        return other in self.get_neighbors()

    @staticmethod
    def from_coordinates(x: int, y: int) -> 'HexID':
        """
        Konvertiert Koordinaten (x, y) in eine HexID.
        Anordnung:
        - y=0: AREA_AVATAR (0xxx) - Avatar-Feld
        - y=1: AREA_PLAYER (1xxx) - Spieler-Lane
        - y=2: AREA_OPPONENT (2xxx) - Gegner-Lane
        - y=3: AREA_IDLE (3xxx) - Idle-Felder (nur 3001-3003)
        - y=4: AREA_PREVIEW_PLAYER (4xxx) - Preview-Bereich Spieler
        - y=5: AREA_PREVIEW_OPPONENT (5xxx) - Preview-Bereich Gegner
        - y=6: AREA_BACK_PLAYER (6xxx) - Back-Spieler
        - y=7: AREA_BACK_OPPONENT (7xxx) - Back-Gegner
        - y=8: AREA_SPECIAL_PLAYER (8xxx) - Spezial-Spieler
        - y=9: AREA_SPECIAL_OPPONENT (9xxx) - Spezial-Gegner
        """
        if y == 0:
            return HexID(f"00{x:02d}")  # AREA_AVATAR
        elif y == 1:
            return HexID(f"10{x:02d}")  # AREA_PLAYER
        elif y == 2:
            return HexID(f"20{x:02d}")  # AREA_OPPONENT
        elif y == 3:
            return HexID(f"30{x:02d}")  # AREA_IDLE
        elif y == 4:
            return HexID(f"40{x:02d}")  # AREA_PREVIEW_PLAYER
        elif y == 5:
            return HexID(f"50{x:02d}")  # AREA_PREVIEW_OPPONENT
        elif y == 6:
            return HexID(f"60{x:02d}")  # AREA_BACK_PLAYER
        elif y == 7:
            return HexID(f"70{x:02d}")  # AREA_BACK_OPPONENT
        elif y == 8:
            return HexID(f"80{x:02d}")  # AREA_SPECIAL_PLAYER
        elif y == 9:
            return HexID(f"90{x:02d}")  # AREA_SPECIAL_OPPONENT
        else:
            raise ValueError(f"Invalid y-coordinate: {y} (must be 0-9)")

    @staticmethod
    def get_idle_fields() -> List['HexID']:
        """
        Gibt alle Idle-Felder (Bereich 3) zurück.
        Die 3 Idle-Felder sind fix: 3001, 3002, 3003.
        """
        return [HexID("3001"), HexID("3002"), HexID("3003")]