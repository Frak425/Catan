import math

import pygame
import numpy as np
from typing import TYPE_CHECKING
from src.managers.base_manager import BaseManager
from src.managers.graphics.board.tile import Tile
from src.managers.graphics.board.edge import Edge
from src.managers.graphics.board.vertex import Vertex

if TYPE_CHECKING:
    from src.managers.game.game_manager import GameManager
    from src.managers.input.input_manager import InputManager
    from src.managers.helper.helper_manager import HelperManager
    from src.managers.player.player_manager import PlayerManager
    from src.managers.audio.audio_manager import AudioManager

class GraphicsManager(BaseManager):
    def __init__(self):
        super().__init__()
        self.board_global_edges: list[Edge] = []
        self.board_global_verts: list[Vertex] = []
        self.board_global_tiles: list[Tile] = []
        self.directions = [(+1, -1, 0),
              (+1, 0, -1),
              (0, +1, -1),
              (-1, +1, 0),
              (-1, 0, +1),
              (0, -1, +1)]
       
    def import_dependencies(self) -> None:
        """Initialize manager after all dependencies are injected."""
        self.game_manager: 'GameManager' = self.get_dependency('game_manager')
        self.helper_manager: 'HelperManager' = self.get_dependency('helper_manager')
        self.input_manager: 'InputManager' = self.get_dependency('input_manager')
        self.player_manager: 'PlayerManager' = self.get_dependency('player_manager')
        self.audio_manager: 'AudioManager' = self.get_dependency('audio_manager')
        
    def init(self, time):
        self.menu_open = False
        self.time = time

        self.create_board()

        self.home_ui_draw_funcs = [lambda: self.draw_ui("images", "home"), lambda: self.draw_ui("text_displays", "home"), lambda: self.draw_ui("buttons", "home"), lambda: self.draw_ui("sliders", "home"), lambda: self.draw_ui("toggles", "home"), lambda: self.draw_ui("scrollable_areas", "home")]
        self.setup_ui_draw_funcs = [lambda: self.draw_ui("images", "setup"), lambda: self.draw_ui("text_displays", "setup"), lambda: self.draw_ui("buttons", "setup"), lambda: self.draw_ui("sliders", "setup"), lambda: self.draw_ui("toggles", "setup"), lambda: self.draw_ui("scrollable_areas", "setup")]
        self.game_ui_draw_funcs = [lambda: self.draw_ui("tiles", "game"), lambda: self.draw_ui("images", "game"), lambda: self.draw_ui("text_displays", "game"), lambda: self.draw_ui("buttons", "game"), lambda: self.draw_ui("sliders", "game"), lambda: self.draw_ui("toggles", "game"), lambda: self.draw_ui("scrollable_areas", "game"), lambda: self.draw_board()]

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
            for func in self.game_ui_draw_funcs:
                func()

        elif (self.game_manager.game_state == "game"):
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
            self.input_manager.menus[self.game_manager.game_state].values(),
            key=lambda m: m.z_index,
            reverse=True
        )
        for menu in sorted_menus:
            # Menu.draw() checks menu.shown internally, so closed menus won't draw
            menu.draw(self.game_manager.screen, self.time)

    def draw_ui(self, type: str, layer: str):
        for element_name, element in self.input_manager.ui_by_type[type][layer].items():
            element.draw(self.game_manager.screen, self.time)

    def draw_board(self):
        for tile in self.board_global_tiles:
            polygon_points = [tile._vertex_position(i) for i in range(6)]
            pygame.draw.polygon(self.game_manager.screen, (50, 50, 50), polygon_points)
            pygame.draw.polygon(self.game_manager.screen, (110, 110, 110), polygon_points, 1)

            for i in range(6):
                edge_start = tile._vertex_position(i)
                edge_end = tile._vertex_position((i + 1) % 6)
                pygame.draw.aaline(self.game_manager.screen, (80, 80, 80), edge_start, edge_end)

        for edge in self.board_global_edges:
            pygame.draw.circle(self.game_manager.screen, (0, 255, 120), (int(edge.center[0]), int(edge.center[1])), 4)

        for vertex in self.board_global_verts:
            pygame.draw.circle(self.game_manager.screen, (0, 120, 255), (int(vertex.center[0]), int(vertex.center[1])), 5)

# --- BOARD CREATION --- #

    def create_board(self):
        self.board_center = self.game_manager.screen.get_rect().center

        #TODO: find place for this var
        self.board_tile_radius = 50

        seed_tile = Tile(0, self.board_center, self.board_tile_radius, 0, "test", 0, 0, 0)
        self.board_global_tiles.append(seed_tile)
    
    
        seed_tile.create_verts(self.board_global_verts)
        seed_tile.create_edges(self.board_global_edges)
    
        self._create_ring_tiles(seed_tile)
        
        #second ring
        first_ring: list[Tile] = self.board_global_tiles[1:7]
        for tile in first_ring:
            self._create_ring_tiles(tile)
    
    
        #populate edge, vertex, and tile neighbors after all initialized
        for tile in self.board_global_tiles:
            tile.populate_edge_to_edge_neighbors()
            tile.populate_vert_to_vert_neighbors()
            tile.populate_edge_to_vert_neighbors()
            tile.populate_vert_to_edge_neighbors()
            tile.populate_edge_to_tile_neighbors()
            tile.populate_vert_to_tile_neighbors()

    def _create_tiles(self, center_tile: Tile):
        #first ring

        self._create_ring_tiles(center_tile)

        #second ring
        first_ring: list[Tile] = self.board_global_tiles[1:7]
        for tile in first_ring:
            self._create_ring_tiles(tile)


        #populate edge, vertex, and tile neighbors after all initialized
        for tile in self.board_global_tiles:
            tile.populate_edge_to_edge_neighbors()
            tile.populate_vert_to_vert_neighbors()
            tile.populate_edge_to_vert_neighbors()
            tile.populate_vert_to_edge_neighbors()
            tile.populate_edge_to_tile_neighbors()
            tile.populate_vert_to_tile_neighbors()
            
    def _create_ring_tiles(self, center_tile: Tile):
        for direction in self.directions:
            #if tile already exists
            for tile in self.board_global_tiles:
                if (direction[0] + center_tile.p, direction[1] + center_tile.q, direction[2] + center_tile.s) == (tile.p, tile.q, tile.s):
                    break
            else: # else create new tile in that direction
                new_p = center_tile.p + direction[0]
                new_q = center_tile.q + direction[1]
                new_s = center_tile.s + direction[2]

                new_center_x = self.board_center[0] + self.board_tile_radius * math.sqrt(3) * (new_p + new_s / 2)
                new_center_y = self.board_center[1] + self.board_tile_radius * 3 / 2 * new_s

                new_tile = Tile(len(self.board_global_tiles), (new_center_x, new_center_y), self.board_tile_radius, len(self.board_global_tiles), "test", new_p, new_q, new_s)
                
                self.board_global_tiles.append(new_tile)
                new_tile.create_verts(self.board_global_verts)
                new_tile.create_edges(self.board_global_edges)