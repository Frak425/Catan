import pygame
import math
import random

from classes.node import Node
from classes.tile import Tile



class Board:
    def __init__(self, hex_r_side: int, screen_h, screen_w, num_tiles, screen, game_font, font_size) -> None:

        self.tiles_names = [] #arr len 19 filled with self.types randomly. Assigned in self.assign_tiles
        self.tile_tops = [] #each index is the top point on a hexagon
        self.tiles = []
        self.pieces = [] #list of all pieces on the board

        self.number_indicies = [1, 2, 3, 12, 13, 14, 4, 11, 18, 19, 15, 5, 10, 17, 16, 6, 9, 8, 7]
        self.numbers = ["5", "2", "6", "3", "8", "10", "9", "12", "11", "4", "8", "10", "9", "4", "5", "6", "3", "11"]
        
        self.types = ["sheep", "brick", "rock", "wheat", "wood", "desert"]

        self.radius = hex_r_side # distance from center to a corner
        self.radius_corner = self.radius / math.sqrt(3) # distance from center to the midpoint of a side

        self.init_assets()

        self.screen_h = screen_h
        self.screen_w = screen_w
        self.num_tiles = num_tiles
        self.screen = screen
        self.game_font = game_font
        self.font_size = font_size

    def init_assets(self) -> None:
        road_width = 5
        road_length = 35
        
        city_width = 20
        city_length = 10

        road_points = [(0, 0), (road_width, 0), (road_width, road_length), (0, road_length)]
        city_points = [(0, 0), (city_width / 2, city_length / -2), (city_width, 0), (city_width, city_length), (0, city_length)]

        self.road_red = pygame.Surface((100,100))
        self.road_blue = pygame.Surface((100,100))
        self.road_green = pygame.Surface((100,100))
        self.road_yellow = pygame.Surface((100,100))

        self.city_red = pygame.Surface((100, 100))
        self.city_blue = pygame.Surface((100, 100))
        self.city_green = pygame.Surface((100, 100))
        self.city_yellow = pygame.Surface((100, 100))

        pygame.draw.polygon(self.road_red, (255, 0, 0), road_points)
        pygame.draw.polygon(self.road_blue, (0, 0, 255), road_points)
        pygame.draw.polygon(self.road_green, (0, 255, 0), road_points)
        pygame.draw.polygon(self.road_yellow, (200, 200, 0), road_points)
        
        pygame.draw.polygon(self.city_red, (255, 0, 0), city_points)
        pygame.draw.polygon(self.city_blue, (0, 0, 255), city_points)
        pygame.draw.polygon(self.city_green, (0, 255, 0), city_points)
        pygame.draw.polygon(self.city_yellow, (200, 200, 0), city_points)

    def midpoint(self, point1: tuple[int], point2: tuple[int]) -> tuple:
        return ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)

    def assign_tile_locations(self) -> None:
        lens = [3, 4, 5, 4, 3]
        for i in range(len(lens)):
            for j in range(lens[i]):
                x_offset = (self.screen_w - lens[i] * 2 * self.radius) / 2 + j * self.radius * 2 + self.radius
                y_offset = (self.screen_h - self.radius_corner * 16) / 2  + self.radius_corner * 3 * i
                self.tile_tops.append((x_offset, y_offset))

    def assign_tiles(self) -> None:
        # Create the list with the exact number of each tile type
        self.tiles_names = ['brick'] * 4 + ['wood'] * 4 + ['wheat'] * 4 + ['sheep'] * 3 + ['rock'] * 3 + ['desert'] * 1
        
        # Shuffle the list to ensure randomness
        random.shuffle(self.tiles_names)

    def assign_tile_classes(self) -> None:
        idx = self.tiles_names.index("desert")
        self.numbers.insert(self.number_indicies[idx] - 1, "")
        for i in range(self.num_tiles):

            top = self.tile_tops[i]

            points = [(top[0], top[1]), 
                  (top[0] + self.radius, top[1] + self.radius_corner), 
                  (top[0] + self.radius, top[1] + self.radius_corner * 3), 
                  (top[0], top[1] + self.radius_corner * 4), 
                  (top[0] - self.radius, top[1] + self.radius_corner * 3), 
                  (top[0] - self.radius, top[1] + self.radius_corner)]
            
            city1 = Node("city", points[0])
            city2 = Node("city", points[1])
            city3 = Node("city", points[2])
            city4 = Node("city", points[3])
            city5 = Node("city", points[4])
            city6 = Node("city", points[5])

            print((points[0], points[1]))

            road1 = Node("road", self.midpoint(points[0], points[1]))
            road2 = Node("road", self.midpoint(points[1], points[2]))
            road3 = Node("road", self.midpoint(points[2], points[3]))
            road4 = Node("road", self.midpoint(points[3], points[4]))
            road5 = Node("road", self.midpoint(points[4], points[5]))
            road6 = Node("road", self.midpoint(points[5], points[0]))

            nodes_on_hex = [[city1, city2, city3, city4, city5, city6], [road1, road1, road2, road3, road4, road5, road6]]

            #Find the color of each tile
            if self.tiles_names[i] == "sheep":
                color = (100, 200, 100)
            elif self.tiles_names[i] == "brick":
                color = (200, 100, 50)
            elif self.tiles_names[i] == "rock":
                color = (100, 100, 100)
            elif self.tiles_names[i] == "wheat":
                color = (200, 200, 0)
            elif self.tiles_names[i] == "wood":
                color = (50, 200, 50)
            elif self.tiles_names[i] == "desert":
                color = (100, 100, 0)

            #Find the center of each tile
            center = (top[0], top[1] + self.radius_corner)
            self.tiles.append(Tile(self.tiles_names[i], nodes_on_hex, color, center, self.numbers[self.number_indicies[i] - 1], points, self.screen))

    """def flatten_nodes(self) -> None:
        i = 0
        while i < len(self.nodes) - 1:
            curr = self.nodes[i].location
            next = self.nodes[i + 1].location

            if curr[0] == next[0] and curr[1] == next[1]:
                # Remove the duplicate node
                self.nodes.pop(i + 1)
            else:
                i += 1  # Only increment if no removal, to avoid skipping"""

    def draw_tiles(self) -> None:
        for i in range(len(self.tiles)):

            self.tiles[i].draw_tile()

            center_x = self.tiles[i].center[0]
            center_y = self.tiles[i].center[1]

            if (self.tiles[i].resource_type != "desert"):
                pygame.draw.circle(self.screen, (230, 230, 200), (center_x, center_y + self.radius_corner), 20)

            text_surf = self.game_font.render(self.tiles[i].number, (0, 0), (0, 0, 0))
            self.screen.blit(text_surf, (center_x - self.font_size / 2, center_y + self.font_size / 2))

    #implement rotation and drawing to the screen
    def draw_pieces(self) -> None:
        for i in range(len(self.pieces)):
            if self.pieces[1] == "road":
                if self.pieces[2] == "red":
                    pass
                elif self.pieces[2] == "blue":
                    pass
                elif self.pieces[2] == "yellow":
                    pass
                elif self.pieces[2] == "green":
                    pass
                else:
                    pass
                
            if self.pieces[1] == "city":
                if self.pieces[2] == "red":
                    pass
                elif self.pieces[2] == "blue":
                    pass
                elif self.pieces[2] == "yellow":
                    pass
                elif self.pieces[2] == "green":
                    pass
                else:
                    pass

    def draw_board(self) -> None:
        self.draw_tiles()
        self.draw_pieces()
