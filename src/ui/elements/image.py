import pygame

from typing import TYPE_CHECKING, Callable, Optional
from src.ui.ui_element import UIElement

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

class Image(UIElement):
    """
    Static image display with fallback color.
    
    Features:
    - Load and display image from file path
    - Fallback to solid color if no image provided
    - Non-interactive (can have callback but no built-in event handling)
    """
    def __init__(self, layout_props: dict, game_manager: 'GameManager', callback: Optional[Callable] = None):
        """
        Initialize image display from file path or default color.
        
        Args:
            layout_props: Configuration from layout.json
            game_manager: Central game state manager
            callback: Optional callback (not used by Image)
        
        Properties:
        - image_path: Path to image file (empty string = use default_color)
        - default_color: Fallback color if no image provided
        """
        # Initialize element-specific defaults
        self.image_path = ""
        self.default_color = (150, 150, 150)
        
        # Call parent constructor
        super().__init__(layout_props, game_manager, callback, shown=True)
        
        # read layout after setting defaults
        self.read_layout(layout_props)

        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        if self.image_path:
            self.image = pygame.image.load(self.image_path).convert_alpha()
            self.surface.blit(self.image, (0, 0))
        else:
            self.surface.fill(self.default_color)

    ## --- RENDERING --- ##

    def draw(self, surface: pygame.surface.Surface):
        """Draw image surface at absolute position."""
        if not self.shown:
            return
        
        self.update()
        
        # Get absolute position for drawing
        abs_rect = self.get_absolute_rect()
        surface.blit(self.surface, abs_rect.topleft)
        
        if self.is_active:
            self.draw_guiding_lines(surface)
    
    ## --- SERIALIZATION --- ##
    
    def read_layout(self, layout: dict) -> None:
        """
        Load image properties and reload image if path changes.
        
        Note: Reloads image if surface already exists (for runtime updates).
        """
        self._read_common_layout(layout)
        self.image_path = layout.get("image_path", self.image_path)
        if self.image_path and hasattr(self, 'surface'):
            self.image = pygame.image.load(self.image_path).convert_alpha()
            self.surface.blit(self.image, (0, 0))

    def get_layout(self) -> dict:
        """Serialize image properties (path and visibility)."""
        layout = self._get_common_layout()
        layout.update({
            "_type": "Image",
            "image_path": self.image_path,
            "shown": self.shown
        })
        return layout
    
    def print_info(self) -> None:
        """Print image properties for debugging."""
        self.print_common_info()
        print(f"Image Path: {self.image_path}")
