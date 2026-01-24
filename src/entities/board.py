import pygame
import math
import random

from src.entities.node import Node
from src.entities.tile import Tile

number_sprite_names = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
number_sprite_pressed_names = ["0_p", "1_p", "2_p", "3_p", "4_p", "5_p", "6_p", "7_p", "8_p", "9_p"]

text_sprite_names = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
text_sprite_pressed_names = ["a_p", "b_p", "c_p", "d_p", "e_p", "f_p", "g_p", "h_p", "i_p", "j_p", "k_p", "l_p", "m_p", "n_p", "o_p", "p_p", "q_p", "r_p", "s_p", "t_p", "u_p", "v_p", "w_p", "x_p", "y_p", "z_p"]

settlement_sprite_names_forward = ["s_red_f", "s_blue_f", "s_white_f", "s_yellow_f", "s_green_f", "s_brown_f"]
settlement_sprite_names_left = ["s_red_l", "s_blue_l", "s_white_l", "s_yellow_l", "s_green_l", "s_brown_l"]
settlement_sprite_names_right = ["s_red_r", "s_blue_r", "s_white_r", "s_yellow_r", "s_green_r", "s_brown_r"]

#city_sprite_names_forward = ["c_red_f", "c_blue_f", "c_white_f", "c_yellow_f", "c_green_f", "c_brown_f"]
#city_sprite_names_left = ["c_red_l", "c_blue_l", "c_white_l", "c_yellow_l", "c_green_l", "c_brown_l"]
#city_sprite_names_right = ["c_red_r", "c_blue_r", "c_white_r", "c_yellow_r", "c_green_r", "c_brown_r"]

#road_sprite_names_forward = ["c_red_f", "c_blue_f", "c_white_f", "c_yellow_f", "c_green_f", "c_brown_f"]
road_sprite_names_left = ["c_red_l", "c_blue_l", "c_white_l", "c_yellow_l", "c_green_l", "c_brown_l"]
#road_sprite_names_right = ["c_red_r", "c_blue_r", "c_white_r", "c_yellow_r", "c_green_r", "c_brown_r"]

sprites = {}

class Board:
    def __init__(self, hex_r_side, screen_h, screen_w, num_tiles, screen, game_font, font_size) -> None:

        self.tiles_names = [] #arr len 19 filled with self.types randomly. Assigned in self.assign_tiles
        self.tile_tops = [] #each index is the top point on a hexagon
        self.tiles = []
        self.pieces = [] #list of all pieces on the board
        self.city_settlemet_indicator_locations = [] #list of all city placement indicators on the board
        self.road_indicator_locations = []

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

        number_sxs = 5
        text_sxs = 13
        other_sxs = 29
        total_sxs = number_sxs + text_sxs + other_sxs

        sprite_sheet = pygame.image.load('src/assets/New Piskel (6).png')
        top_left_offset_x, top_left_offset_y = (3, 3)
        sprite_sheet_w, sprite_sheet_h = sprite_sheet.get_size()
        section_size = 64
        #sprite_sheet_rows = top_left_offset_x % section_size
        #sprite_sheet_cols = top_left_offset_y % section_size
        assignment_mode = "number"
        row_counter = 1

        change_mode_at_idx = [5, 18, 26, 31, 36] #needs to change as sprite sheets change
        for sxs_idx in range(total_sxs):
            item_counter = sxs_idx % (sprite_sheet_w / 64) #currently goes up to 7. last row (row 3) should stop at 6

            temp_surface = pygame.Surface((64, 64))
            x = section_size * (item_counter - 1)
            y = section_size * (row_counter - 1)
            w = section_size
            h = section_size
            temp_surface.blit(sprite_sheet, (0, 0), [x, y, w, h])

            half_surface_length = section_size / 2
            subsurface_length = half_surface_length - top_left_offset_x * 2
            subsurface_width = half_surface_length - top_left_offset_y * 2

            if assignment_mode == "number":
                temp_surface_top_left = pygame.Surface((subsurface_length, subsurface_width))
                temp_surface_top_left.blit(temp_surface, (0, 0), [top_left_offset_x, top_left_offset_y, subsurface_length, subsurface_width])

                temp_surface_top_right = pygame.Surface((subsurface_length, subsurface_width))
                temp_surface_top_right.blit(temp_surface, (0, 0), [top_left_offset_x + half_surface_length, top_left_offset_y, subsurface_length, subsurface_width])

                temp_surface_bottom_left = pygame.Surface((subsurface_length, subsurface_width))
                temp_surface_bottom_left.blit(temp_surface, (0, 0), [top_left_offset_x, top_left_offset_y, subsurface_length, subsurface_width])

                temp_surface_bottom_right = pygame.Surface((subsurface_length, subsurface_width))
                temp_surface_bottom_right.blit(temp_surface, (0, 0), [top_left_offset_x + half_surface_length, top_left_offset_y + half_surface_length, subsurface_length, subsurface_width])

                sprites[number_sprite_names[sxs_idx]] = temp_surface_top_left
                sprites[number_sprite_names[sxs_idx + 1]] = temp_surface_bottom_left
                sprites[number_sprite_pressed_names[sxs_idx]] = temp_surface_top_right
                sprites[number_sprite_pressed_names[sxs_idx + 1]] = temp_surface_bottom_right
            elif assignment_mode == "text":
                temp_surface_top_left = pygame.Surface((subsurface_length, subsurface_width))
                temp_surface_top_left.blit(temp_surface, (0, 0), [top_left_offset_x, top_left_offset_y, subsurface_length, subsurface_width])

                temp_surface_top_right = pygame.Surface((subsurface_length, subsurface_width))
                temp_surface_top_right.blit(temp_surface, (0, 0), [top_left_offset_x + half_surface_length, top_left_offset_y, subsurface_length, subsurface_width])

                temp_surface_bottom_left = pygame.Surface((subsurface_length, subsurface_width))
                temp_surface_bottom_left.blit(temp_surface, (0, 0), [top_left_offset_x, top_left_offset_y, subsurface_length, subsurface_width])

                temp_surface_bottom_right = pygame.Surface((subsurface_length, subsurface_width))
                temp_surface_bottom_right.blit(temp_surface, (0, 0), [top_left_offset_x + half_surface_length, top_left_offset_y + half_surface_length, subsurface_length, subsurface_width])

                sxs_idx_offset = change_mode_at_idx[0]
                sprites[text_sprite_names[sxs_idx - sxs_idx_offset - 1]] = temp_surface_top_left
                sprites[text_sprite_names[sxs_idx - sxs_idx_offset]] = temp_surface_bottom_left
                sprites[text_sprite_pressed_names[sxs_idx - sxs_idx_offset - 1]] = temp_surface_top_right
                sprites[text_sprite_pressed_names[sxs_idx - sxs_idx_offset]] = temp_surface_bottom_right

            elif assignment_mode == "settlement_forward":
                return
                sxs_idx_offset = change_mode_at_idx[1]
                sprites[settlement_sprite_names_forward[sxs_idx - sxs_idx_offset]]

            elif assignment_mode == "settlement_forward":
                sxs_idx_offset = change_mode_at_idx[2]
                sprites[settlement_sprite_names_left[sxs_idx - sxs_idx_offset]]

            elif assignment_mode == "settlement_right":
                sxs_idx_offset = change_mode_at_idx[3]
                sprites[settlement_sprite_names_right[sxs_idx - sxs_idx_offset]]

                """
                elif assignment_mode == "city_forward":
                    sxs_idx_offset = change_mode_at_idx[4]
                    sprites[city_sprite_names_forward[sxs_idx - sxs_idx_offset]]

                elif assignment_mode == "city_left":
                    sxs_idx_offset = change_mode_at_idx[5]
                    sprites[city_sprite_names_left[sxs_idx - sxs_idx_offset]]

                elif assignment_mode == "city_right":
                    sxs_idx_offset = change_mode_at_idx[6]
                    sprites[city_sprite_names_right[sxs_idx - sxs_idx_offset]]"""
                """elif assignment_mode == "road_forward":
                sxs_idx_offset = change_mode_at_idx[7]
                sprites[road_sprite_names_forward[sxs_idx - sxs_idx_offset]]
"""
            
            elif assignment_mode == "road_left":
                sxs_idx_offset = change_mode_at_idx[4]
                sprites[road_sprite_names_left[sxs_idx - sxs_idx_offset]]
                """
            elif assignment_mode == "road_right":
                sxs_idx_offset = change_mode_at_idx[9]
                sprites[road_sprite_names_right[sxs_idx - sxs_idx_offset]]"""
            #Chage logic in future to add
            if sxs_idx == change_mode_at_idx[0]: #after the 6th 64x64, the sprite sheet reads letters. Doesn't matter if repeated bc the counter doesn't return to this number
                assignment_mode = "text"
            elif sxs_idx == change_mode_at_idx[1]:
                assignment_mode = "settlement_forward"
            elif sxs_idx == change_mode_at_idx[2]:
                assignment_mode = "settlement_forward"
            elif sxs_idx == change_mode_at_idx[3]:
                assignment_mode = "settlement_right"

    def midpoint(self, point1: tuple[int, int], point2: tuple[int, int]) -> tuple:
        return ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)

    def assign_tile_locations(self) -> None:
        row_lengths = [3, 4, 5, 4, 3]
        for i in range(len(row_lengths)):
            for j in range(row_lengths[i]):
                x_offset = (self.screen_w - row_lengths[i] * 2 * self.radius) / 2 + j * self.radius * 2 + self.radius
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
            
            for point in points:
                if not point in self.city_settlemet_indicator_locations:
                    self.city_settlemet_indicator_locations.append(point)

            for j in range(len(points)):
                mid = self.midpoint(points[j], points[(j + 1) % len(points)])
                if not mid in self.road_indicator_locations:
                    self.road_indicator_locations.append(mid)

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
            self.tiles.append(Tile(self.tiles_names[i], color, center, self.numbers[self.number_indicies[i] - 1], points, self.screen))

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
