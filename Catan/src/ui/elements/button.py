import pygame

from typing import TYPE_CHECKING, Callable, Optional
from src.ui.ui_element import UIElement

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager



class Button(UIElement):

    text_color: tuple[int, int, int]

    def __init__(self, layout_props: dict, font, game_manager: "GameManager", callback: Optional[Callable] = None, shown: bool = True) -> None:
        # Initialize element-specific defaults
        self.text = ""
        self.color = (0, 0, 0)
        self.text_color = (0, 0, 0)
        
        # Call parent constructor
        super().__init__(layout_props, game_manager, callback, shown)
        
        self.game_font = font
        self.hovering = False
        
        # read layout after setting defaults
        self.read_layout(layout_props)

    def draw(self, surface: pygame.Surface) -> None:
        if not self.shown:
            return
        # Draw using the provided surface explicitly
        pygame.draw.rect(surface, self.color, self.rect) #change this to include backgrounds
        text = self.game_font.render(self.text, False, (0, 0, 0))
        surface.blit(text, (self.rect[0], self.rect[1]))

        if self.is_active:
            self.draw_guiding_lines(surface)

    def read_layout(self, layout: dict) -> None:
        # Schema reference: See [layout.json](./config/layout.json#L23-L41)
        self._read_common_layout(layout)
        
        color_data = layout.get("color", [self.color[0], self.color[1], self.color[2]])
        self.color = (color_data[0], color_data[1], color_data[2])
        self.text = layout.get("text", self.text)

    def get_layout(self) -> dict:
        layout = self._get_common_layout()
        layout.update({
            "color": [self.color[0], self.color[1], self.color[2]],
            "text": self.text,
            "shown": self.shown
        })
        return layout
    
    def update_text(self, new_text: str) -> None:
        self.text = new_text
    