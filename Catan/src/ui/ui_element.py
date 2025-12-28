import pygame
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Optional, List

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
        self.rect = pygame.Rect(0, 0, 0, 0)  # Position relative to parent
        self.guiding_line_color = (100, 100, 200)
        self.is_active = False
        
        # Hierarchical relationship management
        self.parent: Optional['UIElement'] = None
        self.children: List['UIElement'] = []
        self._absolute_rect: Optional[pygame.Rect] = None  # Cached screen coordinates
        
        # Subclasses can add their own defaults before calling read_layout
        
    def trigger(self):
        """Execute the callback if one is assigned."""
        if self.callback:
            self.callback()
    
    def add_child(self, child: 'UIElement') -> None:
        """Add a child element and set its parent reference."""
        child.parent = self
        self.children.append(child)
        child._invalidate_absolute_rect()
    
    def remove_child(self, child: 'UIElement') -> None:
        """Remove a child element."""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            child._invalidate_absolute_rect()
    
    def _invalidate_absolute_rect(self) -> None:
        """Mark absolute rect as needing recalculation."""
        self._absolute_rect = None
        for child in self.children:
            child._invalidate_absolute_rect()
    
    def get_absolute_rect(self) -> pygame.Rect:
        """Get rect in screen coordinates (accounting for all parent offsets)."""
        if self._absolute_rect is None:
            if self.parent:
                parent_rect = self.parent.get_absolute_rect()
                self._absolute_rect = pygame.Rect(
                    parent_rect.x + self.rect.x,
                    parent_rect.y + self.rect.y,
                    self.rect.width,
                    self.rect.height
                )
            else:
                self._absolute_rect = self.rect.copy()
        return self._absolute_rect
    
    def get_clip_rect(self) -> Optional[pygame.Rect]:
        """Get the clipping region for this element (in screen coordinates)."""
        if self.parent:
            return self.parent.get_clip_rect()
        return None
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle event and propagate to children. Returns True if consumed."""
        if not self.shown:
            return False
        
        # Let children handle first (reverse order for top-to-bottom)
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
        
        # Handle own event logic
        return self._handle_own_event(event)
    
    def _handle_own_event(self, event: pygame.event.Event) -> bool:
        """Override in subclasses to handle specific event logic."""
        return False
    
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
    
    @abstractmethod
    def print_info(self) -> None:
        """Print all variable info about the UI element. Must be implemented by subclasses."""
        pass

    def print_common_info(self) -> None:
        """Print common variable info about the UI element."""
        print(f"Name: {self.name}")
        print(f"Rect: {self.rect}")
        print(f"Shown: {self.shown}")
        print(f"Guiding Line Color: {self.guiding_line_color}")

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
        self._invalidate_absolute_rect()
    
    def draw_guiding_lines(self, surface: pygame.Surface) -> None:
        """Draw rectangular guiding lines around the element in dev mode."""
        if self.game_manager.dev_mode:
            abs_rect = self.get_absolute_rect()
            pygame.draw.line(surface, self.guiding_line_color, 
                           (abs_rect.x, abs_rect.y), 
                           (abs_rect.x + abs_rect.width, abs_rect.y), 1)
            pygame.draw.line(surface, self.guiding_line_color, 
                           (abs_rect.x, abs_rect.y), 
                           (abs_rect.x, abs_rect.y + abs_rect.height), 1)
            pygame.draw.line(surface, self.guiding_line_color, 
                           (abs_rect.x + abs_rect.width, abs_rect.y), 
                           (abs_rect.x + abs_rect.width, abs_rect.y + abs_rect.height), 1)
            pygame.draw.line(surface, self.guiding_line_color, 
                           (abs_rect.x, abs_rect.y + abs_rect.height), 
                           (abs_rect.x + abs_rect.width, abs_rect.y + abs_rect.height), 1)
    
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
        
        # Store pending children names for deferred loading
        # (children must be created before they can be added)
        if "children" in layout_props:
            self._pending_children_names = layout_props["children"]
    
    def restore_child_relationships(self, element_registry: dict) -> None:
        """Restore child relationships after all elements are loaded.
        
        Args:
            element_registry: Dict mapping element names to UIElement instances
        """
        if hasattr(self, '_pending_children_names'):
            for child_name in self._pending_children_names:
                if child_name in element_registry:
                    child = element_registry[child_name]
                    # Only add if not already a child (avoid duplicates)
                    if child not in self.children:
                        self.add_child(child)
            # Clear pending list after processing
            delattr(self, '_pending_children_names')
    
    def _get_common_layout(self) -> dict:
        """Helper to get common layout properties. Call this from subclass get_layout()."""
        layout = {
            "name": self.name,
            "rect": [self.rect.x, self.rect.y, self.rect.width, self.rect.height],
            "guiding_line_color": [self.guiding_line_color[0], 
                                  self.guiding_line_color[1], 
                                  self.guiding_line_color[2]]
        }
        
        # Serialize children by name (if they have names)
        if self.children:
            children_names = [child.name for child in self.children if child.name]
            if children_names:
                layout["children"] = children_names
        
        return layout
