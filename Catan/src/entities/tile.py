import pygame
import math
import random

from src.entities.node import Node

class Tile:
    def __init__(self, resource_type: str, color: tuple, center: tuple, number: int, points: list[tuple], screen) -> None:
        self.resource_type = resource_type #"sheep", "brick", etc.
        self.points = points #list of corners in the form (x, y). Different from self.nodes because it's used to draw each polygon
        self.color = color
        self.center = center
        self.number = number
        self.screen = screen

    def draw_tile(self) -> None:
        pygame.draw.polygon(self.screen, self.color, self.points)