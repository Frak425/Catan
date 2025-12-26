import pygame

from typing import TYPE_CHECKING, Callable, Optional
from src.ui.ui_element import UIElement

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager



class Button(UIElement):

    text_color: tuple[int, int, int]

    def __init__(self, layout_props: dict, font: pygame.font.Font, game_manager: "GameManager", background_image: pygame.Surface | None = None, callback: Optional[Callable] = None, shown: bool = True) -> None:
        # Initialize element-specific defaults
        self.text = ""
        self.color = (0, 0, 0)
        self.padding = 5
        self.text_color = (0, 0, 0)
        self.text_align = "center"
        self.font = font
        self.disabled = False

        self.border_radius = 0
        self.border_top_right_radius = 0
        self.border_top_left_radius = 0
        self.border_bottom_right_radius = 0
        self.border_bottom_left_radius = 0
        
        # Call parent constructor
        super().__init__(layout_props, game_manager, callback, shown)
        
        self.game_font = font
        self.hovering = False
        self.selected = False
        self.background_image = background_image

        self.text_surface = self.game_font.render(self.text, False, self.text_color)
        self.text_rect = self.text_surface.get_rect()
        
        if self.background_image:
            self.surface = self.background_image
        else:
            self.surface = pygame.Surface((self.text_rect.width + 2 * self.padding, self.text_rect.height + 2 * self.padding))
            self.surface.fill(self.color)

        self.set_text_align(self.text_align)

        # read layout after setting defaults
        self.read_layout(layout_props)

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

    def set_text_align(self, text_align: str) -> None:
        if text_align == "center":
            self.text_rect.center = self.surface.get_rect().center
        elif text_align == "left":
            self.text_rect.midleft = (self.padding, self.surface.get_rect().centery)
        elif text_align == "right":
            self.text_rect.midright = (self.surface.get_rect().width - self.padding, self.surface.get_rect().centery)


    def draw(self, surface: pygame.Surface) -> None:
        if not self.shown:
            return
        
        # Apply visual state modifications
        draw_color = self.color
        draw_text_color = self.text_color
        
        if self.disabled:
            # Darken disabled buttons
            draw_color = tuple(int(c * 0.5) for c in self.color)
            draw_text_color = tuple(int(c * 0.5) for c in self.text_color)
        elif self.hovering:
            # Lighten on hover
            draw_color = tuple(min(255, int(c * 1.2)) for c in self.color)
        
        # Draw using the provided surface explicitly
        pygame.draw.rect(surface, draw_color, self.rect)
        text = self.game_font.render(self.text, False, draw_text_color)
        surface.blit(text, self.get_text_rect(text))

        if self.is_active:
            self.draw_guiding_lines(surface)

    def get_text_rect(self, text_surface: pygame.Surface) -> pygame.Rect:
        text_rect = text_surface.get_rect()
        if self.text_align == "center":
            text_rect.center = self.rect.center
        elif self.text_align == "left":
            text_rect.midleft = (self.rect.left + 5, self.rect.centery)
        elif self.text_align == "right":
            text_rect.midright = (self.rect.right - 5, self.rect.centery)
        return text_rect

    def read_layout(self, layout: dict) -> None:
        # Schema reference: See [layout.json](./config/layout.json#L23-L41)
        self._read_common_layout(layout)
        
        color_data = layout.get("color", [self.color[0], self.color[1], self.color[2]])
        self.color = (color_data[0], color_data[1], color_data[2])
        self.text = layout.get("text", self.text)
        text_color_data = layout.get("text_color", [self.text_color[0], self.text_color[1], self.text_color[2]])
        self.text_color = (text_color_data[0], text_color_data[1], text_color_data[2])
        self.padding = layout.get("padding", self.padding)
        self.text_align = layout.get("text_align", self.text_align)

    def get_layout(self) -> dict:
        layout = self._get_common_layout()
        layout.update({
            "color": [self.color[0], self.color[1], self.color[2]],
            "text_align": "center",
            "text": self.text,
            "shown": self.shown,
            "padding": self.padding,
            "text_color": [self.text_color[0], self.text_color[1], self.text_color[2]],
            "border_radius": self.border_radius,
            "border_top_right_radius": self.border_top_right_radius,
            "border_top_left_radius": self.border_top_left_radius,
            "border_bottom_right_radius": self.border_bottom_right_radius,
            "border_bottom_left_radius": self.border_bottom_left_radius
        })
        
        # Save callback name if it exists - do reverse lookup in callback registry
        if hasattr(self, 'callback') and self.callback:
            callback_name = None
            if hasattr(self.game_manager, 'input_manager'):
                if hasattr(self.game_manager.input_manager, 'ui_factory'):
                    if hasattr(self.game_manager.input_manager.ui_factory, 'callback_registry'):
                        for name, func in self.game_manager.input_manager.ui_factory.callback_registry.items():
                            if func == self.callback:
                                callback_name = name
                                break
            
            if callback_name:
                layout["callback"] = callback_name
        
        return layout
    
    #print all layout info
    def print_info(self) -> None:
        self.print_common_info()
        print(f"Button: {self.name}")
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
        print(f"Shown: {self.shown}")
        print(f"")