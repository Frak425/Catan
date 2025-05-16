import pygame
from pygame import *
from src.managers.game_manager import GameManager

class Board:
    def __init__(self, game_manager: GameManager):
        self.game_manager = game_manager

    def handle_events(self):
        pass
    
    def draw(self):
        pass