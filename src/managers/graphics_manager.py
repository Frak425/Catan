import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_manager import GameManager
    from input_manager import InputManager

class GraphicsManager:
    def __init__(self, game_manager: GameManager, input_manager: InputManager):
        self.game_manager = game_manager
        self.input_manager = input_manager
        self.menu_open = False

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