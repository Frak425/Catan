import pygame

from typing import TYPE_CHECKING, Callable, Optional
from src.ui.ui_element import UIElement

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

class Image(UIElement):
    def __init__(self, layout_props: dict, game_manager: 'GameManager', callback: Optional[Callable] = None):
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

    def draw(self, surface: pygame.surface.Surface):
        if self.shown:
            surface.blit(self.surface, (self.rect.x, self.rect.y))
        if self.is_active:
            self.draw_guiding_lines(surface)
    
    def read_layout(self, layout: dict) -> None:
        self._read_common_layout(layout)
        self.image_path = layout.get("image_path", self.image_path)
        if self.image_path and hasattr(self, 'surface'):
            self.image = pygame.image.load(self.image_path).convert_alpha()
            self.surface.blit(self.image, (0, 0))

    def get_layout(self) -> dict:
        layout = self._get_common_layout()
        layout.update({
            "image_path": self.image_path,
            "shown": self.shown
        })
        return layout
    
    def print_info(self) -> None:
        self.print_common_info()
        print(f"Image Path: {self.image_path}")
        