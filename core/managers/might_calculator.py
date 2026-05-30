from typing import List, Optional, Dict
from core.entities.base_entity import BaseEntity
from core.game.board import Board
from core.utils import HexID
from core.entities.base_entity import Buff  # Importiere die Buff-Klasse

class MightCalculator:
    """Zentrale Klasse für Might-Berechnungen."""

    def __init__(self, board: Board):
        self.board = board

    def calculate_might_for_hex(self, hex_id: HexID) -> float:
        """Berechnet den finalen Might-Wert für ein Hexfeld."""
        entities = self.board.get_entities_on_hex(hex_id)
        base_might = self._sum_base_might(entities)
        buffs = self._calculate_buffs(hex_id, entities)
        return base_might + buffs

    def _sum_base_might(self, entities: List[BaseEntity]) -> float:
        """Summiert die base_might aller Entities auf dem Feld."""
        return sum(entity.base_might for entity in entities)

    def _calculate_buffs(self, hex_id: HexID, entities: List[BaseEntity]) -> float:
        """Berechnet alle Buffs für die Entities auf dem Feld."""
        buffs = 0
        buffs += self._get_neighbor_buffs(hex_id, entities)
        buffs += self._get_opponent_buffs(hex_id, entities)
        buffs += self._get_faction_buffs(entities)
        buffs += self._get_targeted_buffs(entities)
        buffs += self._get_self_buffs(entities)  # Nur für Alt-State-Entities
        return buffs

    def _get_might_split(self, hex_id: HexID) -> List[float]:
        """Gibt den maximalen might_split aller Entities auf dem Feld zurück."""
        entities = self.board.get_entities_on_hex(hex_id)
        return [
            max(e.might_split[0] for e in entities),
            max(e.might_split[1] for e in entities)
        ]
    
    def calculate_might(
        self,
        entity: BaseEntity,
        hex_id: str,
        neighbor_entities: Optional[List[BaseEntity]] = None,
        opponent: Optional[BaseEntity] = None
    ) -> int:
        """
        Berechnet den Might-Wert einer Entity inkl. aller Buffs.
        Args:
            entity: Die Entity, deren Might berechnet wird.
            hex_id: Hex-ID der Entity (für Nachbarn/Location-Prüfung).
            neighbor_entities: Liste der angrenzenden Entities (optional, wird sonst vom Board geholt).
            opponent: Gegenüberliegende Entity (optional, wird sonst vom Board geholt).
        Returns:
            Might-Wert (>= 0).
        """
        might = entity.base_might

        # 1. Self-Buffs (nur wenn Alt-State aktiv ODER Location mit Figur)
        if self._should_apply_self_buffs(entity, hex_id):
            for buff in entity.buffs["self"]:
                might += buff.value

        # 2. Neighbor-Buffs
        if neighbor_entities is None:
            neighbor_entities = self.board.get_neighbor_entities(hex_id)
        for neighbor in neighbor_entities:
            for buff in neighbor.buffs["neighbor"]:
                if self._buff_applies(buff, entity):
                    might += buff.value

        # 3. Opponent-Buffs
        if opponent is None:
            opponent = self.board.get_opponent_entity(hex_id)
        if opponent:
            for buff in opponent.buffs["opponent"]:
                might += buff.value

        # 4. Faction-Buffs
        for buff in entity.buffs["faction"]:
            if buff.target_type == "faction" and buff.target in (entity.faction or ""):
                might += buff.value

        # 5. Targeted-Buffs
        for buff in entity.buffs["targeted"]:
            might += buff.value

        # 6. Location-Buffs (wenn Figur auf Location steht)
        location = self.board.get_location_at(hex_id)
        if location and entity.type == "figure":
            for buff in location.buffs["self"]:
                might += buff.value

        return max(0, might)

    def _should_apply_self_buffs(self, entity: BaseEntity, hex_id: str) -> bool:
        """Prüft, ob Self-Buffs für die Entity gelten."""
        if entity.alt:
            return True
        if entity.type == "location":
            return self.board.get_figure_at(hex_id) is not None
        return False

    def _buff_applies(self, buff: 'Buff', entity: BaseEntity) -> bool:
        """Prüft, ob ein Buff auf die Entity zutrifft."""
        if buff.target_type == "faction" and buff.target in (entity.faction or ""):
            return True
        if buff.target_type == "tag" and buff.target in entity.tags:
            return True
        if buff.target_type == "id" and buff.target == entity.id:
            return True
        return False