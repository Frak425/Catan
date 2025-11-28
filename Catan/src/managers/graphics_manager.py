import pygame
import numpy as np
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_manager import GameManager
    from input_manager import InputManager
    from helper_manager import HelperManager
    from player_manager import PlayerManager
    from audio_manager import AudioManager

class GraphicsManager:
    def init(self, time):
        self.menu_open = False
        self.time = time

        self.main_menu_ui_draw_funcs = [self.draw_main_menu_buttons, self.draw_main_menu_images, self.draw_main_menu_text_displays]
        self.setup_ui_draw_funcs = [self.draw_setup_buttons, self.draw_setup_sliders, self.draw_setup_text_displays]
        self.game_ui_draw_funcs = [self.draw_game_buttons, self.draw_game_images, self.draw_game_text_displays]

    def set_game_manager(self, game_manager: 'GameManager'):
        self.game_manager = game_manager

    def set_helper_manager(self, helper_manager: 'HelperManager'):
        self.helper_manager = helper_manager

    def set_input_manager(self, input_manager: 'InputManager'):
        self.input_manager = input_manager

    def set_player_manager(self, player_manager: 'PlayerManager'):
        self.player_manager = player_manager

    def set_audio_manager(self, audio_manager: 'AudioManager'):
        self.audio_manager = audio_manager

    def draw_screen(self):
        assert self.game_manager is not None, "GraphicsManager: game_manager not set"
        assert self.input_manager is not None, "GraphicsManager: input_manager not set"

        if (self.game_manager.game_state == "main_menu"):
            for func in self.main_menu_ui_draw_funcs:
                func()

        elif (self.game_manager.game_state == "setup"):       
            for func in self.setup_ui_draw_funcs:
                func()

        elif (self.game_manager.game_state == "init"):
            self.game_manager.init_board()
            self.game_manager.game_state = "game"

        elif (self.game_manager.game_state == "game"):
            self.game_manager.board.draw_board()

            for func in self.game_ui_draw_funcs:
                func()

        else:
            print("wrong game state")
            self.game_manager.running = False

        self.draw_menu()
            
    def draw_menu(self):
        if self.menu_open:
            assert self.input_manager is not None, "GraphicsManager: menu not set in InputManager"
            self.input_manager.menu.draw(self.time)

    def draw_main_menu_buttons(self):
        for button_name, button in self.input_manager.buttons["main_menu"].items():
            button.draw(self.game_manager.screen)

    def draw_main_menu_images(self):
        for image_name, image in self.input_manager.images["main_menu"].items():
            self.game_manager.screen.blit(image.surface, image.rect)

    def draw_main_menu_text_displays(self):
        for text_display_name, text_display in self.input_manager.text_displays["main_menu"].items():
            text_display.draw(self.game_manager.screen)

    def draw_setup_buttons(self):
        for button_name, button in self.input_manager.buttons["setup"].items():
            button.draw(self.game_manager.screen)

    def draw_setup_sliders(self):
        for slider_name, slider in self.input_manager.sliders["setup"].items():
            slider.draw(self.game_manager.screen)

    def draw_setup_text_displays(self):
        for text_display_name, text_display in self.input_manager.text_displays["setup"].items():
            text_display.draw(self.game_manager.screen)

    def draw_game_buttons(self):
        for button_name, button in self.input_manager.buttons["game"].items():
            button.draw(self.game_manager.screen)

    def draw_game_images(self):
        for image_name, image in self.input_manager.images["game"].items():
            self.game_manager.screen.blit(image.surface, image.rect)

    def draw_game_text_displays(self):
        for text_display_name, text_display in self.input_manager.text_displays["game"].items():
            text_display.draw(self.game_manager.screen)