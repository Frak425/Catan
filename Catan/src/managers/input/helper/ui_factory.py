import pygame
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from game_manager import GameManager
    from input_manager import InputManager

from src.ui.button import Button
from src.ui.slider import Slider
from src.ui.toggle import Toggle
from src.ui.image import Image
from src.ui.text_display import TextDisplay
from src.ui.menu import Menu


class UIFactory:
    """Factory class for creating all UI elements (buttons, sliders, toggles, etc.)."""
    
    def __init__(self, game_manager: 'GameManager', input_manager: 'InputManager'):
        self.game_manager = game_manager
        self.input_manager = input_manager

    def _get_from_layout(self, element_type: str, state: str, name: str, tab: str | None = None):
        """Helper to retrieve element from layout or return None."""
        layout = getattr(self.game_manager, 'layout', None)
        if not layout:
            return None
        try:
            if state == 'menu' and tab:
                elements = layout[state][tab].get(element_type, [])
            else:
                elements = layout[state].get(element_type, [])
            return next((e for e in elements if e.get('name') == name), None)
        except Exception:
            return None

    # --- BUTTON CREATION --- #

    def create_all_buttons(self, callbacks) -> Dict[str, Dict]:
        """Create all buttons for all game states."""
        return {
            "home": self.create_title_buttons(callbacks),
            "setup": self.create_setup_buttons(callbacks),
            "game": self.create_game_buttons(callbacks),
            "menu": self.create_menu_buttons(callbacks)
        }

    def create_title_buttons(self, callbacks) -> Dict[str, Button]:
        """Create title screen buttons."""
        props_play = self._get_from_layout('buttons', "home", "play") or {
            "name": "play",
            "rect": [
                self.game_manager.screen_w / 2 - self.game_manager.play_button_width / 2,
                self.game_manager.screen_h / 2 - self.game_manager.play_button_height / 1.75,
                self.game_manager.play_button_width,
                self.game_manager.play_button_height
            ],
            "color": [0, 100, 0],
            "text": "PLAY",
            
        }
        props_quit = self._get_from_layout('buttons', "home", "quit") or {
            "name": "quit",
            "rect": [
                self.game_manager.screen_w / 2 - self.game_manager.play_button_width / 2,
                self.game_manager.screen_h / 2 + self.game_manager.play_button_height / 1.75,
                self.game_manager.play_button_width,
                self.game_manager.play_button_height
            ],
            "color": [100, 0, 0],
            "text": "QUIT",
            
        }

        play_button = Button(
            props_play,
            
            self.game_manager.game_font,
            self.game_manager,
            callback=callbacks['set_game_state_setup']
        )
        quit_button = Button(
            props_quit,
            
            self.game_manager.game_font,
            self.game_manager,
            callback=callbacks['quit']
        )
        return {
            "play_button": play_button,
            "quit_button": quit_button
        }

    def create_setup_buttons(self, callbacks) -> Dict[str, Button]:
        """Create game setup buttons."""
        props_game_setup_back = self._get_from_layout('buttons', "setup", "game_setup_back") or {
            "name": "game_setup_back",
            "rect": [
                self.game_manager.screen_w / 4 - self.game_manager.play_button_width / 2,
                self.game_manager.screen_h / 2,
                200, 100
            ],
            "color": [100, 0, 0],
            "text": "Back",
            
        }
        props_game_start = self._get_from_layout('buttons', "setup", "game_start") or {
            "name": "game_start",
            "rect": [
                self.game_manager.screen_w / 4 * 3 - self.game_manager.game_start_button_width / 2,
                self.game_manager.screen_h / 8 * 6,
                self.game_manager.game_start_button_width,
                self.game_manager.game_start_button_height
            ],
            "color": [100, 0, 0],
            "text": "Start",
            
        }

        game_setup_back_button = Button(
            props_game_setup_back,
            
            self.game_manager.game_font,
            self.game_manager,
            callback=callbacks['set_game_state_home']
        )
        game_start_button = Button(
            props_game_start,
            
            self.game_manager.game_font,
            self.game_manager,
            callback=callbacks['start_game']
        )

        props_choose_color = self._get_from_layout('buttons', "setup", "player_choose_color_cycle") or {
            "name": "player_choose_color_cycle",
            "rect": [10, 10, 10, 10],
            "color": [0, 0, 0],
            "text": "->",
            
        }
        player_choose_color_cycle_button = Button(
            props_choose_color,
            
            self.game_manager.game_font,
            self.game_manager,
            callback=callbacks['choose_player_color_cycle']
        )

        props_easy = self._get_from_layout('buttons', "setup", "difficulty_level_easy") or {
            "name": "difficulty_level_easy",
            "rect": [10, 10, 10, 10],
            "color": [0, 0, 0],
            "text": "easy",
            
        }
        props_medium = self._get_from_layout('buttons', "setup", "difficulty_level_medium") or {
            "name": "difficulty_level_medium",
            "rect": [10, 10, 10, 10],
            "color": [0, 0, 0],
            "text": "medium",
            
        }
        props_hard = self._get_from_layout('buttons', "setup", "difficulty_level_hard") or {
            "name": "difficulty_level_hard",
            "rect": [10, 10, 10, 10],
            "color": [0, 0, 0],
            "text": "hard",
            
        }

        difficulty_level_easy_button = Button(
            props_easy,
            
            self.game_manager.game_font,
            self.game_manager,
            callback=callbacks['set_diff_level_easy']
        )
        difficulty_level_medium_button = Button(
            props_medium,
            
            self.game_manager.game_font,
            self.game_manager,
            callback=callbacks['set_diff_level_medium']
        )
        difficulty_level_hard_button = Button(
            props_hard,
            
            self.game_manager.game_font,
            self.game_manager,
            callback=callbacks['set_diff_level_hard']
        )

        props_open_menu = self._get_from_layout('buttons', "setup", "open_menu") or {
            "name": "open_menu",
            "rect": [
                self.game_manager.screen_w - self.game_manager.settings_open_button_offset - self.game_manager.settings_open_button_size,
                self.game_manager.settings_open_button_offset,
                self.game_manager.settings_open_button_size,
                self.game_manager.settings_open_button_size
            ],
            "color": [100, 0, 0],
            "text": "image",
            
        }
        open_menu_button = Button(
            props_open_menu,
            
            self.game_manager.game_font,
            self.game_manager,
            callback=callbacks['open_menu']
        )

        return {
            "difficulty_level_easy_button": difficulty_level_easy_button,
            "difficulty_level_medium_button": difficulty_level_medium_button,
            "difficulty_level_hard_button": difficulty_level_hard_button,
            "open_menu_button": open_menu_button,
            "player_choose_color_cycle_button": player_choose_color_cycle_button,
            "game_start_button": game_start_button,
            "game_setup_back_button": game_setup_back_button
        }

    def create_game_buttons(self, callbacks) -> Dict[str, Button]:
        """Create board/game buttons."""
        props_back = self._get_from_layout('buttons', "game", "back") or {
            "name": "back",
            "rect": [10, 10, 70, 40],
            "color": [100, 100, 200],
            "text": "back",
            
        }
        back_button = Button(
            props_back,
            
            self.game_manager.game_font,
            self.game_manager,
            callback=callbacks['set_game_state_home']
        )

        props_buy_settlement = self._get_from_layout('buttons', "game", "board_buy_settlement") or {
            "name": "board_buy_settlement",
            "rect": [700, 650, 40, 40],
            "color": [0, 0, 0],
            "text": "image",
            
        }
        props_buy_city = self._get_from_layout('buttons', "game", "board_buy_city") or {
            "name": "board_buy_city",
            "rect": [800, 650, 40, 40],
            "color": [0, 0, 0],
            "text": "image",
            
        }
        props_buy_road = self._get_from_layout('buttons', "game", "board_buy_road") or {
            "name": "board_buy_road",
            "rect": [900, 10, 10, 40],
            "color": [0, 0, 0],
            "text": "image",
            
        }
        props_buy_dev = self._get_from_layout('buttons', "game", "board_buy_development") or {
            "name": "board_buy_development",
            "rect": [1000, 40, 40, 40],
            "color": [0, 0, 0],
            "text": "image",
            
        }
        props_roll_dice = self._get_from_layout('buttons', "game", "board_roll_dice") or {
            "name": "board_roll_dice",
            "rect": [1050, 600, 40, 40],
            "color": [0, 0, 0],
            "text": "image",
            
        }

        board_buy_settlement_button = Button(
            props_buy_settlement,
            
            self.game_manager.game_font,
            self.game_manager
        )
        board_buy_city_button = Button(
            props_buy_city,
            
            self.game_manager.game_font,
            self.game_manager
        )
        board_buy_road_button = Button(
            props_buy_road,
            
            self.game_manager.game_font,
            self.game_manager
        )
        board_buy_development_button = Button(
            props_buy_dev,
            
            self.game_manager.game_font,
            self.game_manager
        )
        board_roll_dice_button = Button(
            props_roll_dice,
            
            self.game_manager.game_font,
            self.game_manager
        )
        
        props_settings_menu = self._get_from_layout('buttons', "game", "settings_menu") or {
            "name": "settings_menu",
            "rect": [
                self.game_manager.screen_w - self.game_manager.settings_open_button_offset - self.game_manager.settings_open_button_size,
                self.game_manager.settings_open_button_offset,
                self.game_manager.settings_open_button_size,
                self.game_manager.settings_open_button_size
            ],
            "color": [100, 0, 0],
            "text": "image",
            
        }
        settings_menu_button = Button(
            props_settings_menu,
            
            self.game_manager.game_font,
            self.game_manager,
            callback=callbacks['open_menu']
        )

        return {
            "board_buy_settlement_button": board_buy_settlement_button,
            "board_buy_city_button": board_buy_city_button,
            "board_buy_road_button": board_buy_road_button,
            "board_buy_development_button": board_buy_development_button,
            "board_roll_dice_button": board_roll_dice_button,
            "settings_menu_button": settings_menu_button,
            "back_button": back_button
        }

    def create_menu_buttons(self, callbacks) -> Dict[str, Dict[str, Button]]:
        """Create menu tab buttons and content buttons."""
        tabs = {
            "input": Button(
                {"name": "input", "rect": [300, self.game_manager.menu_tab_margin_top, self.game_manager.menu_input_tab_size[0], self.game_manager.menu_input_tab_size[1]], "color": [100, 0, 0], "text": "Input", },
                
                self.game_manager.game_font,
                self.game_manager,
                callback=callbacks['change_tab_input']
            ),
            "accessibility": Button(
                {"name": "accessibility", "rect": [400, self.game_manager.menu_tab_margin_top, self.game_manager.menu_accessibility_tab_size[0], self.game_manager.menu_accessibility_tab_size[1]], "color": [100, 0, 0], "text": "Accessibility", },
                
                self.game_manager.game_font,
                self.game_manager,
                callback=callbacks['change_tab_accessibility']
            ),
            "gameplay": Button(
                {"name": "gameplay", "rect": [self.game_manager.menu_size[0] / 2 - self.game_manager.menu_gameplay_tab_size[0] / 2, self.game_manager.menu_tab_margin_top, self.game_manager.menu_gameplay_tab_size[0], self.game_manager.menu_gameplay_tab_size[1]], "color": [100, 0, 0], "text": "Gameplay", },
                
                self.game_manager.game_font,
                self.game_manager,
                callback=callbacks['change_tab_gameplay']
            ),
            "audio": Button(
                {"name": "audio", "rect": [700, self.game_manager.menu_tab_margin_top, self.game_manager.menu_audio_tab_size[0], self.game_manager.menu_audio_tab_size[1]], "color": [100, 0, 0], "text": "Audio", },
                
                self.game_manager.game_font,
                self.game_manager,
                callback=callbacks['change_tab_audio']
            ),
            "graphics": Button(
                {"name": "graphics", "rect": [800, self.game_manager.menu_tab_margin_top, self.game_manager.menu_graphics_tab_size[0], self.game_manager.menu_graphics_tab_size[1]], "color": [100, 0, 0], "text": "Graphics", },
                
                self.game_manager.game_font,
                self.game_manager,
                callback=callbacks['change_tab_graphics']
            ),
            "close_menu": Button(
                {"name": "close_menu", "rect": [self.game_manager.menu_size[0] - self.game_manager.close_menu_size[0] - self.game_manager.close_menu_margins[0], self.game_manager.close_menu_margins[1], self.game_manager.close_menu_size[0], self.game_manager.close_menu_size[1]], "color": [100, 0, 0], "text": "Close", },
                
                self.game_manager.game_font,
                self.game_manager,
                callback=callbacks['close_menu']
            )
        }

        # Content buttons for each tab
        props_test1 = self._get_from_layout('buttons', "menu", "test1", tab="input") or {
            "name": "test1", "rect": [200, 100, 100, 50], "color": [200, 50, 100], "text": "test1", 
        }
        input_buttons = {
            "test1": Button(props_test1,  self.game_manager.game_font, self.game_manager)
        }

        props_test2 = self._get_from_layout('buttons', "menu", "test2", tab="accessibility") or {
            "name": "test2", "rect": [200, 100, 100, 50], "color": [200, 50, 100], "text": "test2", 
        }
        accessability_buttons = {
            "test2": Button(props_test2,  self.game_manager.game_font, self.game_manager)
        }

        props_test3_graphics = self._get_from_layout('buttons', "menu", "test3", tab="graphics") or {
            "name": "test3", "rect": [200, 100, 100, 50], "color": [200, 50, 100], "text": "test3", 
        }
        graphics_buttons = {
            "test3": Button(props_test3_graphics,  self.game_manager.game_font, self.game_manager)
        }

        props_test4 = self._get_from_layout('buttons', "menu", "test4", tab="audio") or {
            "name": "test4", "rect": [200, 100, 100, 50], "color": [200, 50, 100], "text": "test4", 
        }
        audio_buttons = {
            "test4": Button(props_test4,  self.game_manager.game_font, self.game_manager)
        }

        props_test5 = self._get_from_layout('buttons', "menu", "test5", tab="gameplay") or {
            "name": "test5", "rect": [200, 100, 100, 50], "color": [200, 50, 100], "text": "test5", 
        }
        gameplay_buttons = {
            "test5": Button(props_test5,  self.game_manager.game_font, self.game_manager)
        }

        return {
            "tabs": tabs,
            "gameplay": gameplay_buttons,
            "audio": audio_buttons,
            "graphics": graphics_buttons,
            "accessibility": accessability_buttons,
            "input": input_buttons
        }

    # --- SLIDER CREATION --- #

    def create_all_sliders(self, callbacks) -> Dict[str, Dict]:
        """Create all sliders for all game states."""
        return {
            "home": {},
            "setup": self.create_setup_sliders(callbacks),
            "game": {},
            "menu": self.create_menu_sliders(callbacks)
        }

    def create_setup_sliders(self, callbacks) -> Dict[str, Slider]:
        """Create sliders for the setup screen."""
        props = self._get_from_layout('sliders', "setup", "player_num_slider") or {
            "name": "player_num_slider",
            "rect": [100, 200, 300, 20],
            "wrapper_rect": [100, 200, 300, 20],
            "min_value": 1,
            "max_value": 4,
            "bar_color": [0, 100, 0],
            "handle_color": [100, 0, 0],
            "handle_radius": 10
        }

        player_num_slider = Slider(props, self.game_manager.players_num, self.game_manager, None, callback=None)
        # Assign callback after creation so the lambda can reference the slider instance
        player_num_slider.callback = lambda: callbacks['set_player_num'](int(player_num_slider.value))

        return {
            "player_num_slider": player_num_slider
        }

    def create_menu_sliders(self, callbacks) -> Dict[str, Dict[str, Slider]]:
        """Create sliders for the menu."""
        # Input tab sliders
        props_deadzone = self._get_from_layout('sliders', "menu", "deadzone", tab="input") or {
            "name": "deadzone", "rect": [100, 200, 300, 20], "wrapper_rect": [100, 200, 300, 20],
            "min_value": 0, "max_value": 1, "initial_value": 0.1,
            "bar_color": [0, 100, 0], "handle_color": [100, 0, 0], "handle_radius": 10
        }
        props_controller_sens = self._get_from_layout('sliders', "menu", "controller_sensitivity", tab="input") or {
            "name": "controller_sensitivity", "rect": [100, 300, 300, 20], "wrapper_rect": [100, 300, 300, 20],
            "min_value": 0, "max_value": 10, "initial_value": 5,
            "bar_color": [0, 100, 0], "handle_color": [100, 0, 0], "handle_radius": 10
        }
        props_controller_vib = self._get_from_layout('sliders', "menu", "controller_vibration_strength", tab="input") or {
            "name": "controller_vibration_strength", "rect": [100, 400, 300, 20], "wrapper_rect": [100, 400, 300, 20],
            "min_value": 0, "max_value": 1, "initial_value": 0.5,
            "bar_color": [0, 100, 0], "handle_color": [100, 0, 0], "handle_radius": 10
        }

        input_sliders = {
            "deadzone": Slider(props_deadzone, props_deadzone.get("initial_value", 0.1), self.game_manager, None),
            "controller_sensitivity": Slider(props_controller_sens, props_controller_sens.get("initial_value", 5), self.game_manager, None),
            "controller_vibration_strength": Slider(props_controller_vib, props_controller_vib.get("initial_value", 0.5), self.game_manager, None)
        }
        
        accessability_sliders = {}
        
        props_brightness = self._get_from_layout('sliders', "menu", "brightness", tab="graphics") or {
            "name": "brightness", "rect": [100, 200, 300, 20], "wrapper_rect": [100, 200, 300, 20],
            "min_value": 0, "max_value": 1, "initial_value": 0.5,
            "bar_color": [0, 100, 0], "handle_color": [100, 0, 0], "handle_radius": 10
        }
        graphics_sliders = {
            "brightness": Slider(props_brightness, props_brightness.get("initial_value", 0.5), self.game_manager, None)
        }
        
        props_master = self._get_from_layout('sliders', "menu", "master_volume", tab="audio") or {
            "name": "master_volume", "rect": [100, 200, 300, 20], "wrapper_rect": [100, 200, 300, 20],
            "min_value": 0, "max_value": 1, "initial_value": 0.5,
            "bar_color": [0, 100, 0], "handle_color": [100, 0, 0], "handle_radius": 10
        }
        props_music = self._get_from_layout('sliders', "menu", "music_volume", tab="audio") or {
            "name": "music_volume", "rect": [100, 300, 300, 20], "wrapper_rect": [100, 300, 300, 20],
            "min_value": 0, "max_value": 1, "initial_value": 0.5,
            "bar_color": [0, 100, 0], "handle_color": [100, 0, 0], "handle_radius": 10
        }
        props_sfx = self._get_from_layout('sliders', "menu", "sfx_volume", tab="audio") or {
            "name": "sfx_volume", "rect": [100, 400, 300, 20], "wrapper_rect": [100, 400, 300, 20],
            "min_value": 0, "max_value": 1, "initial_value": 0.5,
            "bar_color": [0, 100, 0], "handle_color": [100, 0, 0], "handle_radius": 10
        }

        audio_sliders = {
            "master_volume": Slider(props_master, props_master.get("initial_value", 0.5), self.game_manager, None),
            "music_volume": Slider(props_music, props_music.get("initial_value", 0.5), self.game_manager, None),
            "sfx_volume": Slider(props_sfx, props_sfx.get("initial_value", 0.5), self.game_manager, None)
        }
        
        gameplay_sliders = {}
        
        return {
            "input": input_sliders,
            "accessibility": accessability_sliders,
            "graphics": graphics_sliders,
            "audio": audio_sliders,
            "gameplay": gameplay_sliders
        }

    # --- TOGGLE CREATION --- #

    def create_all_toggles(self, callbacks) -> Dict[str, Dict]:
        """Create all toggles for all game states."""
        return {
            "home": {},
            "setup": {},
            "game": {},
            "menu": self.create_menu_toggles(callbacks)
        }

    def create_menu_toggles(self, callbacks) -> Dict[str, Dict[str, Toggle]]:
        """Create toggles for the menu."""

        # Build input toggles using layout props
        props_controller_vib = self._get_from_layout('toggles', "menu", "controller_vibration", tab="input") or {
            "name": "controller_vibration", "rect": [100, 300, 150, 50], "guiding_lines": self.game_manager.default_guiding_lines,
            "height": self.game_manager.default_height, "center_width": self.game_manager.default_center_width, "fill_color": list(self.game_manager.default_fill_color),
            "handle_color": list(self.game_manager.default_handle_color), "toggle_gap": self.game_manager.default_toggle_gap, "time_to_flip": self.game_manager.default_time_to_flip
        }
        props_invert_y = self._get_from_layout('toggles', "menu", "invert_y_axis", tab="input") or {
            "name": "invert_y_axis", "rect": [200, 300, 150, 50], "guiding_lines": self.game_manager.default_guiding_lines,
            "height": self.game_manager.default_height, "center_width": self.game_manager.default_center_width, "fill_color": list(self.game_manager.default_fill_color),
            "handle_color": list(self.game_manager.default_handle_color), "toggle_gap": self.game_manager.default_toggle_gap, "time_to_flip": self.game_manager.default_time_to_flip
        }
        props_invert_x = self._get_from_layout('toggles', "menu", "invert_x_axis", tab="input") or {
            "name": "invert_x_axis", "rect": [300, 300, 150, 50], "guiding_lines": self.game_manager.default_guiding_lines,
            "height": self.game_manager.default_height, "center_width": self.game_manager.default_center_width, "fill_color": list(self.game_manager.default_fill_color),
            "handle_color": list(self.game_manager.default_handle_color), "toggle_gap": self.game_manager.default_toggle_gap, "time_to_flip": self.game_manager.default_time_to_flip
        }

        input_toggles = {
            "controller_vibration": Toggle(props_controller_vib, 0, self.game_manager, on=self.game_manager.default_on, callback=None),
            "invert_y_axis": Toggle(props_invert_y, 0, self.game_manager, on=self.game_manager.default_on, callback=None),
            "invert_x_axis": Toggle(props_invert_x, 0, self.game_manager, on=self.game_manager.default_on, callback=None)
        }
        
        props_high_contrast = self._get_from_layout('toggles', "menu", "high_contrast_mode", tab="accessibility") or {
            "name": "high_contrast_mode", "rect": [100, 300, 150, 50], "guiding_lines": self.game_manager.default_guiding_lines,
            "height": self.game_manager.default_height, "center_width": self.game_manager.default_center_width, "fill_color": list(self.game_manager.default_fill_color),
            "handle_color": list(self.game_manager.default_handle_color), "toggle_gap": self.game_manager.default_toggle_gap, "time_to_flip": self.game_manager.default_time_to_flip
        }
        accessability_toggles = {
            "high_contrast_mode": Toggle(props_high_contrast, 0, self.game_manager, on=self.game_manager.default_on, callback=None)
        }
        
        props_aa = self._get_from_layout('toggles', "menu", "aa", tab="graphics") or {
            "name": "aa", "rect": [200, 300, 150, 50], "guiding_lines": self.game_manager.default_guiding_lines,
            "height": self.game_manager.default_height, "center_width": self.game_manager.default_center_width, "fill_color": list(self.game_manager.default_fill_color),
            "handle_color": list(self.game_manager.default_handle_color), "toggle_gap": self.game_manager.default_toggle_gap, "time_to_flip": self.game_manager.default_time_to_flip
        }
        props_fullscreen = self._get_from_layout('toggles', "menu", "fullscreen", tab="graphics") or {
            "name": "fullscreen", "rect": [300, 300, 150, 50], "guiding_lines": self.game_manager.default_guiding_lines,
            "height": self.game_manager.default_height, "center_width": self.game_manager.default_center_width, "fill_color": list(self.game_manager.default_fill_color),
            "handle_color": list(self.game_manager.default_handle_color), "toggle_gap": self.game_manager.default_toggle_gap, "time_to_flip": self.game_manager.default_time_to_flip
        }
        props_shadows = self._get_from_layout('toggles', "menu", "shadows", tab="graphics") or {
            "name": "shadows", "rect": [400, 300, 150, 50], "guiding_lines": self.game_manager.default_guiding_lines,
            "height": self.game_manager.default_height, "center_width": self.game_manager.default_center_width, "fill_color": list(self.game_manager.default_fill_color),
            "handle_color": list(self.game_manager.default_handle_color), "toggle_gap": self.game_manager.default_toggle_gap, "time_to_flip": self.game_manager.default_time_to_flip
        }
        graphics_toggles = {
            "aa": Toggle(props_aa, 0, self.game_manager, on=self.game_manager.default_on, callback=None),
            "fullscreen": Toggle(props_fullscreen, 0, self.game_manager, on=self.game_manager.default_on, callback=None),
            "shadows": Toggle(props_shadows, 0, self.game_manager, on=self.game_manager.default_on, callback=None)
        }
        
        props_sfx = self._get_from_layout('toggles', "menu", "sfx", tab="audio") or {
            "name": "sfx", "rect": [100, 300, 150, 50], "guiding_lines": self.game_manager.default_guiding_lines,
            "height": self.game_manager.default_height, "center_width": self.game_manager.default_center_width, "fill_color": list(self.game_manager.default_fill_color),
            "handle_color": list(self.game_manager.default_handle_color), "toggle_gap": self.game_manager.default_toggle_gap, "time_to_flip": self.game_manager.default_time_to_flip
        }
        audio_toggles = {
            "sfx": Toggle(props_sfx, 0, self.game_manager, on=self.game_manager.default_on, callback=None)
        }
        
        props_hud = self._get_from_layout('toggles', "menu", "hud", tab="gameplay") or {
            "name": "hud", "rect": [100, 300, 150, 50], "guiding_lines": self.game_manager.default_guiding_lines,
            "height": self.game_manager.default_height, "center_width": self.game_manager.default_center_width, "fill_color": list(self.game_manager.default_fill_color),
            "handle_color": list(self.game_manager.default_handle_color), "toggle_gap": self.game_manager.default_toggle_gap, "time_to_flip": self.game_manager.default_time_to_flip
        }
        props_language = self._get_from_layout('toggles', "menu", "language", tab="gameplay") or {
            "name": "language", "rect": [200, 300, 150, 50], "guiding_lines": self.game_manager.default_guiding_lines,
            "height": self.game_manager.default_height, "center_width": self.game_manager.default_center_width, "fill_color": list(self.game_manager.default_fill_color),
            "handle_color": list(self.game_manager.default_handle_color), "toggle_gap": self.game_manager.default_toggle_gap, "time_to_flip": self.game_manager.default_time_to_flip
        }
        gameplay_toggles = {
            "hud": Toggle(props_hud, 0, self.game_manager, on=self.game_manager.default_on, callback=None),
            "language": Toggle(props_language, 0, self.game_manager, on=self.game_manager.default_on, callback=None)
        }
        
        return {
            "input": input_toggles,
            "accessibility": accessability_toggles,
            "graphics": graphics_toggles,
            "audio": audio_toggles,
            "gameplay": gameplay_toggles
        }

    # --- IMAGE CREATION --- #

    def create_all_images(self, callbacks) -> Dict[str, Dict]:
        """Create all images for all game states."""
        return {
            "home": {},
            "setup": {},
            "game": self.create_game_images(callbacks),
            "menu": {}
        }

    def create_game_images(self, callbacks) -> Dict[str, Image]:
        """Create images for the game screen."""
        props_buy_background = self._get_from_layout('images', "game", "buy_background_image") or {
            "name": "buy_background_image",
            "rect": [self.game_manager.screen_w / 2, 650, int(self.game_manager.screen_w / 3), 100],
            "image_path": ""
        }
        buy_background_image = Image(props_buy_background, self.game_manager, callback=None)

        return {
            "buy_background_image": buy_background_image
        }

    # --- TEXT DISPLAY CREATION --- #

    def create_all_text_displays(self, callbacks) -> Dict[str, Dict]:
        """Create all text displays for all game states."""
        return {
            "home": {},
            "setup": self.create_setup_text_displays(callbacks),
            "game": self.create_game_text_displays(callbacks),
            "menu": self.create_menu_text_displays(callbacks)
        }

    def create_setup_text_displays(self, callbacks) -> Dict[str, TextDisplay]:
        """Create text displays for the setup screen."""
        props_player_num_text = self._get_from_layout('text_displays', "setup", "player_num_text") or {
            "name": "player_num_text",
            "rect": [100, 150, 300, 50],
            "color": [255, 255, 255],
            "text": "Number of Players: 2",
            "text_color": [0, 0, 0],
            "padding": 5
        }
        player_num_text = TextDisplay(
            props_player_num_text,
            self.game_manager,
            self.game_manager.game_font,
            background_image=None
        )
        return {
            "player_num_text": player_num_text
        }

    def create_game_text_displays(self, callbacks) -> Dict[str, TextDisplay]:
        """Create text displays for the game screen."""
        return {}

    def create_menu_text_displays(self, callbacks) -> Dict[str, Dict[str, TextDisplay]]:
        """Create text displays for the menu."""
        input_text_displays = {}
        accessibility_text_displays = {}
        graphics_text_displays = {}
        audio_text_displays = {}
        gameplay_text_displays = {}

        return {
            "input": input_text_displays,
            "accessibility": accessibility_text_displays,
            "graphics": graphics_text_displays,
            "audio": audio_text_displays,
            "gameplay": gameplay_text_displays
        }

    # --- MENU CREATION --- #

    def create_menu(self, buttons, toggles, sliders) -> Menu:
        """Create the main menu."""
        menu = Menu(
            self.game_manager.menu_rect,
            self.game_manager.game_font,
            buttons['menu'],
            toggles["menu"],
            sliders["menu"],
            self.game_manager.init_location,
            self.game_manager.final_location,
            bckg_color=self.game_manager.menu_background_color
        )
        return menu
