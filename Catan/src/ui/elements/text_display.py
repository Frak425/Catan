import pygame
import math

from typing import TYPE_CHECKING, Callable, Optional
from src.ui.ui_element import UIElement

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

class TextDisplay(UIElement):

    text_color: tuple[int, int, int]

    def __init__(self, layout_props: dict, game_manager: GameManager, font: pygame.font.Font, background_image: pygame.Surface | None = None, callback: Optional[Callable] = None, shown: bool = True) -> None:
        # Initialize element-specific defaults
        self.background_color = (200, 200, 200)
        self.text = ""
        self.text_color = (0, 0, 0)
        self.padding = 5
        
        # Call parent constructor
        super().__init__(layout_props, game_manager, callback, shown)
        
        self.font = font
        self.background_image = background_image
        
        # read layout after setting defaults
        self.read_layout(layout_props)

        # Render the text surface
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect()

        # Create the background surface
        if self.background_image:
            self.surface = self.background_image
        else:
            self.surface = pygame.Surface((self.text_rect.width + 2 * self.padding, self.text_rect.height + 2 * self.padding))
            self.surface.fill(self.background_color)

    def update_text(self, new_text: str) -> None:
        self.text = new_text
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect()

    def draw(self, surface: pygame.Surface) -> None:
        # Center the text on the background
        self.text_rect.center = self.surface.get_rect().center

        # Blit the background and text to the surface
        self.surface.fill(self.background_color)
        self.surface.blit(self.text_surface, self.text_rect)
        surface.blit(self.surface, self.rect)

        if self.is_active:
            self.draw_guiding_lines(surface)

    def read_layout(self, layout_props: dict) -> None:
        # Schema reference: See [layout.json](./config/layout.json#L219-L239)
        self._read_common_layout(layout_props)
        
        color_data = layout_props.get("color", [self.background_color[0], self.background_color[1], self.background_color[2]])
        self.background_color = (color_data[0], color_data[1], color_data[2])
        self.text = layout_props.get("text", self.text)
        text_color_data = layout_props.get("text_color", [self.text_color[0], self.text_color[1], self.text_color[2]])
        self.text_color = (text_color_data[0], text_color_data[1], text_color_data[2])
        self.padding = layout_props.get("padding", self.padding)

    def get_layout(self) -> dict:
        layout = self._get_common_layout()
        layout.update({
            "color": [self.background_color[0], self.background_color[1], self.background_color[2]],
            "text": self.text,
            "text_color": [self.text_color[0], self.text_color[1], self.text_color[2]],
            "padding": self.padding
        })
        return layout
    