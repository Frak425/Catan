import pygame
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager


class UIElement(ABC):
    """Base class for all UI elements with common functionality."""
    
    def __init__(self, layout_props: dict, game_manager: 'GameManager', callback: Optional[Callable] = None, shown: bool = True):
        self.game_manager = game_manager
        self.callback = callback
        self.shown = shown
        
        # Initialize common defaults
        self.name = ""
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.guiding_line_color = (100, 100, 200)
        self.is_active = False
        
        # Subclasses can add their own defaults before calling read_layout
        
    def trigger(self):
        """Execute the callback if one is assigned."""
        if self.callback:
            self.callback()
    
    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the UI element to the surface. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def read_layout(self, layout_props: dict) -> None:
        """Read layout properties from config. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_layout(self) -> dict:
        """Get layout properties as dict. Must be implemented by subclasses."""
        pass
    
    def read_settings(self, settings: dict) -> None:
        """Read settings from config. Can be overridden by subclasses."""
        pass
    
    def get_settings(self) -> dict:
        """Get settings as dict. Can be overridden by subclasses."""
        return {}
    
    def hide(self) -> None:
        """Hide the UI element."""
        self.shown = False
    
    def show(self) -> None:
        """Show the UI element."""
        self.shown = True
    
    def dev_mode_drag(self, x: int, y: int) -> None:
        """Move the UI element by the given offset in dev mode."""
        self.rect.x += x
        self.rect.y += y
    
    def draw_guiding_lines(self, surface: pygame.Surface) -> None:
        """Draw rectangular guiding lines around the element in dev mode."""
        if self.game_manager.dev_mode:
            pygame.draw.line(surface, self.guiding_line_color, 
                           (self.rect.x, self.rect.y), 
                           (self.rect.x + self.rect.width, self.rect.y), 1)
            pygame.draw.line(surface, self.guiding_line_color, 
                           (self.rect.x, self.rect.y), 
                           (self.rect.x, self.rect.y + self.rect.height), 1)
            pygame.draw.line(surface, self.guiding_line_color, 
                           (self.rect.x + self.rect.width, self.rect.y), 
                           (self.rect.x + self.rect.width, self.rect.y + self.rect.height), 1)
            pygame.draw.line(surface, self.guiding_line_color, 
                           (self.rect.x, self.rect.y + self.rect.height), 
                           (self.rect.x + self.rect.width, self.rect.y + self.rect.height), 1)
    
    def _read_common_layout(self, layout_props: dict) -> None:
        """Helper to read common layout properties. Call this from subclass read_layout()."""
        self.name = layout_props.get("name", self.name)
        rect_data = layout_props.get("rect", [self.rect.x, self.rect.y, self.rect.width, self.rect.height])
        self.rect = pygame.Rect(rect_data[0], rect_data[1], rect_data[2], rect_data[3])
        guiding_line_color_data = layout_props.get("guiding_line_color", 
                                                    [self.guiding_line_color[0], 
                                                     self.guiding_line_color[1], 
                                                     self.guiding_line_color[2]])
        self.guiding_line_color = (guiding_line_color_data[0], 
                                   guiding_line_color_data[1], 
                                   guiding_line_color_data[2])
    
    def _get_common_layout(self) -> dict:
        """Helper to get common layout properties. Call this from subclass get_layout()."""
        return {
            "name": self.name,
            "rect": [self.rect.x, self.rect.y, self.rect.width, self.rect.height],
            "guiding_line_color": [self.guiding_line_color[0], 
                                  self.guiding_line_color[1], 
                                  self.guiding_line_color[2]]
        }
