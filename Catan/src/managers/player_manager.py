import pygame
from src.entities.player import Player

class PlayerManager:
    def __init__(self, player_list: list[Player]):
        self.players = player_list
        self.current_turn = 0

    def next_turn(self) -> None:
        """Moves turn to the next player"""
        pass

    def current_player(self) -> Player:
        """Return a reference to the current player"""
        return self.players[self.current_turn]

    def get_player_resources(self, player_name: str) -> object:
        """Returns the specified player's resources"""
        pass

    def perform_action(self, action: str, *args) -> None:
        pass

    def check_winner(self) -> Player | None:
        for player in self.players:
            if player.points > 10:
                return player

        return None