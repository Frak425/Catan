import pygame
import numpy as np
from typing import TYPE_CHECKING
from src.managers.base_manager import BaseManager
if TYPE_CHECKING:
    from src.managers.game.game_manager import GameManager
    from src.managers.input.input_manager import InputManager
    from src.managers.helper.helper_manager import HelperManager
    from src.managers.player.player_manager import PlayerManager
    from src.managers.audio.audio_manager import AudioManager

class GraphicsManager(BaseManager):
    def __init__(self):
        super().__init__()
        
    def initialize(self) -> None:
        """Initialize manager after all dependencies are injected."""
        self.game_manager = self.get_dependency('game_manager')
        self.helper_manager = self.get_dependency('helper_manager')
        self.input_manager = self.get_dependency('input_manager')
        self.player_manager = self.get_dependency('player_manager')
        self.audio_manager = self.get_dependency('audio_manager')
        
    def init(self, time):
        self.menu_open = False
        self.time = time

        self.home_ui_draw_funcs = [lambda: self.draw_ui("images", "home"), lambda: self.draw_ui("text_displays", "home"), lambda: self.draw_ui("buttons", "home"), lambda: self.draw_ui("sliders", "home"), lambda: self.draw_ui("toggles", "home"), lambda: self.draw_ui("scrollable_areas", "home")]
        self.setup_ui_draw_funcs = [lambda: self.draw_ui("images", "setup"), lambda: self.draw_ui("text_displays", "setup"), lambda: self.draw_ui("buttons", "setup"), lambda: self.draw_ui("sliders", "setup"), lambda: self.draw_ui("toggles", "setup"), lambda: self.draw_ui("scrollable_areas", "setup")]
        self.game_ui_draw_funcs = [lambda: self.draw_ui("images", "game"), lambda: self.draw_ui("text_displays", "game"), lambda: self.draw_ui("buttons", "game"), lambda: self.draw_ui("sliders", "game"), lambda: self.draw_ui("toggles", "game"), lambda: self.draw_ui("scrollable_areas", "game")]

    def set_ui_by_type(self):
        self.ui_by_type = {
            "buttons": self.input_manager.buttons,
            "images": self.input_manager.images,
            "text_displays": self.input_manager.text_displays,
            "sliders": self.input_manager.sliders,
            "toggles": self.input_manager.toggles,
            "scrollable_areas": self.input_manager.scrollable_areas
        }

    def draw_screen(self):
        assert self.game_manager is not None, "GraphicsManager: game_manager not set"
        assert self.input_manager is not None, "GraphicsManager: input_manager not set"

        if hasattr(self.game_manager, "driver_manager") and self.game_manager.driver_manager:
            self.game_manager.driver_manager.evaluate_drivers()

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

        self.draw_menus()
            
    def draw_menus(self):
        """Draw all open menus sorted by z-index (higher z_index = drawn first = behind)."""
        if not self.input_manager or not hasattr(self.input_manager, 'menus'):
            return
        
        # Get all menus sorted by z-index (higher first, so they draw in back)
        sorted_menus = sorted(
            self.input_manager.menus.values(),
            key=lambda m: m.z_index,
            reverse=True
        )
        for menu in sorted_menus:
            # Menu.draw() checks menu.shown internally, so closed menus won't draw
            menu.draw(self.game_manager.screen, self.time)

    def draw_ui(self, type: str, layer: str):
        for element_name, element in self.ui_by_type[type][layer].items():
            element.draw(self.game_manager.screen)
