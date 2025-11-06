import pygame
import numpy as np
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_manager import GameManager
    from input_manager import InputManager
    from helper_manager import HelperManager

class GraphicsManager:
    def __init__(self, time):
        self.game_manager = None
        self.input_manager = None
        self.menu_open = False
        self.time = time

    def set_game_manager(self, game_manager: 'GameManager'):
        self.game_manager = game_manager

    def set_helper_manager(self, helper_manager: 'HelperManager'):
        self.helper_manager = helper_manager

    def set_input_manager(self, input_manager: 'InputManager'):
        self.input_manager = input_manager

    def draw_screen(self):

        if (self.game_manager.game_state == "main_menu"):
            for button_name, button in self.input_manager.buttons["main_menu"].items():
                button.draw()

        elif (self.game_manager.game_state == "setup"):       
            for button_name, button in self.input_manager.buttons["setup"].items():
                button.draw()

            for slider_name, slider in self.input_manager.sliders["setup"].items():
                slider.draw(self.game_manager.screen)

            for text_display_name, text_display in self.input_manager.text_displays["setup"].items():
                text_display.draw(self.game_manager.screen)

        elif (self.game_manager.game_state == "init"):
            self.game_manager.init_board()
            self.game_manager.game_state = "game"

        elif (self.game_manager.game_state == "game"):
            self.game_manager.board.draw_board()
            for button_name, button in self.input_manager.buttons["game"].items():
                button.draw()

            for image_name, image in self.input_manager.images["game"].items():
                self.game_manager.screen.blit(image.surface, image.rect)

        else:
            print("wrong game state")
            self.game_manager.running = False

        self.draw_menu()
            
    def draw_menu(self):
        if self.menu_open:
            self.input_manager.menu.draw(self.time)