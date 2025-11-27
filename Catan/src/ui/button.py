import pygame

from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager



class Button:
    def __init__(self, layout_props: dict, surface: pygame.Surface, font, game_manager: "GameManager", callback: Optional[Callable] = None, shown: bool = True) -> None:
        self.game_manager = game_manager

        # Initialize defaults so read_layout() can fall back reliably
        self.name = ""
        self.text = ""
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.color = (0, 0, 0)

        # read layout and override default values
        self.read_layout(layout_props)

        self.surface = surface
        self.game_font = font
        self.shown = shown
        self.hovering = False
        # Optional callback to run when clicked
        self.callback = callback

    def trigger(self):
        if self.callback:
            self.callback()

    def draw(self, surface: pygame.Surface) -> None:
        if not self.shown:
            return
        # Draw using the provided surface explicitly
        pygame.draw.rect(surface, self.color, self.rect) #change this to include backgrounds
        text = self.game_font.render(self.text, False, (0, 0, 0))
        surface.blit(text, (self.rect[0], self.rect[1]))

    def read_layout(self, layout: dict) -> None:
        # Schema reference: See [layout.json](./config/layout.json#L23-L41)

        self.name = layout.get("name", self.name)
        rect_data = layout.get("rect", [self.rect.x, self.rect.y, self.rect.width, self.rect.height])
        self.rect = pygame.Rect(rect_data[0], rect_data[1], rect_data[2], rect_data[3])
        color_data = layout.get("color", [self.color[0], self.color[1], self.color[2]])
        self.color = (color_data[0], color_data[1], color_data[2])
        self.text = layout.get("text", self.text)

    def get_layout(self) -> dict:
        return {
            "name": self.name,
            "rect": [self.rect.x, self.rect.y, self.rect.width, self.rect.height],
            "color": [self.color[0], self.color[1], self.color[2]],
            "text": self.text
        }
    
    #TODO: implement settings read/write
    def read_settings(self, settings: dict) -> None:
        pass

    def get_settings(self) -> dict:
        return {}

    def hide(self) -> None:
        self.shown = False

    def show(self) -> None:
        self.shown = True