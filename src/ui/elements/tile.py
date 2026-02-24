import pygame
import math
from typing import TYPE_CHECKING, Any

from pygame.event import Event

if TYPE_CHECKING:
    from src.managers.game.game_manager import GameManager

from src.ui.ui_element import UIElement

class Tile(UIElement):
    def __init__(self, game_manager: 'GameManager', props: dict, image: pygame.Surface | None = None, callback=None):
        super().__init__(props, game_manager, callback, True)
        self.image = image

        self.create_draw_surface()

    def create_draw_surface(self):
        self.draw_surface = self.image if self.image else pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)

        if not self.image:
            #create hexagon shape on draw surface
            points = []
            for i in range(6):
                angle = i * 60
                x = self.rect.w / 2 + self.rect.w / 2 * math.cos(math.radians(angle))
                y = self.rect.h / 2 + self.rect.h / 2 * math.sin(math.radians(angle))
                points.append((x, y))
            pygame.draw.polygon(self.draw_surface, self.color , points)


    def _handle_own_event(self, event: Event) -> bool:
        return super()._handle_own_event(event)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.draw_surface, self.rect.topleft)
        self.draw_inactive_overlay(surface)

        if self.is_active:
            self.draw_guiding_lines(surface)

    def read_layout(self, layout: dict):
        self._read_common_layout(layout)
        self.color = tuple(layout.get("color", [255, 255, 255]))

    def get_layout(self) -> dict:
        layout = self._get_common_layout()
        layout.update({
            'type': '_Tile',
            "color": [self.color[0], self.color[1], self.color[2]],
        })
        return layout
    
    def print_info(self):
        self.print_common_info()