import json
from pathlib import Path
import pygame

from src.ui.button import Button
from src.ui.image import Image
from src.ui.slider import Slider
from src.ui.text_display import TextDisplay
from src.ui.toggle import Toggle
from src.entities.player import Player
from src.entities.board import Board
from src.ui.menu import Menu
from src.managers.input.input_manager import InputManager
from src.managers.helper_manager import HelperManager
from src.managers.graphics_manager import GraphicsManager
from src.managers.player_manager import PlayerManager
from src.managers.audio_manager import AudioManager

class GameManager:
    def init(self, screen: pygame.Surface) -> None:
        #TODO: Refactor this to use config files properly
        self.running = True
        self.edited = False  #whether to use edited settings or layout
        self.LAYOUT_CONFIG_PATH = Path("Catan/src/config/layout.json")
        self.SETTINGS_CONFIG_PATH = Path("Catan/src/config/settings.json")
        self.LAYOUT_STATE_CONFIG_PATH = Path("Catan/src/config/layout_state.json")
        self.SETTINGS_STATE_CONFIG_PATH = Path("Catan/src/config/settings_state.json")
        self.screen = screen
        self.screen_size = (self.screen.get_width(), self.screen.get_height())
        self.screen_w = self.screen_size[0]
        self.screen_h = self.screen_size[1]
        self.font_size = 20
        self.game_font = pygame.font.SysFont('Comic Sans', self.font_size)
        self.game_state = "home" # main menu -> game setup -> init -> game ongoing -> game over -> main menu
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

        self.dev_mode = False
        self.dev_mode_typing = False
        self.dev_mode_text = ""

    def init_board(self) -> Board:
        for i in range(self.players_num):
            self.players_list.append(Player(self.player_colors, self.points_to_win))

        global board
        board = Board(self.screen_w / 27.32, self.screen_h, self.screen_w, self.num_tiles, self.screen, self.game_font, self.font_size)
        board.assign_tile_locations()
        board.assign_tiles()
        board.assign_tile_classes()
        return board

    def set_input_manager(self, input_manager: InputManager):
        self.input_manager = input_manager
        self.load_config("layout", False)
        #self.get_layout()

    def set_audio_manager(self, audio_manager: AudioManager):
        self.audio_manager = audio_manager

    def set_graphics_manager(self, graphics_manager: GraphicsManager):
        self.graphics_manager = graphics_manager

    def set_helper_manager(self, helper_manager: HelperManager):
        self.helper_manager = helper_manager

    def set_player_manager(self, player_manager: PlayerManager):
        self.player_manager = player_manager

    #initialize default settings
    def get_layout(self) -> dict:

        layout = {
            "home": {
                "images": [],
                "sliders": [],
                "toggles": [],
                "text_displays": [],
                "text_inputs": [],
                "multi_selects": []
            },
            "setup": {
                "buttons": [],
                "images": [],
                "sliders": [],
                "toggles": [],
                "text_displays": [],
                "text_inputs": [],
                "multi_selects": []
            },
            "game": {
                "buttons": [],
                "images": [],
                "sliders": [],
                "toggles": [],
                "text_displays": [],
                "text_inputs": [],
                "multi_selects": []
            },
            "menu": {
                "buttons": [],
                "images": [],
                "sliders": [],
                "toggles": [],
                "text_displays": [],
                "text_inputs": [],
                "multi_selects": []
            }
        }

        layout["home"] = self.save_layout_by_section("home")
        layout["setup"] = self.save_layout_by_section("setup")
        layout["game"] = self.save_layout_by_section("game")
        layout["menu"] = self.save_layout_by_section("menu")

        return layout

    def get_settings(self) -> dict:
        settings_defaults = {
            "audio": {},
            "graphics": {},
            "gameplay": {},
            "accessibility": {},
            "input": {}
        }

        return settings_defaults
            
    def save_layout_by_section(self, section: str) -> dict:
        section_defaults = {
            "buttons": [],
            "images": [],
            "sliders": [],
            "toggles": [],
            "text_displays": [],
            "text_inputs": [],
            "multi_selects": []
        }

        #create defaults for each section here
        if section == "menu":
            menu = {
                "input": section_defaults,
                "accessibility": section_defaults,
                "gameplay": section_defaults,
                "audio": section_defaults,
                "graphics": section_defaults
            }

            for tab_name in self.input_manager.menu.tabs:
                buttons = self.input_manager.buttons["menu"][tab_name]
                menu[tab_name]["buttons"] = self.convert_buttons_to_list(buttons)

                sliders = self.input_manager.sliders["menu"][tab_name]
                menu[tab_name]["sliders"] = self.convert_sliders_to_list(sliders)

                toggles = self.input_manager.toggles["menu"][tab_name]
                menu[tab_name]["toggles"] = self.convert_toggles_to_list(toggles)

                text_displays = self.input_manager.text_displays["menu"][tab_name]
                menu[tab_name]["text_displays"] = self.convert_text_displays_to_list(text_displays)
                
                #TODO: implement these
                #text_inputs = self.input_manager.text_inputs["menu"][tab_name]
                #menu[tab_name]["text_inputs"] = self.convert_text_inputs_to_list(text_inputs)

                #multi_selects = self.input_manager.multi_selects["menu"][tab_name]
                #menu[tab_name]["multi_selects"] = self.convert_multi_selects_to_list(multi_selects)
            return menu
            
        else:
            buttons = self.input_manager.buttons[section]
            section_defaults["buttons"] = self.convert_buttons_to_list(buttons)

            sliders = self.input_manager.sliders[section]
            section_defaults["sliders"] = self.convert_sliders_to_list(sliders)

            toggles = self.input_manager.toggles[section]
            section_defaults["toggles"] = self.convert_toggles_to_list(toggles)

            text_displays = self.input_manager.text_displays[section]
            section_defaults["text_displays"] = self.convert_text_displays_to_list(text_displays)

            #TODO: implement these
            #text_inputs = self.input_manager.text_inputs[section]
            #section_defaults["text_inputs"] = self.convert_text_inputs_to_list(text_inputs)

            #multi_selects = self.input_manager.multi_selects[section]
            #section_defaults["multi_selects"] = self.convert_multi_selects_to_list(multi_selects)

            return section_defaults

    ## --- CONVERT OBJECTS TO --- ##

    def convert_buttons_to_list(self, buttons: dict[str, Button]) -> list:
        layout_object_list = []
        for button_name, button in buttons.items():
            layout_object = {
                "name": button.name,
                "rect": [button.rect[0], button.rect[1], button.rect[2], button.rect[3]],
                "color": [button.color[0], button.color[1], button.color[2]],
                "text": button.text
            }
            layout_object_list.append(layout_object)
        return layout_object_list

    def convert_images_to_list(self, images: dict[str, Image]) -> list:
        layout_object_list = []
        for image_name, image in images.items():
            layout_object = {
                "name": image.name,
                "rect": [image.rect[0], image.rect[1], image.rect[2], image.rect[3]],
                "file_path": image.image_path,
            }
            layout_object_list.append(layout_object)
        return layout_object_list

    def convert_sliders_to_list(self, sliders: dict[str, Slider]) -> list:
        layout_object_list = []
        for slider_name, slider in sliders.items():
            layout_object = {
                "name": slider.name,
                "rect": [slider.rect[0], slider.rect[1], slider.rect[2], slider.rect[3]],
                "wrapper_rect": [slider.wrapper_rect[0], slider.wrapper_rect[1], slider.wrapper_rect[2], slider.wrapper_rect[3]],
                "min_value": slider.min_value,
                "max_value": slider.max_value,
                "bar_color": [slider.bar_color[0], slider.bar_color[1], slider.bar_color[2]],
                "handle_color": [slider.handle_color[0], slider.handle_color[1], slider.handle_color[2]],
                "handle_radius": slider.handle_radius
            }
            layout_object_list.append(layout_object)
        return layout_object_list

    def convert_toggles_to_list(self, toggles: dict[str, Toggle]) -> list:
        layout_object_list = []
        for toggle_name, toggle in toggles.items():
            layout_object = {
                "name": toggle.name,
                "rect": [toggle.rect[0], toggle.rect[1], toggle.rect[2], toggle.rect[3]],
                "guiding_lines": toggle.guiding_lines,
                "height": toggle.height,
                "center_width": toggle.center_width,
                "fill_color": [toggle.fill_color[0], toggle.fill_color[1], toggle.fill_color[2]],
                "toggle_color": [toggle.toggle_color[0], toggle.toggle_color[1], toggle.toggle_color[2]],
                "toggle_gap": toggle.toggle_gap,
                "time_to_flip": toggle.time_to_flip
            }
            layout_object_list.append(layout_object)
        return layout_object_list

    def convert_text_displays_to_list(self, text_displays: dict[str, TextDisplay]) -> list:
        layout_object_list = []
        for text_display_name, text_display in text_displays.items():
            layout_object = {
                "name": text_display.name,
                "rect": [text_display.rect[0], text_display.rect[1], text_display.rect[2], text_display.rect[3]],
                "color": [text_display.background_color[0], text_display.background_color[1], text_display.background_color[2]],
                "text": text_display.text,
                "text_color": [text_display.text_color[0], text_display.text_color[1], text_display.text_color[2]],
                "padding": text_display.padding
            }
            layout_object_list.append(layout_object)
        return layout_object_list

    def convert_text_inputs_to_list(self, text_inputs: list) -> list:
        return []

    def convert_multi_selects_to_list(self, multi_selects: list) -> list:
        return []

    ## --- SET/GET CONFIG FROM FILES --- ##

    #loag config from file into game manager
    def load_config(self, file: str, overriding: bool) -> None:
        CONFIG_PATH = self.config_path_by_name(file, overriding)
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)  # Ensure directories exist

        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
        else:
            # File does not exist — create it with an empty dict or default config
            data = self.get_layout() if file == "layout" else self.get_settings()
            with open(CONFIG_PATH, "w") as f:
                json.dump(data, f, indent=4)

        # Assign loaded data to the correct attribute
        if file == "layout":
            self.layout = data
        elif file == "settings":
            self.settings = data

    #save settings from game manager into file
    def save_config(self, file: str, overriding: bool) -> None:
        CONFIG_PATH = self.config_path_by_name(file, overriding)

        with open(CONFIG_PATH, "w") as f:
            json.dump(self.reload_config(CONFIG_PATH), f, indent=4)

    #return config as object
    def config_path_by_name(self, file: str, overriding: bool) -> Path:
        if file == "layout":
            CONFIG_PATH = self.LAYOUT_STATE_CONFIG_PATH
            if overriding:
                CONFIG_PATH = self.LAYOUT_CONFIG_PATH
        elif file == "settings":
            CONFIG_PATH = self.SETTINGS_STATE_CONFIG_PATH
            if overriding:
                CONFIG_PATH = self.SETTINGS_CONFIG_PATH

        return CONFIG_PATH
    
    def ref_by_name(self, file: str):
        if file == "layout":
            return self.layout
        elif file == "settings":
            return self.settings

    #get config data based on path. could be better but for now it works
    def reload_config(self, path: Path) -> dict:
        if path == self.LAYOUT_STATE_CONFIG_PATH:
            return self.get_layout()
        elif path == self.SETTINGS_STATE_CONFIG_PATH:
            return self.get_settings()
        elif path == self.LAYOUT_CONFIG_PATH:
            return self.get_layout()
        elif path == self.SETTINGS_CONFIG_PATH:
            return self.get_settings()
        
        return {}
    
    #loads default config file into game manager
    def restore_config(self, file: str) -> None:
        self.load_config(file, True)

        self.input_manager.reset_ui()