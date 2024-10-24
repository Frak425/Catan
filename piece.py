import pygame
import math
import random

class Piece:
    def __init__(self, type: str, color: tuple[int], location: tuple[int], points: list[tuple[int]], rotation: int, screen) -> None:
        self.type = type
        self.color = color
        self.location = location
        self.points = points
        self.rotation = rotation
        self.screen = screen

        self.surface = pygame.Surface(100, 100)
        pygame.draw.polygon(self.surface, self.color, self.points)
        pygame.transform.rotate(self.surface, self.rotation)

    def draw_piece(self):
        self.screen.blit(self.surface, self.location)