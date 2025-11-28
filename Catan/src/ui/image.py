import pygame

from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

class Image:
    def __init__(self, layout_props: dict, game_manager: 'GameManager', callback: Optional[Callable] = None):
        self.game_manager = game_manager

        # initialize defaults so read_layout() can fall back reliably
        self.name = ""
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.image_path = ""
        self.default_color = (150, 150, 150)
        self.guiding_line_color = (100, 100, 200)
        self.is_active = False

        # read layout and override default values
        self.read_layout(layout_props)

        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.shown = True
        if self.image_path:
            self.image = pygame.image.load(self.image_path).convert_alpha()
            self.surface.blit(self.image, (0, 0))
        else:
            self.surface.fill(self.default_color)
        # optional callback
        self.callback = callback

    def trigger(self):
        if self.callback:
            self.callback()

    def draw(self, surface: pygame.surface.Surface):
        if self.shown:
            surface.blit(self.surface, (self.rect.x, self.rect.y))
        if self.is_active:
            self.draw_guiding_lines(surface)
    
    def read_layout(self, layout: dict) -> None:
        self.name = layout.get("name", self.name)
        rect_data = layout.get("rect", [self.rect.x, self.rect.y, self.rect.width, self.rect.height])
        self.rect = pygame.Rect(rect_data[0], rect_data[1], rect_data[2], rect_data[3])
        self.image_path = layout.get("image_path", self.image_path)
        if self.image_path:
            self.image = pygame.image.load(self.image_path).convert_alpha()
            self.surface.blit(self.image, (0, 0))

    def get_layout(self) -> dict:
            layout = {
                "name": self.name,
                "rect": [self.rect.x, self.rect.y, self.rect.width, self.rect.height],
                "image_path": self.image_path,
                "shown": self.shown,
                "guiding_line_color": [self.guiding_line_color[0], self.guiding_line_color[1], self.guiding_line_color[2]]
            }
            return layout
    #TODO: implement settings read/write
    def read_settings(self, settings: dict) -> None:
        pass

    def get_settings(self) -> dict:
        return {}

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
    