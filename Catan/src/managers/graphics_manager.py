import pygame
import numpy as np
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_manager import GameManager
    from src.managers.input.input_manager import InputManager
    from helper_manager import HelperManager
    from player_manager import PlayerManager
    from audio_manager import AudioManager

class GraphicsManager:
    def init(self, time):
        self.menu_open = False
        self.time = time

        self.home_ui_draw_funcs = [lambda: self.draw_ui("buttons", "home"), lambda: self.draw_ui("text_displays", "home"), lambda: self.draw_ui("images", "home"), lambda: self.draw_ui("sliders", "home"), lambda: self.draw_ui("toggles", "home")]
        self.setup_ui_draw_funcs = [lambda: self.draw_ui("buttons", "setup"), lambda: self.draw_ui("text_displays", "setup"), lambda: self.draw_ui("images", "setup"), lambda: self.draw_ui("sliders", "setup"), lambda: self.draw_ui("toggles", "setup")]
        self.game_ui_draw_funcs = [lambda: self.draw_ui("buttons", "game"), lambda: self.draw_ui("text_displays", "game"), lambda: self.draw_ui("images", "game"), lambda: self.draw_ui("sliders", "game"), lambda: self.draw_ui("toggles", "game")]

    def set_ui_by_type(self):
        self.ui_by_type = {
            "buttons": self.input_manager.buttons,
            "images": self.input_manager.images,
            "text_displays": self.input_manager.text_displays,
            "sliders": self.input_manager.sliders,
            "toggles": self.input_manager.toggles
        }

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

        if (self.game_manager.game_state == "home"):
            for func in self.home_ui_draw_funcs:
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
            self.input_manager.menu.draw(self.game_manager.screen, self.time)

    def draw_ui(self, type: str, layer: str):
        for element_name, element in self.ui_by_type[type][layer].items():
            element.draw(self.game_manager.screen)
