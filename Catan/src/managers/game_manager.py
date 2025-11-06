import json
from pathlib import Path
import pygame
from pygame import *

from src.entities.player import Player
from src.entities.board import Board
from src.ui.menu import Menu

class GameManager:
    def __init__(self, screen: Surface) -> None:
        #TODO: Refactor this to use config files properly
        self.running = True
        self.LAYOUT_CONFIG_FILE = Path("layout.json")
        self.SETTINGS_CONFIG_FILE = Path("settings.json")
        self.screen = screen
        self.screen_size = (self.screen.get_width(), self.screen.get_height())
        self.screen_w = self.screen_size[0]
        self.screen_h = self.screen_size[1]
        self.font_size = 20
        self.game_font = pygame.font.SysFont('Comic Sans', self.font_size)
        self.game_state = "main_menu" # main menu -> game setup -> init -> game ongoing -> game over -> main menu
        self.player_state = "roll" # roll -> trade -> buy -> place
        self.settings_open = False
        self.players_num = 2
        self.players_list = []
        self.players_list_index = 0
        self.player_colors = ["yellow", "blue", "green", "red"]
        self.player_color_chosen_index = 0
        self.game_difficulty = "easy"
        self.framerates = [30, 60, 120, 240]
        self.framerate_index = 1
        self.num_tiles = 19
        self.points_to_win = 10
        self.game_difficulty = "easy"
        self.menu_margins = (50, 50) #top, bottom
        self.menu_size = (self.screen_w - 2 * self.menu_margins[0], self.screen_h - 2 * self.menu_margins[1])
        self.init_location = (self.screen_w + self.menu_margins[0], self.menu_margins[1]) #of top left corner
        self.final_location = self.menu_margins #of top left corner
        self.menu_background_color = (100, 100, 100)
        self.play_button_width = 200
        self.play_button_height = 75
        self.game_start_button_width = 150
        self.game_start_button_height = 50
        self.player_number_incease_decrease_button_size = self.screen_h / 20
        self.settings_open_button_size = self.screen_w / 12 / 1.5
        self.settings_open_button_offset = self.screen_h / 24 / 1.5
        self.menu_tab_margin_top = 20
        self.close_menu_margins = (50, 50)
        self.close_menu_size = (100, 50)
        self.menu_input_tab_size = (60, 35)
        self.menu_accessibility_tab_size = (130, 35)
        self.menu_gameplay_tab_size = (95, 35)
        self.menu_audio_tab_size = (65, 35)
        self.menu_graphics_tab_size = (90, 35)
        
        self.buy_selection_backdrop_offset = (self.screen_w / 8 * 5, self.screen_h / 8 * 7)
        self.buy_selection_offset = (50, 50)
        self.board = self.init_board()

    def init_board(self) -> Board:
        for i in range(self.players_num):
            self.players_list.append(Player(self.player_colors, self.points_to_win))

        global board
        board = Board(self.screen_w / 27.32, self.screen_h, self.screen_w, self.num_tiles, self.screen, self.game_font, self.font_size)
        board.assign_tile_locations()
        board.assign_tiles()
        board.assign_tile_classes()
        return board

    def init_configs(self):
        self.layout = self.create_layout_defaults()
        self.settings = self.create_settings_defaults()
        self.save_config(self.layout, "layout")
        self.save_config(self.settings, "settings")

    def create_settings_defaults(self) -> dict:
        if (self.settings != {}):
            return
        
        #create settings default values
        return {}

    def create_layout_defaults(self) -> dict:
        if (self.layout != {}):
            return
        
        #create layout default values
        return {}

    def load_config(self, file: str) -> None:
        CONFIG_FILE = self.get_config_file(file)
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)  # Ensure directories exist

        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
        else:
            # File does not exist — create it with an empty dict or default config
            data = {}
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=4)

        # Assign loaded data to the correct attribute
        self.set_config_file(file, data)

    
    def save_config(self, config: dict, file: str) -> None:
        CONFIG_FILE = self.get_config_file(file)

        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

    def get_config_file(self, file: str) -> Path:
        if file == "layout":
            CONFIG_FILE = self.LAYOUT_CONFIG_FILE
        elif file == "settings":
            CONFIG_FILE = self.SETTINGS_CONFIG_FILE

        return CONFIG_FILE
    
    def set_config_file(self, file: str, value: dict) -> Path:
        if file == "layout":
            CONFIG_FILE = self.LAYOUT_CONFIG_FILE
        elif file == "settings":
            CONFIG_FILE = self.SETTINGS_CONFIG_FILE

        CONFIG_FILE = value