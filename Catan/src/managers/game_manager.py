import pygame
from pygame import *

from src.entities.player import Player
from src.entities.board import Board
from src.ui.menu import Menu

class GameManager:
    def __init__(self, screen: Surface) -> None:
        self.running = True
        self.screen = screen
        self.screen_size = (self.screen.get_width(), self.screen.get_height())
        self.screen_w = self.screen_size[0]
        self.screen_h = self.screen_size[1]
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
        
        self.board = self.init_board()

    def init_board(self) -> Board:
        for i in range(self.players_num):
            self.players_list.append(Player(self.player_colors, self.points_to_win))

        global board
        board = Board(self.screen_w / 27.32, self.screen_h, self.screen_w, self.num_tiles, self.screen, self.game_font, self.font_size)
        board.assign_tile_locations()
        board.assign_tiles()
        board.assign_tile_classes()
        return board

    def set_menu(self, menu):
        self.menu = menu
