import pygame
from src.managers.base_manager import BaseManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.managers.game.game_manager import GameManager
    from src.managers.input.input_manager import InputManager
    from src.managers.helper.helper_manager import HelperManager
    from src.managers.audio.audio_manager import AudioManager
    from src.managers.graphics.graphics_manager import GraphicsManager

class PlayerManager(BaseManager):
    def __init__(self):
        super().__init__()
        
    def initialize(self) -> None:
        """Initialize manager after all dependencies are injected."""
        self.game_manager = self.get_dependency('game_manager')
        self.input_manager = self.get_dependency('input_manager')
        self.helper_manager = self.get_dependency('helper_manager')
        self.audio_manager = self.get_dependency('audio_manager')
        self.graphics_manager = self.get_dependency('graphics_manager')
        
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

        self.graphics_manager = graphics_manager