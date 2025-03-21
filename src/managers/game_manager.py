import pygame
from pygame import *

class GameManager:
    def __init__(self, screen: Surface) -> None:
        self.screen = screen
        self.screen_size = (self.screen.get_width, self.screen.get_height)
        
        self.points_to_win = 10
        self.game_difficulty = "easy"

    def set_game_difficulty(self, new_diff: str) -> None:
        """Updated the games difficulty when playing against AI"""
        self.game_difficulty = new_diff

    def set_points_to_win(self, new_points: int) -> None:
        """Changes the points required to win"""
        self.points_to_win = new_points