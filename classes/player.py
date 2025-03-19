import pygame
import math
import random

class Player:
    def __init__(self, colors, points_to_win) -> None:
        self.player_color = colors[random.randint(0, len(colors) - 1)] #color of the player's pieces
        self.resources = {
            "sheep": 0,
            "brick": 0, 
            "stone": 0,
            "wheat": 0,
            "wood": 0
        }
        #TO-DO: Figure out all development card in catan. Treat this structure similarly to resources, as these are also cards in the ral game
        self.development = {}
        self.points_to_win = points_to_win
        self.points = 0 #in base: 10, in kights and cities: 13
        self.cities = 5
        self.settlements = 5
        self.roads = 15
        self.has_longest_road = False
        self.has_biggest_army = False
        self.longest_road_length = 1
        self.army_size = 0

    #TO-DO: Find a way to check current points
    def update_points(self) -> None:
        pass

    def check_winner(self) -> None:
        if self.points >= self.points_to_win:
            return True

    def place_piece(self, type: str, board, location) -> None:
        board.pieces.append([location, self.player_color, type])

    def reset_resources(self):
        self.resources = {
            "sheep": 0,
            "brick": 0, 
            "stone": 0,
            "wheat": 0,
            "wood": 0
        }

    def change_resources(self, operation: str, items: list[str], number: int) -> None:
        mult = -1 if operation == "subtract" else 1
        for item in items:
            if (self.resources[item]):
                self.resources[item] = max(0, self.resources[item] + number * mult)

    def check_buy(self, item) -> bool:
        if item == "city":
            if self.resources["stone"] >= 3 and self.resources["wheat"] >= 2:
                return True
        elif item == "settlement":
            if self.resources["sheep"] >= 1 and self.resources["wheat"] >= 1 and self.resources["brick"] >= 1 and self.resources["wood"] >= 1:
                return True
        elif item == "road":
            if self.resources["brick"] >= 1 and self.resources["wood"] >= 1:
                return True
        elif item == "dev":
            if self.resources["sheep"] >= 1 and self.resources["wheat"] >= 1 and self.resources["stone"] >= 1:
                return True
        else:
            return False

    def buy(self, item) -> bool:
        if item == "city":
            self.change_resources("subtract", ["stone", "wheat"], 3)
            self.cities -= 1
        elif item == "settlement":
            self.change_resources("subtract", ["wheat", "sheep", "brick", "wood"], 1)
            self.settlements -= 1
        elif item == "road":
            self.change_resources("subtract", ["brick", "wood"], 1)
            self.roads -= 1
        elif item == "dev":
            self.change_resources("subtract", ["sheep", "wheat", "stone"], 1)
        else:
            print("Error: Incorrect name input when buying")

    def check_longest_road(self, list_other_max_lengths: list[int]) -> None:
        max_length = self.return_longest_road()
        longest = True
        for other in list_other_max_lengths:
            if other > max_length:
                longest = False

        if longest and max_length > 5:
            self.has_longest_road = True

    def check_longest_army(self, list_other_armies: list[int]) -> None:
        size = self.army_size
        largest = True
        for other in list_other_armies:
            if other > size:
                largest = False

        if largest and size >= 3:
            self.has_biggest_army = True
        

    #TO-DO: Find a way to calculate longest adjacent path of roads on the board for any given player
    def update_longest_road(self) -> int:
        pass
