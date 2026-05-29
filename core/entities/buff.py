from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class Buff:
    value: int
    target: Optional[str] = None
    target_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"value": self.value, "target": self.target, "target_type": self.target_type}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Buff':
        return cls(value=data.get("value", 0), target=data.get("target"), target_type=data.get("target_type"))