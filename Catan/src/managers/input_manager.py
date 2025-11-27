import pygame
import math
from typing import Dict
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_manager import GameManager
    from graphics_manager import GraphicsManager
    from helper_manager import HelperManager
    from src.managers.audio_manager import AudioManager
    from src.managers.player_manager import PlayerManager

from src.ui.button import Button
from src.entities.node import Node
from src.ui.menu import Menu
from src.ui.toggle import Toggle
from src.ui.image import Image
from src.ui.slider import Slider
from src.ui.text_display import TextDisplay

class InputManager:
    def __init__(self):
        #All of these have to be defined after initialization
        self.game_manager: GameManager
        self.graphics_manager: GraphicsManager
        self.helper_manager: HelperManager
        self.audio_manager: AudioManager
        self.player_manager: PlayerManager
        
        # Handlers are now passed directly into Button/Slider/Image instances via callback args.

        ## --- VARIABLES --- ##

        self.dragging = False #true between MBD and MBU with distance > 5 pixels
        self.clicked = False #true between MBD and MBU
        self.active: Button | Slider | Toggle | Button | Image | None #the currently active clickable object
        self.start_x = 0
        self.start_y = 0
        self.click_end_x = 0
        self.click_end_y = 0

    def handle_input(self, x, y, event_type) -> None:
        #MBD will only set active clickable object, actions will happen on MBU if mouse is still over the clickable object
        if event_type == pygame.MOUSEBUTTONDOWN:
            #create a start x and y to compare with the mouses position on future events
            self.start_x = x
            self.start_y = y
            self.clicked = True
            state = self.game_manager.game_state
            # If the menu is open, we check the menu buttons first
            if self.graphics_manager.menu_open:
                # Check if the click is within the menu area
                button_clicked: Button | None = self.helper_manager.check_clickable_from_dict(self.buttons["menu"][self.menu.active_tab], (x, y), self.game_manager.menu_margins[0], self.game_manager.menu_margins[1])
                toggle_clicked: Toggle | None = self.helper_manager.check_clickable_from_dict(self.toggles["menu"][self.menu.active_tab], (x, y), self.game_manager.menu_margins[0], self.game_manager.menu_margins[1])
                slider_clicked: Slider | None = self.helper_manager.check_clickable_from_dict(self.sliders["menu"][self.menu.active_tab], (x, y), self.game_manager.menu_margins[0], self.game_manager.menu_margins[1])
                # If not, check the tabs of the menu
                if not button_clicked:
                    button_clicked = self.helper_manager.check_clickable_from_dict(self.buttons["menu"]["tabs"], (x, y), self.game_manager.menu_margins[0], self.game_manager.menu_margins[1])

                    self.active = slider_clicked

            else:
                # If the menu is not open, we check the buttons for the current game state
                button_clicked: Button | None = self.helper_manager.check_clickable_from_dict(self.buttons[state], (x, y))
                toggle_clicked: Toggle | None = self.helper_manager.check_clickable_from_dict(self.toggles[state], (x, y))
                slider_clicked: Slider | None = self.helper_manager.check_clickable_from_dict(self.sliders[state], (x, y))

            if button_clicked:
                self.active = button_clicked

            if toggle_clicked:
                self.active = toggle_clicked

            if slider_clicked:
                self.active = slider_clicked

        elif event_type == pygame.MOUSEMOTION:
            #find distance from start to current position
            dx = x - self.start_x
            dy = y - self.start_y
            #if the distance is greater than 5 pixels, we are dragging
            #print(math.sqrt(abs(dx)**2 + abs(dy)**2))
            drag_distance = math.sqrt(abs(dx)**2 + abs(dy)**2)
            if self.clicked and drag_distance > 5:
                self.dragging = True
            #handle drag updates
            if self.dragging and isinstance(self.active, Slider):
                if self.graphics_manager.menu_open:
                    self.handle_drag(x - self.game_manager.menu_margins[0], y - self.game_manager.menu_margins[1], self.sliders["menu"][self.menu.active_tab])
                else:
                    self.handle_drag(x, y, self.sliders[self.game_manager.game_state])

        elif event_type == pygame.MOUSEBUTTONUP:
            self.click_end_x = x
            self.click_end_y = y
            self.dragging = False
            self.clicked = False

            if self.active:
                self.handle_click()

    def handle_click(self) -> None:
        x = self.click_end_x
        y = self.click_end_y
        state = self.game_manager.game_state

        #if the click ended inside the clickable object, call its handler
        #TODO: simplify logic, to much computation
        assert self.active is not None
        handler = None
        if self.graphics_manager.menu_open:
            if pygame.rect.Rect.collidepoint(pygame.Rect(self.active.rect.x + self.game_manager.menu_margins[0], self.active.rect.y + self.game_manager.menu_margins[1], self.active.rect.w, self.active.rect.h), (x, y)):
                handler = getattr(self.active, 'callback', None)
            if isinstance(self.active, Toggle):
                self.active.set_animating(self.graphics_manager.time)

        else:
            if pygame.rect.Rect.collidepoint(self.active.rect, (x, y)):
                handler = getattr(self.active, 'callback', None)

            if isinstance(self.active, Toggle):
                self.active.set_animating(self.graphics_manager.time)

        if handler:
            handler()
    
    def handle_drag(self, x: int, y: int, sliders: Dict[str, Slider]) -> None:
        if self.active and isinstance(self.active, Slider):
            self.active.update_location(x, y)

    def handle_keyboard(self, key: pygame.event.Event):
        if key == pygame.K_0:
            self.game_manager.dev_mode = not self.game_manager.dev_mode

    ## --- EVENT FUNCTIONS --- ##
    #TODO: Add return types to functions
    def player_num_increase(self):
        if (self.game_manager.players_num < 4):
            self.game_manager.players_num += 1

    def player_num_decrease(self):
        if (self.game_manager.players_num > 2):
            self.game_manager.players_num -= 1

    def set_player_num(self, num: int) -> None:
        self.game_manager.players_num = num
        self.text_displays["setup"]["player_num_text"].update_text(f"Number of Players: {num}")

    def choose_player_color_cycle(self):
        self.game_manager.player_color_chosen_index += 1
        self.game_manager.player_color_chosen_index %= len(self.game_manager.player_colors)

    #TODO: Implement
    def set_diff_level(self, level: str):
        pass
        #if (self.game_manager.difficulty_level != level):
        #   self.game_manager.difficulty_level = level
        
    def start_game(self):
        self.game_manager.game_state = "init"

    def open_menu(self):
        self.menu.open_menu()
        self.graphics_manager.menu_open = True
        self.buttons["setup"]["open_menu_button"].hide()

    def close_menu(self):
        self.menu.close_menu()
        self.graphics_manager.menu_open = False
        self.buttons["setup"]["open_menu_button"].show()

    def set_game_state(self, state: str):
        self.game_manager.game_state = state

    def change_tab(self, new_tab):
        self.menu.active_tab = new_tab
        self.buttons["menu"]["tabs"][new_tab].color = (0, 100, 0)  # Highlight the active tab
        for tab_name, button in self.buttons["menu"]["tabs"].items():
            if tab_name != new_tab:
                button.color = (100, 0, 0)
        self.menu.update_menu(self.graphics_manager.time)

    def quit(self):
        self.game_manager.running = False

    ## --- ON INIT --- ##

    def set_game_manager(self, game_manager: 'GameManager') -> None:
        self.game_manager = game_manager
        #Put all new UI types here
        self.buttons = self.create_buttons()
        self.toggles = self.create_toggles()
        self.sliders = self.create_sliders()
        self.images = self.create_images()
        self.menu = self.create_menu()
        self.text_displays = self.create_text_displays()
        self.initialize_ui_elements()

    def set_graphics_manager(self, graphics_manager: 'GraphicsManager') -> None:
        self.graphics_manager = graphics_manager
        self.change_tab("input")  # Set the initial active tab

    def set_helper_manager(self, helper_manager: 'HelperManager') -> None:
        self.helper_manager = helper_manager

    def _layout_section_for_state(self, state: str) -> str:
        # map internal state names to layout.json sections
        if state == "main_menu":
            return "home"
        if state == "menu":
            return "menu"
        return state

    def get_layout_button_props(self, state: str, name: str, tab: str | None = None) -> dict | None:
        """Return layout props dict for given named button (or None if not found).
        `state` is a game_state like 'main_menu', 'setup', 'game' or 'menu'.
        If `state` == 'menu', `tab` should be provided to look under that tab section.
        """
        layout = getattr(self.game_manager, 'layout', None)
        if not layout:
            return None

        layout_section = self._layout_section_for_state(state)
        try:
            if layout_section == 'menu':
                if not tab:
                    return None
                buttons_list = layout[layout_section][tab]['buttons']
            else:
                buttons_list = layout[layout_section]['buttons']
        except Exception:
            return None

        for b in buttons_list:
            if b.get('name') == name:
                return b
        return None

    def get_layout_slider_props(self, state: str, name: str, tab: str | None = None) -> dict | None:
        """Return layout props dict for given named slider (or None if not found).
        Mirrors `get_layout_button_props` but looks for sliders in the layout JSON.
        """
        layout = getattr(self.game_manager, 'layout', None)
        if not layout:
            return None

        layout_section = self._layout_section_for_state(state)
        try:
            if layout_section == 'menu':
                if not tab:
                    return None
                sliders_list = layout[layout_section][tab].get('sliders', [])
            else:
                sliders_list = layout[layout_section].get('sliders', [])
        except Exception:
            return None

        for s in sliders_list:
            if s.get('name') == name:
                return s
        return None
    
    def create_menu(self) -> Menu:
        menu = Menu(self.game_manager.screen, self.game_manager.game_font, "static", self.buttons['menu'], self.toggles["menu"], self.sliders["menu"], self.game_manager.menu_size, self.game_manager.init_location, self.game_manager.final_location, bckg_color=self.game_manager.menu_background_color)
        return menu
    
    def initialize_ui_elements(self) -> None:
        # Initialize any UI elements that require setup after creation
        # Call the callback for setup player number slider to set initial UI text
        player_num_slider = self.sliders["setup"]["player_num_slider"]
        if hasattr(player_num_slider, 'callback') and player_num_slider.callback:
            player_num_slider.callback()

    # - CREATE BUTTONS - #

    def create_buttons(self):
        return {
            "main_menu": self.create_title_buttons(),
            "setup": self.create_setup_buttons(),
            "game": self.create_game_buttons(),
            "menu": self.create_menu_buttons()
        }
    
    def create_title_buttons(self) -> Dict[str, Button]:
        #create title screen
        props_play = self.get_layout_button_props("main_menu", "play") or {"name":"play", "rect":[self.game_manager.screen_w / 2 - self.game_manager.play_button_width / 2, self.game_manager.screen_h / 2 - self.game_manager.play_button_height / 1.75, self.game_manager.play_button_width, self.game_manager.play_button_height], "color":[0,100,0], "text":"PLAY", "location":[0,0]}
        props_quit = self.get_layout_button_props("main_menu", "quit") or {"name":"quit", "rect":[self.game_manager.screen_w / 2 - self.game_manager.play_button_width / 2, self.game_manager.screen_h / 2 + self.game_manager.play_button_height / 1.75, self.game_manager.play_button_width, self.game_manager.play_button_height], "color":[100,0,0], "text":"QUIT", "location":[0,0]}

        play_button = Button(props_play, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=lambda: self.set_game_state("setup"))
        quit_button = Button(props_quit, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=self.quit)
        return {
            "play_button": play_button, 
            "quit_button": quit_button
        }

    def create_setup_buttons(self) -> Dict[str, Button]:
        #create game setup buttons
        props_game_setup_back = self.get_layout_button_props("setup", "game_setup_back") or {"name":"game_setup_back", "rect":[self.game_manager.screen_w / 4 - self.game_manager.play_button_width / 2, self.game_manager.screen_h / 2, 200, 100], "color":[100,0,0], "text":"Back", "location":[0,0]}
        props_game_start = self.get_layout_button_props("setup", "game_start") or {"name":"game_start", "rect":[self.game_manager.screen_w / 4 * 3 - self.game_manager.game_start_button_width / 2, self.game_manager.screen_h / 8 * 6, self.game_manager.game_start_button_width, self.game_manager.game_start_button_height], "color":[100,0,0], "text":"Start", "location":[0,0]}

        game_setup_back_button = Button(props_game_setup_back, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=lambda: self.set_game_state("main_menu"))
        game_start_button = Button(props_game_start, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=self.start_game)
        
        #TODO: decide on player_num being changed by button or slider
        #player_num_increase_button = Button((0, 100, 0), "+", pygame.Rect(self.game_manager.screen_w / 4 - self.game_manager.player_number_incease_decrease_button_size / 2 + 100, self.game_manager.screen_h / 4 * 2.5, self.game_manager.player_number_incease_decrease_button_size, self.game_manager.player_number_incease_decrease_button_size), "player_num_increase", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        #player_num_decrease_button = Button((0, 100, 0), "-", pygame.Rect(self.game_manager.screen_w / 4 - self.game_manager.player_number_incease_decrease_button_size / 2 - 100, self.game_manager.screen_h / 4 * 2.5, self.game_manager.player_number_incease_decrease_button_size, self.game_manager.player_number_incease_decrease_button_size), "player_num_decrease", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        
        props_choose_color = self.get_layout_button_props("setup", "player_choose_color_cycle") or {"name":"player_choose_color_cycle","rect":[10,10,10,10],"color":[0,0,0],"text":"->","location":[0,0]}
        player_choose_color_cycle_button = Button(props_choose_color, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=self.choose_player_color_cycle)
        
        props_easy = self.get_layout_button_props("setup", "difficulty_level_easy") or {"name":"difficulty_level_easy","rect":[10,10,10,10],"color":[0,0,0],"text":"easy","location":[0,0]}
        props_medium = self.get_layout_button_props("setup", "difficulty_level_medium") or {"name":"difficulty_level_medium","rect":[10,10,10,10],"color":[0,0,0],"text":"medium","location":[0,0]}
        props_hard = self.get_layout_button_props("setup", "difficulty_level_hard") or {"name":"difficulty_level_hard","rect":[10,10,10,10],"color":[0,0,0],"text":"hard","location":[0,0]}

        difficulty_level_easy_button = Button(props_easy, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=lambda: self.set_diff_level("easy"))
        difficulty_level_medium_button = Button(props_medium, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=lambda: self.set_diff_level("medium"))
        difficulty_level_hard_button = Button(props_hard, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=lambda: self.set_diff_level("hard"))
        
        props_open_menu = self.get_layout_button_props("setup", "open_menu") or {"name":"open_menu","rect":[self.game_manager.screen_w - self.game_manager.settings_open_button_offset - self.game_manager.settings_open_button_size, self.game_manager.settings_open_button_offset, self.game_manager.settings_open_button_size, self.game_manager.settings_open_button_size],"color":[100,0,0],"text":"image","location":[0,0]}
        open_menu_button = Button(props_open_menu, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=self.open_menu)
        
        return {
            #TODO: decide on player_num being changed by button or slider
            #"player_num_increase_button": player_num_increase_button, 
            #"player_num_decrease_button": player_num_decrease_button, 
            "difficulty_level_easy_button": difficulty_level_easy_button, 
            "difficulty_level_medium_button": difficulty_level_medium_button, 
            "difficulty_level_hard_button": difficulty_level_hard_button, 
            "open_menu_button": open_menu_button, 
            "player_choose_color_cycle_button": player_choose_color_cycle_button, 
            "game_start_button": game_start_button, 
            "game_setup_back_button": game_setup_back_button
        }

    def create_game_buttons(self) -> Dict[str, Button]:
        #create board buttons
        props_back = self.get_layout_button_props("game", "back") or {"name":"back","rect":[10,10,70,40],"color":[100,100,200],"text":"back","location":[0,0]}
        back_button = Button(props_back, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=lambda: self.set_game_state("main_menu"))

        props_buy_settlement = self.get_layout_button_props("game", "board_buy_settlement") or {"name":"board_buy_settlement","rect":[700,650,40,40],"color":[0,0,0],"text":"image","location":[0,0]}
        props_buy_city = self.get_layout_button_props("game", "board_buy_city") or {"name":"board_buy_city","rect":[800,650,40,40],"color":[0,0,0],"text":"image","location":[0,0]}
        props_buy_road = self.get_layout_button_props("game", "board_buy_road") or {"name":"board_buy_road","rect":[900,10,10,40],"color":[0,0,0],"text":"image","location":[0,0]}
        props_buy_dev = self.get_layout_button_props("game", "board_buy_development") or {"name":"board_buy_development","rect":[1000,40,40,40],"color":[0,0,0],"text":"image","location":[0,0]}
        props_roll_dice = self.get_layout_button_props("game", "board_roll_dice") or {"name":"board_roll_dice","rect":[1050,600,40,40],"color":[0,0,0],"text":"image","location":[0,0]}

        board_buy_settlement_button = Button(props_buy_settlement, self.game_manager.screen, self.game_manager.game_font, self.game_manager)
        board_buy_city_button = Button(props_buy_city, self.game_manager.screen, self.game_manager.game_font, self.game_manager)
        board_buy_road_button = Button(props_buy_road, self.game_manager.screen, self.game_manager.game_font, self.game_manager)
        board_buy_development_button = Button(props_buy_dev, self.game_manager.screen, self.game_manager.game_font, self.game_manager)
        board_roll_dice_button = Button(props_roll_dice, self.game_manager.screen, self.game_manager.game_font, self.game_manager)
        props_settings_menu = self.get_layout_button_props("game", "settings_menu") or {"name":"settings_menu","rect":[self.game_manager.screen_w - self.game_manager.settings_open_button_offset - self.game_manager.settings_open_button_size, self.game_manager.settings_open_button_offset, self.game_manager.settings_open_button_size, self.game_manager.settings_open_button_size],"color":[100,0,0],"text":"image","location":[0,0]}
        settings_menu_button = Button(props_settings_menu, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=self.open_menu)
        
        #select_citys_button = Button((0, 0, 0), "", )
        #select_roads_button = Button()
        #select_settlements_button = Button()

        return {
            "board_buy_settlement_button": board_buy_settlement_button, 
            "board_buy_city_button": board_buy_city_button, 
            "board_buy_road_button": board_buy_road_button, 
            "board_buy_development_button": board_buy_development_button, 
            "board_roll_dice_button": board_roll_dice_button, 
            "settings_menu_button": settings_menu_button,
            "back_button": back_button
        }
   
    def create_menu_buttons(self) -> Dict[str, Dict[str, Button]]:    
        """
        Tabs:
        -Input
        -Accessibility
        -Graphics
        -Audio
        -Gameplay
        """

        #TODO: fill with buttons
        tabs = {
            "input": 
                Button({"name":"input","rect":[300,self.game_manager.menu_tab_margin_top,self.game_manager.menu_input_tab_size[0],self.game_manager.menu_input_tab_size[1]],"color":[100,0,0],"text":"Input","location":[0,0]}, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=lambda: self.change_tab("input")),
            "accessibility": 
                Button({"name":"accessibility","rect":[400,self.game_manager.menu_tab_margin_top,self.game_manager.menu_accessibility_tab_size[0],self.game_manager.menu_accessibility_tab_size[1]],"color":[100,0,0],"text":"Accessibility","location":[0,0]}, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=lambda: self.change_tab("accessibility")),
            "gameplay": 
                Button({"name":"gameplay","rect":[self.game_manager.menu_size[0] / 2 - self.game_manager.menu_gameplay_tab_size[0] / 2,self.game_manager.menu_tab_margin_top,self.game_manager.menu_gameplay_tab_size[0],self.game_manager.menu_gameplay_tab_size[1]],"color":[100,0,0],"text":"Gameplay","location":[0,0]}, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=lambda: self.change_tab("gameplay")),
            "audio": 
                Button({"name":"audio","rect":[700,self.game_manager.menu_tab_margin_top,self.game_manager.menu_audio_tab_size[0],self.game_manager.menu_audio_tab_size[1]],"color":[100,0,0],"text":"Audio","location":[0,0]}, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=lambda: self.change_tab("audio")),
            "graphics": 
                Button({"name":"graphics","rect":[800,self.game_manager.menu_tab_margin_top,self.game_manager.menu_graphics_tab_size[0],self.game_manager.menu_graphics_tab_size[1]],"color":[100,0,0],"text":"Graphics","location":[0,0]}, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=lambda: self.change_tab("graphics")),
            "close_menu": 
                Button({"name":"close_menu","rect":[self.game_manager.menu_size[0] - self.game_manager.close_menu_size[0] - self.game_manager.close_menu_margins[0], self.game_manager.close_menu_margins[1], self.game_manager.close_menu_size[0], self.game_manager.close_menu_size[1]],"color":[100,0,0],"text":"Close","location":[0,0]}, self.game_manager.screen, self.game_manager.game_font, self.game_manager, callback=self.close_menu)
        } 

        """
        Input (keyboard and controller):
        -Controller vibration (toggle)
        -Deadzone adjustment (slider)
        -Invert Y and X axes (toggles)
        -Key remapping (list TBD: something similar to minecraft w/ keyboard and controller inputs listed?)
        -Sensitivities (sliders TBD)
        """
        #TODO: fill with buttons
        props_test1 = self.get_layout_button_props("menu", "test1", tab="input") or {"name":"test1","rect":[200,100,100,50],"color":[200,50,100],"text":"test1","location":[0,0]}
        input_buttons = {
            "test1": Button(props_test1, self.game_manager.screen, self.game_manager.game_font, self.game_manager)
        }

    
        """
        accessability:
        -Colorblind mode: deuteranopia, protanopia, and tritanopia (multi-choice select box)
        -Font Size: small, medium, large (multi-choice select box)
        -High contrast mode (toggle)
        -TTS: Hesitant to implement because limited usage and maximal time to produce
        """
        #TODO: fill with buttons
        props_test2 = self.get_layout_button_props("menu", "test2", tab="accessibility") or {"name":"test2","rect":[200,100,100,50],"color":[200,50,100],"text":"test2","location":[0,0]}
        accessability_buttons = {
            "test2": Button(props_test2, self.game_manager.screen, self.game_manager.game_font, self.game_manager)
        }

    
        """
        Graphics:
        -AA (toggle)
        -Brightness (slider)
        -Windowed/fullscreen (toggle)
        -Particle effects (toggle)
        -Resolution (multi-choice select box)
        -Shadows (toggle)
        -Texture quality (multi-choice select box)
        -V-sync (toggle)
        """
        #TODO: fill with buttons
        props_test3_graphics = self.get_layout_button_props("menu", "test3", tab="graphics") or {"name":"test3","rect":[200,100,100,50],"color":[200,50,100],"text":"test3","location":[0,0]}
        graphics_buttons = {
            "test3": Button(props_test3_graphics, self.game_manager.screen, self.game_manager.game_font, self.game_manager)
        }

    
        """
        Audio:
        -Master (slider)
        -Music (slider)
        -SFX (toggle)
        """
        #TODO: fill with buttons
        props_test4 = self.get_layout_button_props("menu", "test4", tab="audio") or {"name":"test4","rect":[200,100,100,50],"color":[200,50,100],"text":"test4","location":[0,0]}
        audio_buttons = {
            "test4": Button(props_test4, self.game_manager.screen, self.game_manager.game_font, self.game_manager)
        }

    
        """
        Gameplay:
        -HUD (ask ChatGPT)
        -Language (multi-choice select box)
        """ 
        #TODO: fill with buttons
        props_test5 = self.get_layout_button_props("menu", "test5", tab="gameplay") or {"name":"test5","rect":[200,100,100,50],"color":[200,50,100],"text":"test5","location":[0,0]}
        gameplay_buttons = {
            "test5": Button(props_test5, self.game_manager.screen, self.game_manager.game_font, self.game_manager)
        } 
        
        return {
            "tabs": tabs,
            "gameplay": gameplay_buttons,
            "audio": audio_buttons,
            "graphics": graphics_buttons,
            "accessibility": accessability_buttons,
            "input": input_buttons
        }
    
    # - CREAT SLIDERS -#

    def create_sliders(self):
        return {
            "main_menu": {},
            "setup": self.create_setup_sliders(),
            "game": {},
            "menu": self.create_menu_sliders()
        }
    
    def create_setup_sliders(self) -> Dict[str, Slider]:
        """
        Create sliders for the setup.
        """
        props = self.get_layout_slider_props("setup", "player_num_slider") or {
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
        # assign callback after creation so the lambda can reference the slider instance
        player_num_slider.callback = lambda: self.set_player_num(int(player_num_slider.value))

        return {
            "player_num_slider": player_num_slider
        }
    
    def create_menu_sliders(self) -> Dict[str, Dict[str, Slider]]:
        """
        Create sliders for the menu.
        """
        # input tab sliders
        props_deadzone = self.get_layout_slider_props("menu", "deadzone", tab="input") or {"name": "deadzone", "rect": [100, 200, 300, 20], "wrapper_rect": [100, 200, 300, 20], "min_value": 0, "max_value": 1, "initial_value": 0.1, "bar_color": [0, 100, 0], "handle_color": [100, 0, 0], "handle_radius": 10}
        props_controller_sens = self.get_layout_slider_props("menu", "controller_sensitivity", tab="input") or {"name": "controller_sensitivity", "rect": [100, 300, 300, 20], "wrapper_rect": [100, 300, 300, 20], "min_value": 0, "max_value": 10, "initial_value": 5, "bar_color": [0, 100, 0], "handle_color": [100, 0, 0], "handle_radius": 10}
        props_controller_vib = self.get_layout_slider_props("menu", "controller_vibration_strength", tab="input") or {"name": "controller_vibration_strength", "rect": [100, 400, 300, 20], "wrapper_rect": [100, 400, 300, 20], "min_value": 0, "max_value": 1, "initial_value": 0.5, "bar_color": [0, 100, 0], "handle_color": [100, 0, 0], "handle_radius": 10}

        input_sliders = {
            "deadzone": Slider(props_deadzone, props_deadzone.get("initial_value", 0.1), self.game_manager, None),
            "controller_sensitivity": Slider(props_controller_sens, props_controller_sens.get("initial_value", 5), self.game_manager, None),
            "controller_vibration_strength": Slider(props_controller_vib, props_controller_vib.get("initial_value", 0.5), self.game_manager, None)
        }
        accessability_sliders = {}
        props_brightness = self.get_layout_slider_props("menu", "brightness", tab="graphics") or {"name": "brightness", "rect": [100, 200, 300, 20], "wrapper_rect": [100, 200, 300, 20], "min_value": 0, "max_value": 1, "initial_value": 0.5, "bar_color": [0,100,0], "handle_color": [100,0,0], "handle_radius": 10}
        graphics_sliders = {
            "brightness": Slider(props_brightness, props_brightness.get("initial_value", 0.5), self.game_manager, None)
        }
        props_master = self.get_layout_slider_props("menu", "master_volume", tab="audio") or {"name": "master_volume", "rect": [100,200,300,20], "wrapper_rect": [100,200,300,20], "min_value": 0, "max_value": 1, "initial_value": 0.5, "bar_color": [0,100,0], "handle_color": [100,0,0], "handle_radius": 10}
        props_music = self.get_layout_slider_props("menu", "music_volume", tab="audio") or {"name": "music_volume", "rect": [100,300,300,20], "wrapper_rect": [100,300,300,20], "min_value": 0, "max_value": 1, "initial_value": 0.5, "bar_color": [0,100,0], "handle_color": [100,0,0], "handle_radius": 10}
        props_sfx = self.get_layout_slider_props("menu", "sfx_volume", tab="audio") or {"name": "sfx_volume", "rect": [100,400,300,20], "wrapper_rect": [100,400,300,20], "min_value": 0, "max_value": 1, "initial_value": 0.5, "bar_color": [0,100,0], "handle_color": [100,0,0], "handle_radius": 10}

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
        

    # - CREATE TOGGLES - #

    def create_toggles(self):
        return {
            "main_menu": {},
            "setup": {},
            "game": {},
            "menu": self.create_menu_toggles()
        }
    
    def create_menu_toggles(self) -> Dict[str, Dict[str, Toggle]]:
        default_time_to_flip = 0.25
        default_height = 50
        default_center_width = 100
        default_fill_color = (0, 100, 0)
        default_toggle_color = (100, 0, 0)
        default_toggle_gap = 7
        default_on = False
        default_guiding_lines = True
        #Create toggles for the menu.
        
        input_toggles = {
            "controller_vibration": Toggle(
                0,
                time_to_flip=default_time_to_flip,
                location=(100, 300),
                height=default_height,
                center_width=default_center_width,
                fill_color=default_fill_color,
                toggle_color=default_toggle_color,
                toggle_gap=default_toggle_gap,
                toggle_name="controller_vibration",
                game_manager=self.game_manager,
                on=default_on,
                guiding_lines=default_guiding_lines,
                callback=None,
            ),
            "invert_y_axis": Toggle(
                0,
                time_to_flip=default_time_to_flip,
                location=(200, 300),
                height=default_height,
                center_width=default_center_width,
                fill_color=default_fill_color,
                toggle_color=default_toggle_color,
                toggle_gap=default_toggle_gap,
                toggle_name="controller_vibration",
                game_manager=self.game_manager,
                on=default_on,
                guiding_lines=default_guiding_lines,
                callback=None,
            ),
            "invert_x_axis": Toggle(
                0,
                time_to_flip=default_time_to_flip,
                location=(300, 300),
                height=default_height,
                center_width=default_center_width,
                fill_color=default_fill_color,
                toggle_color=default_toggle_color,
                toggle_gap=default_toggle_gap,
                toggle_name="controller_vibration",
                game_manager=self.game_manager,
                on=default_on,
                guiding_lines=default_guiding_lines,
                callback=None,
            )
        }
        accessability_toggles = {
            "high_contrast_mode": Toggle(
                0,
                time_to_flip=default_time_to_flip,
                location=(100, 300),
                height=default_height,
                center_width=default_center_width,
                fill_color=default_fill_color,
                toggle_color=default_toggle_color,
                toggle_gap=default_toggle_gap,
                toggle_name="controller_vibration",
                game_manager=self.game_manager,
                on=default_on,
                guiding_lines=default_guiding_lines,
                callback=None,
            )
        }
        graphics_toggles = {
            "aa": Toggle(
                0,
                time_to_flip=default_time_to_flip,
                location=(200, 300),
                height=default_height,
                center_width=default_center_width,
                fill_color=default_fill_color,
                toggle_color=default_toggle_color,
                toggle_gap=default_toggle_gap,
                toggle_name="controller_vibration",
                game_manager=self.game_manager,
                on=default_on,
                guiding_lines=default_guiding_lines,
                callback=None,
            ),
            "fullscreen": Toggle(
                0,
                time_to_flip=default_time_to_flip,
                location=(300, 300),
                height=default_height,
                center_width=default_center_width,
                fill_color=default_fill_color,
                toggle_color=default_toggle_color,
                toggle_gap=default_toggle_gap,
                toggle_name="controller_vibration",
                game_manager=self.game_manager,
                on=default_on,
                guiding_lines=default_guiding_lines,
                callback=None,
            ),
            "shadows": Toggle(
                0,
                time_to_flip=default_time_to_flip,
                location=(400, 300),
                height=default_height,
                center_width=default_center_width,
                fill_color=default_fill_color,
                toggle_color=default_toggle_color,
                toggle_gap=default_toggle_gap,
                toggle_name="controller_vibration",
                game_manager=self.game_manager,
                on=default_on,
                guiding_lines=default_guiding_lines,
                callback=None,
            )
        }
        audio_toggles = {
            "sfx": Toggle(
                0,
                time_to_flip=default_time_to_flip,
                location=(100, 300),
                height=default_height,
                center_width=default_center_width,
                fill_color=default_fill_color,
                toggle_color=default_toggle_color,
                toggle_gap=default_toggle_gap,
                toggle_name="controller_vibration",
                game_manager=self.game_manager,
                on=default_on,
                guiding_lines=default_guiding_lines,
                callback=None,
            )
        }
        gameplay_toggles = {
            "hud": Toggle(
                0,
                time_to_flip=default_time_to_flip,
                location=(100, 300),
                height=default_height,
                center_width=default_center_width,
                fill_color=default_fill_color,
                toggle_color=default_toggle_color,
                toggle_gap=default_toggle_gap,
                toggle_name="controller_vibration",
                game_manager=self.game_manager,
                on=default_on,
                guiding_lines=default_guiding_lines,
                callback=None,
            ),
            "language": Toggle(
                0,
                time_to_flip=default_time_to_flip,
                location=(200, 300),
                height=default_height,
                center_width=default_center_width,
                fill_color=default_fill_color,
                toggle_color=default_toggle_color,
                toggle_gap=default_toggle_gap,
                toggle_name="controller_vibration",
                game_manager=self.game_manager,
                on=default_on,
                guiding_lines=default_guiding_lines,
                callback=None,
            )
        }
        return {
            "input": input_toggles,
            "accessibility": accessability_toggles,
            "graphics": graphics_toggles,
            "audio": audio_toggles,
            "gameplay": gameplay_toggles
        }
    
    # - CREATE IMAGES - #

    def create_images(self) -> Dict[str, Dict[str, Image]]:
        return {
            "main_menu": {},
            "setup": {},
            "game": self.create_game_images(),
            "menu": {}
        }

    def create_game_images(self) -> Dict[str, Image]:
        """
        Create images for the menu.
        """
        buy_background_image = Image(self.game_manager, "buy_background_image", pygame.Rect(self.game_manager.screen_w / 2, 650, self.game_manager.screen_w / 3, 100))

        return {
            "buy_background_image": buy_background_image
        }
        

    # - CREATE TEXT DISPLAYS - #

    def create_text_displays(self):
        return {
            "main_menu": {},
            "setup": self.create_setup_text_displays(),
            "game": self.create_game_text_displays(),
            "menu": self.create_menu_text_displays()
        }
    
    def create_setup_text_displays(self) -> Dict[str, TextDisplay]:
        player_num_text = TextDisplay(
            name="player_num_text",
            text="Number of Players: ", 
            font=self.game_manager.game_font,
            text_color=(0, 0, 0),
            rect=pygame.Rect(100, 150, 300, 50),
            game_manager=self.game_manager
        )
        return {
            "player_num_text": player_num_text
        }

    def create_game_text_displays(self) -> Dict[str, TextDisplay]:
        return {}

    def create_menu_text_displays(self) -> Dict[str, Dict[str, TextDisplay]]:
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