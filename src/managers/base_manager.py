from abc import ABC, abstractmethod
from typing import Any, Dict
import pygame

class BaseManager(ABC):
    def __init__(self):
        self._dependencies: Dict[str, Any] = {}
    
    def inject(self, name: str, manager: Any) -> None:
        """Inject a dependency by name."""
        self._dependencies[name] = manager
    
    def get_dependency(self, name: str) -> Any:
        """Get an injected dependency."""
        return self._dependencies.get(name)
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize manager after all dependencies are injected."""
        pass
    
    def update(self) -> None:
        """Per-frame update hook (optional override)."""
        pass