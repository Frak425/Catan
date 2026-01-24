import pygame

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.managers.game_manager import GameManager
    from src.managers.input.input_manager import InputManager
    from src.managers.helper_manager import HelperManager
    from src.managers.audio_manager import AudioManager
    from src.managers.graphics_manager import GraphicsManager

class PlayerManager:
    def init(self, player_list: list):
        self.players = player_list
        self.current_turn = 0

    def next_turn(self) -> None:
        """Moves turn to the next player"""
        pass

    def current_player(self):
        """Return a reference to the current player"""
        return self.players[self.current_turn]

    def get_player_resources(self, player_name: str) -> object:
        """Returns the specified player's resources"""
        pass

    def perform_action(self, action: str, *args) -> None:
        pass

    def check_winner(self):
        for player in self.players:
            if player.points > 10:
                return player

        return None
    
    def set_game_manager(self, game_manager: 'GameManager'):
        self.game_manager = game_manager

    def set_input_manager(self, input_manager: 'InputManager'):
        self.input_manager = input_manager

    def set_helper_manager(self, helper_manager: 'HelperManager'):
        self.helper_manager = helper_manager

    def set_audio_manager(self, audio_manager: 'AudioManager'):
        self.audio_manager = audio_manager

    def set_graphics_manager(self, graphics_manager: 'GraphicsManager'):
        self.graphics_manager = graphics_manager