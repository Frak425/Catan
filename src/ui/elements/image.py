from dataclasses import field

from attr import dataclass
from attrs import fields
import pygame

from typing import TYPE_CHECKING, Callable, Optional
from src.ui.ui_element import UIElement, UIElementInfo

if TYPE_CHECKING:
    from src.managers.game.game_manager import GameManager

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
        self.image: pygame.Surface | None = None
        self._last_surface_signature: tuple | None = None
        
        # Call parent constructor
        super().__init__(layout_props, game_manager, callback, shown=True)
        
        # read layout after setting defaults
        self.read_layout(layout_props)

        for name, value in vars(self.layout).items():
            setattr(self, name, value)

        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self._rebuild_surface()

    def _rebuild_surface(self) -> None:
        """Recreate display surface and scale image/fallback fill to current rect size."""
        size = (max(1, int(self.rect.width)), max(1, int(self.rect.height)))
        self.surface = pygame.Surface(size, pygame.SRCALPHA)

        if self.image_path:
            self.image = pygame.image.load(self.image_path).convert_alpha()
            if self.image.get_size() != size:
                scaled = pygame.transform.smoothscale(self.image, size)
            else:
                scaled = self.image
            self.surface.blit(scaled, (0, 0))
        else:
            self.image = None
            self.surface.fill(self.default_color)

        self._last_surface_signature = self._get_surface_signature()

    def _get_surface_signature(self) -> tuple:
        """Return a signature for values that affect the rendered surface."""
        return (
            int(self.rect.width),
            int(self.rect.height),
            self.image_path,
            tuple(self.default_color),
        )

    ## --- RENDERING --- ##

    def draw(self, surface: pygame.surface.Surface, time: int):
        """Draw image surface at absolute position."""
        if not self.shown:
            return
        
        self.update()

        # Ensure visual surface matches current size/path/color inputs.
        if self._last_surface_signature != self._get_surface_signature():
            self._rebuild_surface()
        
        # Get absolute position for drawing
        abs_rect = self.get_absolute_rect()
        if self.animation:
            frame = self.animation.get_current_frame()
            if frame.get_size() != self.rect.size:
                frame = pygame.transform.scale(frame, self.rect.size)
            surface.blit(frame, abs_rect.topleft)
        else:
            surface.blit(self.surface, abs_rect.topleft)

        self.draw_inactive_overlay(surface, abs_rect)
        
        if self.is_active:
            self.draw_guiding_lines(surface)

    def _invalidate_absolute_rect(self) -> None:
        """Invalidate cached absolute rect and rebuild image surface if size changed."""
        super()._invalidate_absolute_rect()
        if not hasattr(self, 'surface'):
            return
        if self._last_surface_signature != self._get_surface_signature():
            self._rebuild_surface()
    
    ## --- SERIALIZATION --- ##
    
    def read_layout(self, layout: dict) -> None:
        """
        Load image properties and reload image if path changes.
        
        Note: Reloads image if surface already exists (for runtime updates).
        """
        field_names = {f.name for f in fields(ImageInfo)}
        self.layout = ImageInfo(
            common_layout=self._get_common_layout(),
            **{k: v for k, v in layout.items() if k in field_names}
        )
        if hasattr(self, 'surface'):
            self._rebuild_surface()

    def get_layout(self) -> ImageInfo:
        """Serialize image properties (path and visibility)."""
        layout = ImageInfo(
            common_layout=self._get_common_layout(),
            image_path=self.image_path,
            default_color=[self.default_color[0], self.default_color[1], self.default_color[2]]
        )
        return layout
    
    def print_info(self) -> None:
        """Print image properties for debugging."""
        self.print_common_info()
        print(f"Image Path: {self.image_path}")

@dataclass
class ImageInfo:
    common_layout: UIElementInfo
    image_path: str = ""
    default_color: list[int] = field(default_factory=lambda: [255, 255, 255])