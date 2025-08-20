import pygame
import math

class PlacementIndicator:
    def __init__(self, rect: pygame.Rect, item_type: str, color: tuple[int, int, int], min_radius: int = 5, max_radius: int = 10):
        self.rect = rect
        self.color = color
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.radius = (max_radius - min_radius) / 2
        self.surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))  # Transparent background
        self.animating = False
        self.item_type = item_type

    def set_animating(self, time: int):
        self.animating = True
        self.start_time = time

    def stop_animating(self):
        self.animating = False

    def update_radius(self, new_time: int):
        if self.animating:
            return math.sin((new_time - self.start_time) / 200) * (self.max_radius - self.min_radius) / 2 + (self.max_radius + self.min_radius) / 2

    def update(self, new_time: int):
        if self.animating:
            #animate circle growing and shrinking with sine wave
            self.radius = self.update_radius(new_time)    

    def draw(self, surface: pygame.Surface):
        self.surface.fill((0, 0, 0, 0))
        pygame.draw.circle(self.surface, self.color, (self.rect.width // 2, self.rect.height // 2), int(self.radius), 2)
        surface.blit(self.surface, self.rect.topleft)