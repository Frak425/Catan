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
        board: Board = self.init_board()
        menu: Menu = self.create_menu()
        test = 1

    def init_board(self) -> Board:
        for i in range(self.players_num):
            self.players_list.append(Player(self.player_colors, self.points_to_win))

        global board
        board = Board(self.screen_w / 27.32, self.screen_h, self.screen_w, self.num_tiles, self.screen, self.game_font, self.font_size)
        board.assign_tile_locations()
        board.assign_tiles()
        board.assign_tile_classes()
        return board

    def create_menu(self) -> Menu:
        menu_margins = (50, 50) #top, bottom
        menu_size = (self.screen_w - 2 * menu_margins[0], self.screen_h - 2 * menu_margins[1])
        init_location = (self.screen_w + menu_margins[0], menu_margins[1]) #of top left corner
        final_location = menu_margins #of top left corner
        background_color = (100, 100, 100)
        menu = Menu(self.screen, self.game_font, "static", menu_size, init_location, final_location, bckg_color=background_color)
        return menu


    def set_game_difficulty(self, new_diff: str) -> None:
        """Updated the games difficulty when playing against AI"""
        self.game_difficulty = new_diff

    def set_points_to_win(self, new_points: int) -> None:
        """Changes the points required to win"""
        self.points_to_win = new_points

    def update_state(self, new_state):
        self.game_state = new_state

    def quit(self):
        pygame.quit()