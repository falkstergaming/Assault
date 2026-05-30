from typing import List, Optional, Dict, TYPE_CHECKING
from core.entities.base_entity import BaseEntity
from core.entities.buff import Buff
from core.game.board import Board
from core.utils.hex_id import HexID

if TYPE_CHECKING:
    from core.game.board import Board


class MightCalculator:
    """
    Zentrale Klasse für Might-Berechnungen.
    
    Berechnet den Might-Wert für ein Hexfeld basierend auf:
    1. base_might aller Entities auf dem Feld
    2. Buffs nach Prioritätenreihenfolge:
       - neighbor (von angrenzenden Entities)
       - opponent (von gegenüberliegender Entity)
       - faction (für alle Entities der gleichen Faction)
       - targeted (für spezifische Entities)
       - self (nur bei Alt-State aktiv)
    
    Location Self-Buffs wirken automatisch, wenn eine Figur darauf steht.
    """

    def __init__(self, board: Board):
        self.board = board

    def calculate_might_for_hex(self, hex_id: HexID) -> float:
        """
        Berechnet den finalen Might-Wert für ein Hexfeld.
        
        Summiert base_might aller Entities + alle anwendbaren Buffs.
        Buffs werden nach Prioritätenreihenfolge berechnet.
        
        Args:
            hex_id: Die HexID des Feldes
            
        Returns:
            Der gesamte Might-Wert des Feldes (>= 0)
        """
        entities = self.board.get_entities_on_hex(hex_id)
        
        # 1. Summiere base_might aller Entities
        base_might = sum(entity.base_might for entity in entities)
        
        # 2. Berechne alle Buffs für dieses Feld
        buffs = self._calculate_buffs_for_hex(hex_id, entities)
        
        total_might = base_might + buffs
        return max(0, total_might)

    def get_might_split(self, hex_id: HexID) -> List[float]:
        """
        Gibt den maximalen might_split aller Entities auf dem Feld zurück.
        
        Args:
            hex_id: Die HexID des Feldes
            
        Returns:
            Liste mit 2 Werten (für die beiden Idle-Felder)
        """
        entities = self.board.get_entities_on_hex(hex_id)
        if not entities:
            return [0.5, 0.5]  # Default
        return [
            max(e.might_split[0] for e in entities),
            max(e.might_split[1] for e in entities)
        ]

    def _calculate_buffs_for_hex(self, hex_id: HexID, entities: List[BaseEntity]) -> float:
        """
        Berechnet alle Buffs für ein Hexfeld nach Prioritätenreihenfolge.
        
        Prioritäten:
        1. neighbor - Buffs von angrenzenden Entities (links/rechts)
        2. opponent - Buffs von gegenüberliegender Entity  
        3. faction - Buffs für alle Entities der gleichen Faction
        4. targeted - Buffs für spezifische Entities
        5. self - Self-Buffs (nur bei Alt-State oder Location mit Figur)
        
        Args:
            hex_id: Die HexID des Feldes
            entities: Liste der Entities auf diesem Feld
            
        Returns:
            Summe aller anwendbaren Buff-Werte
        """
        total_buff = 0.0
        
        # 2. Neighbor-Buffs: von angrenzenden Entities
        total_buff += self._get_neighbor_buffs(hex_id, entities)
        
        # 3. Opponent-Buffs: von gegenüberliegender Entity
        total_buff += self._get_opponent_buffs(hex_id, entities)
        
        # 4. Faction-Buffs: für alle Entities der gleichen Faction
        total_buff += self._get_faction_buffs(entities)
        
        # 5. Targeted-Buffs: für spezifische Entities
        total_buff += self._get_targeted_buffs(entities)
        
        # 6. Self-Buffs: nur bei Alt-State oder Location mit Figur
        total_buff += self._get_self_buffs(hex_id, entities)
        
        return total_buff

    def _get_neighbor_buffs(self, hex_id: HexID, entities: List[BaseEntity]) -> float:
        """
        Berechnet Neighbor-Buffs von angrenzenden Entities.
        Nur Entities auf logischen Nachbarfeldern (links/rechts, max 2).
        """
        neighbor_entities = self.board.get_neighbor_entities(hex_id)
        buff_value = 0.0
        
        for entity in entities:
            for neighbor in neighbor_entities:
                # Jede Entity gibt ihre neighbor-Buffs an ihre Nachbarn
                for buff in neighbor.buffs.get("neighbor", []):
                    if self._buff_applies_to_entity(buff, entity):
                        buff_value += buff.value
        
        return buff_value

    def _get_opponent_buffs(self, hex_id: HexID, entities: List[BaseEntity]) -> float:
        """
        Berechnet Opponent-Buffs von der gegenüberliegenden Entity.
        """
        opponent = self.board.get_opponent_entity(hex_id)
        if opponent is None:
            return 0.0
        
        buff_value = 0.0
        for entity in entities:
            for buff in opponent.buffs.get("opponent", []):
                # Opponent-Buffs wirken auf alle Entities (ohne Target-Prüfung laut README)
                buff_value += buff.value
        
        return buff_value

    def _get_faction_buffs(self, entities: List[BaseEntity]) -> float:
        """
        Berechnet Faction-Buffs für alle Entities der gleichen Faction.
        """
        buff_value = 0.0
        
        for entity in entities:
            if not entity.faction:
                continue
            
            # Faction-Buffs der Entity selbst
            for buff in entity.buffs.get("faction", []):
                if buff.target_type == "faction" and buff.target == entity.faction:
                    buff_value += buff.value
        
        return buff_value

    def _get_targeted_buffs(self, entities: List[BaseEntity]) -> float:
        """
        Berechnet Targeted-Buffs für spezifische Entities (per ID oder Name).
        """
        buff_value = 0.0
        
        for entity in entities:
            for buff in entity.buffs.get("targeted", []):
                if self._buff_applies_to_entity(buff, entity):
                    buff_value += buff.value
        
        return buff_value

    def _get_self_buffs(self, hex_id: HexID, entities: List[BaseEntity]) -> float:
        """
        Berechnet Self-Buffs (nur bei Alt-State aktiv oder Location mit Figur).
        """
        buff_value = 0.0
        
        for entity in entities:
            # Self-Buffs wirken nur, wenn:
            # - Entity ist im Alt-State (entity.alt == True)
            # - ODER Entity ist eine Location und eine Figur steht darauf
            if self._should_apply_self_buffs(entity, hex_id):
                for buff in entity.buffs.get("self", []):
                    buff_value += buff.value
        
        return buff_value

    def _should_apply_self_buffs(self, entity: BaseEntity, hex_id: HexID) -> bool:
        """
        Prüft, ob Self-Buffs für die Entity gelten.
        
        Self-Buffs wirken, wenn:
        - Die Entity im Alt-State ist (entity.alt == True)
        - ODER die Entity eine Location ist und eine Figur darauf steht
        """
        if entity.alt:
            return True
        if entity.type == "location":
            return self.board.get_figure_at(hex_id) is not None
        return False

    def _buff_applies_to_entity(self, buff: Buff, entity: BaseEntity) -> bool:
        """
        Prüft, ob ein Buff auf die gegebene Entity zutrifft.
        
        Args:
            buff: Der Buff
            entity: Die Entity, die den Buff erhalten soll
            
        Returns:
            True, wenn der Buff auf die Entity zutrifft
        """
        # Faction: Buff trifft zu, wenn Entity zur Ziel-Faction gehört
        if buff.target_type == "faction" and entity.faction:
            return buff.target == entity.faction
        
        # Tag: Buff trifft zu, wenn Entity den Ziel-Tag hat
        if buff.target_type == "tag" and entity.tags:
            return buff.target in entity.tags
        
        # ID: Buff trifft zu, wenn Entity die Ziel-ID hat
        if buff.target_type == "id":
            return buff.target == entity.id
        
        # Pool: Buff trifft zu, wenn Entity zum Ziel-Pool gehört
        if buff.target_type == "pool":
            # Pool-Logik: z.B. "Good", "Evil", "Neutral", "Horde"
            from core.utils.global_constants import FACTION_POOLS
            if entity.faction in FACTION_POOLS:
                for pool, factions in FACTION_POOLS.items():
                    if entity.faction in factions and buff.target == pool:
                        return True
        
        # self: Buff trifft immer auf die Entity selbst zu (wird in _get_self_buffs geprüft)
        if buff.target_type == "self":
            return True
        
        return False