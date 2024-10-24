import pygame
import math
import random

class Player:
    def __init__(self, player_color) -> None:
        self.player_color = player_color
        self.cards = []
        self.development = []
        self.points = 0
        self.cities = 5
        self.settlements = 5
        self.roads = 15
        self.has_longest_road = False
        self.has_biggest_army = False

    def calculate_points(self) -> None:
        pass

    def check_winner(self) -> None:
        pass

    def place_piece(self, type: str, board, location) -> None:
        board.pieces.append([location, self.player_color, type])

    def return_resource_values(self) -> object:
        resources = {
            "sheep": 0,
            "brick": 0, 
            "stone": 0,
            "wheat": 0,
            "wood": 0
        }

        for i in range(len(self.cards)):
            resources[self.cards[i]] += 1

        return resources

    def buy(self, item) -> bool:
        resources = self.return_resource_values()
        if item == "city":
            if resources["stone"] >= 3 and resources["wheat"] >= 2:
                for i in range(3):
                    self.cards.remove("stone")
                for i in range(2):
                    self.cards.remove("wheat")
                return True
        elif item == "settlement":
            if resources["sheep"] >= 1 and resources["wheat"] >= 1 and resources["brick"] >= 1 and resources["wood"] >= 1:
                self.cards.remove("wheat")
                self.cards.remove("sheep")
                self.cards.remove("brick")
                self.cards.remove("wood")
                return True
        elif item == "road":
            if resources["brick"] >= 1 and resources["wood"] >= 1:
                self.cards.remove("brick")
                self.cards.remove("wood")
                return True
        elif item == "dev":
            if resources["sheep"] >= 1 and resources["wheat"] >= 1 and resources["stone"] >= 1:
                self.cards.remove("sheep")
                self.cards.remove("wheat")
                self.cards.remove("stone")
                return True
        else:
            return False
