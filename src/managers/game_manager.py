import pygame
from pygame import *

class GameManager:
    def __init__(self, screen: Surface) -> None:
        self.screen = screen
        self.screen_size = (self.screen.get_width, self.screen.get_height)
        self.font_size = 20
        self.game_font = pygame.font.SysFont('Comic Sans', self.font_size)
        self.game_state = "main_menu" # main menu -> game setup -> init -> game ongoing -> game over -> main menu
        self.player_state = "roll" # roll -> trade -> buy -> place
        self.settings_open = False
        self.players_num = 2
        self.players_list = []
        self.players_list_index = 0
        self.player_colors = ["yellow", "blue", "green", "red"]
        self.player_color_chosen_index = 0
        self.game_difficulty = "easy"
        self.framerates = [30, 60, 120, 240]
        self.framerate_index = 0
        self.num_tiles = 19
        self.points_to_win = 10
        self.game_difficulty = "easy"

    def set_game_difficulty(self, new_diff: str) -> None:
        """Updated the games difficulty when playing against AI"""
        self.game_difficulty = new_diff

    def set_points_to_win(self, new_points: int) -> None:
        """Changes the points required to win"""
        self.points_to_win = new_points