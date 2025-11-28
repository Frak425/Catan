import pygame

from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager



class Button:

    text_color: tuple[int, int, int]

    def __init__(self, layout_props: dict, surface: pygame.Surface, font, game_manager: "GameManager", callback: Optional[Callable] = None, shown: bool = True) -> None:
        self.game_manager = game_manager

        # Initialize defaults so read_layout() can fall back reliably
        self.name = ""
        self.text = ""
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.color = (0, 0, 0)
        self.guiding_line_color = (100, 100, 200)
        self.text_color = (0, 0, 0)

        #store is_active.inactive state for drawing guiding lines
        self.is_active = False

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

        if self.is_active:
            self.draw_guiding_lines(surface)

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
            "text": self.text,
            "shown": self.shown,
            "guiding_line_color": [self.guiding_line_color[0], self.guiding_line_color[1], self.guiding_line_color[2]]
        }
    
    #TODO: implement settings read/write
    def read_settings(self, settings: dict) -> None:
        pass

    def get_settings(self) -> dict:
        return {}

    def update_text(self, new_text: str) -> None:
        self.text = new_text

    def hide(self) -> None:
        self.shown = False

    def show(self) -> None:
        self.shown = True

    def dev_mode_drag(self, x: int, y: int) -> None:
        self.rect.x += x
        self.rect.y += y

    def draw_guiding_lines(self, surface: pygame.Surface) -> None:
        if self.game_manager.dev_mode:
            pygame.draw.line(surface, self.guiding_line_color, (self.rect.x, self.rect.y), (self.rect.x + self.rect.width, self.rect.y), 1)
            pygame.draw.line(surface, self.guiding_line_color, (self.rect.x, self.rect.y), (self.rect.x, self.rect.y + self.rect.height), 1)
            pygame.draw.line(surface, self.guiding_line_color, (self.rect.x + self.rect.width, self.rect.y), (self.rect.x + self.rect.width, self.rect.y + self.rect.height), 1)
            pygame.draw.line(surface, self.guiding_line_color, (self.rect.x, self.rect.y + self.rect.height), (self.rect.x + self.rect.width, self.rect.y + self.rect.height), 1)
    