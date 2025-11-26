import pygame

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

class Image:
    def __init__(self, game_manager: GameManager, name: str, rect: pygame.Rect, image_path: str | None = None, default_color: tuple[int, int, int] = (100, 100, 100)):
        self.name = name
        self.rect = rect
        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.image_path = image_path
        if self.image_path:
            self.image = pygame.image.load(self.image_path).convert_alpha()
            self.surface.blit(self.image, (0, 0))
        else:
            self.surface.fill(default_color)


    def draw(self, surface: pygame.surface.Surface):
        surface.blit(self.surface, (self.rect.x, self.rect.y))
        