"""
Debug State - Einfacher State für Test- und Debug-Zwecke.
Verwaltet den aktuellen Spielzustand während manueller Tests.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class DebugState:
    """
    Einfacher State für manuelle Tests und Debugging.
    
    Attributes:
        mode: Aktueller Modus (z.B. "debugging", "testing")
        phase: Aktuelle Phase (z.B. "manual_testing", "might_calculation")
        current_test: Aktueller Testname (z.B. "Test 5: Fülle mit Entities")
        board_state: Beliebige Daten zum Board-Zustand
        custom_data: Flexibles Dict für test-spezifische Daten
    """
    mode: str = "debugging"
    phase: str = "manual_testing"
    current_test: Optional[str] = None
    board_state: Dict[str, Any] = field(default_factory=dict)
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def set_test(self, test_name: str) -> None:
        """Setzt den aktuellen Test."""
        self.current_test = test_name
        self.phase = f"test_{test_name}"

    def clear_test(self) -> None:
        """Löscht den aktuellen Test."""
        self.current_test = None
        self.phase = "manual_testing"
        self.custom_data.clear()

    def update_board_state(self, key: str, value: Any) -> None:
        """Aktualisiert den Board-State."""
        self.board_state[key] = value

    def get_board_state(self, key: str, default: Any = None) -> Any:
        """Gibt einen Wert aus dem Board-State zurück."""
        return self.board_state.get(key, default)

    def update_custom_data(self, key: str, value: Any) -> None:
        """Aktualisiert benutzerdefinierte Daten."""
        self.custom_data[key] = value

    def get_custom_data(self, key: str, default: Any = None) -> Any:
        """Gibt benutzerdefinierte Daten zurück."""
        return self.custom_data.get(key, default)

    def reset(self) -> None:
        """Setzt den State komplett zurück."""
        self.mode = "debugging"
        self.phase = "manual_testing"
        self.current_test = None
        self.board_state.clear()
        self.custom_data.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert den State in ein Dictionary."""
        return {
            "mode": self.mode,
            "phase": self.phase,
            "current_test": self.current_test,
            "board_state": self.board_state.copy(),
            "custom_data": self.custom_data.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DebugState':
        """Erstellt einen DebugState aus einem Dictionary."""
        return cls(
            mode=data.get("mode", "debugging"),
            phase=data.get("phase", "manual_testing"),
            current_test=data.get("current_test"),
            board_state=data.get("board_state", {}),
            custom_data=data.get("custom_data", {})
        )
