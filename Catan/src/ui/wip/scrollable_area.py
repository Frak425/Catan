import pygame
from src.ui.elements.slider import Slider

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

class ScrollableArea:
    def __init__(self, game_manager: GameManager, wrapper_rect: pygame.Rect, content_height: int, exterior_padding: int, interior_padding, scroll_bar_width: int, content_background_image: pygame.Surface | None, scroll_bar_image: pygame.Surface | None, scroll_handle_image: pygame.Surface | None, background_image: pygame.Surface | None, content_background_color: tuple = (255, 255, 255, 1), scroll_bar_color: tuple = (200, 200, 200, 1), scroll_handle_color: tuple = (100, 100, 100, 1), scroll_bar_side: str = "right", background_color: tuple = (255, 255, 255, 1)):
        self.game_manager = game_manager
        
        self.rect = wrapper_rect
        self.content_height = content_height
        self.exterior_padding = exterior_padding
        self.interior_padding = interior_padding
        self.scroll_bar_width = scroll_bar_width

        self.background_color = background_color
        self.background_image = background_image
        self.content_background_image = content_background_image
        self.content_background_color = content_background_color
        self.scroll_bar_side = scroll_bar_side
        self.scroll_bar_image = scroll_bar_image
        self.scroll_bar_color = scroll_bar_color
        self.scroll_handle_color = scroll_handle_color
        self.scroll_handle_image = scroll_handle_image

        self.scroll_y = 0
        self.max_scroll = max(0, content_height - (self.rect.height - 2 * (self.exterior_padding)))

        self.create_surfaces()

    def create_surfaces(self):
        self.background_surface = pygame.Surface((self.rect.width, self.rect.height))
        if self.background_image:
            self.background_surface.blit(self.background_image, (0, 0))
        else:
            self.background_surface.fill(self.background_color)

        self.content_surface = pygame.Surface((self.rect.width - 2 * (self.exterior_padding + self.scroll_bar_width), self.content_height))
        if self.content_background_image:
            self.content_surface.blit(self.content_background_image, (0, 0))
        else:
            self.content_surface.fill(self.content_background_color)
        if self.scroll_bar_side == "right":
            self.scroll_bar_rect = pygame.Rect(self.rect.right - self.exterior_padding - self.scroll_bar_width, self.rect.y + self.exterior_padding, self.scroll_bar_width, self.rect.height - 2 * self.exterior_padding)
        else:
            self.scroll_bar_rect = pygame.Rect(self.rect.x + self.exterior_padding, self.rect.y + self.exterior_padding, self.scroll_bar_width, self.rect.height - 2 * self.exterior_padding)
        
        layout_props = {
            "name": "scroll_slider",
            "rect": [0, 0, self.scroll_bar_width, 50],
            "wrapper_rect": [self.scroll_bar_rect.x, self.scroll_bar_rect.y, self.scroll_bar_rect.width, self.scroll_bar_rect.height],
            "min_value": 0,
            "max_value": self.max_scroll,
            "bar_color": [self.scroll_bar_color[0], self.scroll_bar_color[1], self.scroll_bar_color[2]],
            "handle_color": [self.scroll_handle_color[0], self.scroll_handle_color[1], self.scroll_handle_color[2]],
            "handle_radius": self.scroll_bar_width // 2,
            "direction": "vertical",
            "handle_shape": "stadium"
        }
        
        self.scroll_slider = Slider(
            layout_props,
            1,  # initial_value
            self.game_manager,
            bar_image=self.scroll_bar_image
        )

    def update_scroll(self, new_scroll_y: int):
        self.scroll_y = max(0, min(self.max_scroll, new_scroll_y))
        self.scroll_slider.value = self.scroll_y
        self.scroll_slider.slider_position = self.scroll_slider.calculate_slider_position(self.scroll_y)

    #draws from the bottom up, background surface is blitted last and refreshed every frame. This will be made more efficient later, but for now it works.
    def draw(self, surface: pygame.Surface):
        #refresh background surface
        if self.background_image:
            self.background_surface.blit(self.background_image, (0, 0))
        else:
            self.background_surface.fill(self.background_color)

        #blit content surface
        self.background_surface.blit(self.content_surface, (self.exterior_padding, self.exterior_padding))
        
        #blit scroll bar
        self.scroll_slider.draw(self.background_surface)

        #draw to main surface
        surface.blit(self.background_surface, (self.rect.x, self.rect.y))

        