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
        self.color = (200, 200, 200)
        self.text = ""
        self.text_color = (0, 0, 0)
        self.padding = 5
        self.text_align = "center"

        self.border_radius = 0
        self.border_top_right_radius = 0
        self.border_top_left_radius = 0
        self.border_bottom_right_radius = 0
        self.border_bottom_left_radius = 0
        
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
            self.surface.fill(self.color)

        self.set_text_align(self.text_align)

    def set_text_align(self, text_align: str) -> None:
        if text_align == "center":
            self.text_rect.center = self.surface.get_rect().center
        elif text_align == "left":
            self.text_rect.midleft = (self.padding, self.surface.get_rect().centery)
        elif text_align == "right":
            self.text_rect.midright = (self.surface.get_rect().width - self.padding, self.surface.get_rect().centery)

    def update_text(self, new_text: str) -> None:
        self.text = new_text
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect()
        self.set_text_align(self.text_align)

    def update_text_color(self, new_color: tuple[int, int, int]) -> None:
        self.text_color = new_color
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect()
        self.set_text_align(self.text_align)

    def draw(self, surface: pygame.Surface) -> None:
        if not self.shown:
            return
        
        # Get absolute position for drawing
        abs_rect = self.get_absolute_rect()
        
        # Blit the background and text to the surface
        self.surface.fill(self.color)
        self.surface.blit(self.text_surface, self.text_rect)
        surface.blit(self.surface, abs_rect.topleft)

        if self.is_active:
            self.draw_guiding_lines(surface)

    def read_layout(self, layout_props: dict) -> None:
        # Schema reference: See [layout.json](./config/layout.json#L219-L239)
        self._read_common_layout(layout_props)
        
        color_data = layout_props.get("color", [self.color[0], self.color[1], self.color[2]])
        self.color = (color_data[0], color_data[1], color_data[2])
        self.text = layout_props.get("text", self.text)
        text_color_data = layout_props.get("text_color", [self.text_color[0], self.text_color[1], self.text_color[2]])
        self.text_color = (text_color_data[0], text_color_data[1], text_color_data[2])
        self.padding = layout_props.get("padding", self.padding)
        self.text_align = layout_props.get("text_align", self.text_align)

    def get_layout(self) -> dict:
        layout = self._get_common_layout()
        layout.update({
            "_type": "TextDisplay",
            "color": [self.color[0], self.color[1], self.color[2]],
            "text": self.text,
            "text_color": [self.text_color[0], self.text_color[1], self.text_color[2]],
            "padding": self.padding,
            "text_align": "center",
            "shown": self.shown,
            "border_radius": self.border_radius,
            "border_top_right_radius": self.border_top_right_radius,
            "border_top_left_radius": self.border_top_left_radius,
            "border_bottom_right_radius": self.border_bottom_right_radius,
            "border_bottom_left_radius": self.border_bottom_left_radius
        })
        return layout
    
    def print_info(self) -> None:
        self.print_common_info()
        print(f"TextDisplay: {self.name}")
        print(f"Text: {self.text}")
        print(f"Color: {self.color}")
        print(f"Text Color: {self.text_color}")
        print(f"Padding: {self.padding}")
        print(f"Text Align: {self.text_align}")
        print(f"Rect: {self.rect}")
        print(f"border_radius: {self.border_radius}")
        print(f"border_top_right_radius: {self.border_top_right_radius}")
        print(f"border_top_left_radius: {self.border_top_left_radius}")
        print(f"border_bottom_right_radius: {self.border_bottom_right_radius}")
        print(f"border_bottom_left_radius: {self.border_bottom_left_radius}")