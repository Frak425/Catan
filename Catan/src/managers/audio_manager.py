import pygame

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.managers.game_manager import GameManager
    from src.managers.input_manager import InputManager
    from src.managers.helper_manager import HelperManager
    from src.managers.player_manager import PlayerManager
    from src.managers.graphics_manager import GraphicsManager
    

class AudioManager:
    def init(self):
        pass

    def set_game_manager(self, game_manager: 'GameManager'):
        self.game_manager = game_manager 
    
    def set_input_manager(self, input_manager: 'InputManager'):
        self.input_manager = input_manager

    def set_helper_manager(self, helper_manager: 'HelperManager'):
        self.helper_manager = helper_manager

    def set_player_manager(self, player_manager: 'PlayerManager'):
        self.player_manager = player_manager

    def set_graphics_manager(self, graphics_manager: 'GraphicsManager'):
        self.graphics_manager = graphics_manager