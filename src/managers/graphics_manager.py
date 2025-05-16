import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_manager import GameManager
    from input_manager import InputManager
    from helper_manager import HelperManager

class GraphicsManager:
    def __init__(self):
        self.game_manager = None
        self.input_manager = None
        self.menu_open = False

    def set_game_manager(self, game_manager: 'GameManager'):
        self.game_manager = game_manager

    def set_helper_manager(self, helper_manager: 'HelperManager'):
        self.helper_manager = helper_manager

    def set_input_manager(self, input_manager: 'InputManager'):
        self.input_manager = input_manager

    def draw_screen(self):
        if (self.game_manager.game_state == "main_menu"):
            for button in self.input_manager.buttons["title_screen"]:
                button.draw_button()

        elif (self.game_manager.game_state == "game_setup"):       
            for button in self.input_manager.buttons["setup"]:
                button.draw_button()

        elif (self.game_manager.game_state == "init"):
            self.game_manager.init_board()
            self.game_manager.game_state = "game_ongoing"

        elif (self.game_manager.game_state == "game_ongoing"):
            self.game_manager.board.draw_board()
            for button in self.input_manager.buttons["board"]:
                button.draw_button()

        else:
            print("wrong game state")
            running = False
            
    def draw_menu(self):
        if self.menu_open:
            self.game_manager.menu.draw()