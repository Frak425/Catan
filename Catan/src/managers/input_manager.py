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
        
        #Handlers abstract the effects of all buttons
        #EX. "button_name_here": self.function_defined_below, all button names corrospond to some handler
        #When adding buttons, make sure to add their handlers here
        self.main_menu_handlers = {
            "play": lambda: self.set_game_state("setup"),
            "quit": self.quit
        }
        self.setup_handlers = {
            "player_num_increase": self.player_num_increase,
            "player_num_decrease": self.player_num_decrease,
            "player_num_slider": lambda: self.set_player_num(self.sliders["setup"]["player_num_slider"].value),
            "player_choose_color_cycle": self.choose_player_color_cycle,
            "difficulty_level_easy": lambda:  self.set_diff_level("easy"),
            "difficulty_level_medium": lambda:  self.set_diff_level("medium"),
            "difficulty_level_hard": lambda:  self.set_diff_level("hard"),
            "game_start": self.start_game,
            "open_menu": self.open_menu,
            "game_setup_back": lambda: self.set_game_state("main_menu"),
        }
        self.game_handlers = {
            "settings_menu": self.open_menu,
            "back": lambda: self.set_game_state("main_menu")
        }
        self.menu_handlers = {
            "close_menu": self.close_menu,
            "input": lambda: self.change_tab("input"),
            "accessibility": lambda: self.change_tab("accessibility"),
            "gameplay": lambda: self.change_tab("gameplay"),  
            "audio": lambda: self.change_tab("audio"),
            "graphics": lambda: self.change_tab("graphics"),
        }
        self.game_over_handlers = {}
        self.handlers_by_state: dict[str, dict] = {
            "main_menu": self.main_menu_handlers,
            "setup": self.setup_handlers,
            "game": self.game_handlers,
            "game_over": self.game_over_handlers,
            "menu": self.menu_handlers
        }

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
            if self.dragging and self.active.__class__.__name__ == "Slider":
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
        if self.graphics_manager.menu_open:
            
            if pygame.rect.Rect.collidepoint(pygame.Rect(self.active.rect.x + self.game_manager.menu_margins[0], self.active.rect.y + self.game_manager.menu_margins[1], self.active.rect.w, self.active.rect.h), (x, y)):
                self.handler = self.handlers_by_state["menu"].get(self.active.name)
            if isinstance(self.active, Toggle):
                self.active.set_animating(self.graphics_manager.time)

        else:
            if pygame.rect.Rect.collidepoint(self.active.rect, (x, y)):
                self.handler = self.handlers_by_state[state].get(self.active.name)

            if isinstance(self.active, Toggle):
                self.active.set_animating(self.graphics_manager.time)


        if self.handler:
            self.handler()
    
    def handle_drag(self, x: int, y: int, sliders: Dict[str, Slider]) -> None:
        for slider in sliders.values():
            if slider == self.active:
                slider.update_location(x, y)

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
    
    def create_menu(self) -> Menu:
        menu = Menu(self.game_manager.screen, self.game_manager.game_font, "static", self.buttons['menu'], self.toggles["menu"], self.sliders["menu"], self.game_manager.menu_size, self.game_manager.init_location, self.game_manager.final_location, bckg_color=self.game_manager.menu_background_color)
        return menu
    
    def initialize_ui_elements(self) -> None:
        # Initialize any UI elements that require setup after creation
        self.handlers_by_state["setup"]["player_num_slider"]()  # Set initial player number text

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
        play_button = Button((0, 100, 0), "PLAY", pygame.rect.Rect(self.game_manager.screen_w / 2 - self.game_manager.play_button_width / 2, self.game_manager.screen_h / 2 - self.game_manager.play_button_height / 1.75, self.game_manager.play_button_width, self.game_manager.play_button_height), "play", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        quit_button = Button((100, 0, 0), "QUIT", pygame.rect.Rect(self.game_manager.screen_w / 2 - self.game_manager.play_button_width / 2, self.game_manager.screen_h / 2 + self.game_manager.play_button_height / 1.75, self.game_manager.play_button_width, self.game_manager.play_button_height), "quit", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        return {
            "play_button": play_button, 
            "quit_button": quit_button
        }

    def create_setup_buttons(self) -> Dict[str, Button]:
        #create game setup buttons
        game_setup_back_button = Button((100, 0, 0), "Back", pygame.Rect(self.game_manager.screen_w / 4 - self.game_manager.play_button_width / 2, self.game_manager.screen_h / 2, 200, 100), "game_setup_back", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        game_start_button = Button((100, 0, 0), "Start", pygame.Rect(self.game_manager.screen_w / 4 * 3 - self.game_manager.game_start_button_width / 2, self.game_manager.screen_h / 8 * 6, self.game_manager.game_start_button_width, self.game_manager.game_start_button_height), "game_start", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        
        #TODO: decide on player_num being changed by button or slider
        #player_num_increase_button = Button((0, 100, 0), "+", pygame.Rect(self.game_manager.screen_w / 4 - self.game_manager.player_number_incease_decrease_button_size / 2 + 100, self.game_manager.screen_h / 4 * 2.5, self.game_manager.player_number_incease_decrease_button_size, self.game_manager.player_number_incease_decrease_button_size), "player_num_increase", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        #player_num_decrease_button = Button((0, 100, 0), "-", pygame.Rect(self.game_manager.screen_w / 4 - self.game_manager.player_number_incease_decrease_button_size / 2 - 100, self.game_manager.screen_h / 4 * 2.5, self.game_manager.player_number_incease_decrease_button_size, self.game_manager.player_number_incease_decrease_button_size), "player_num_decrease", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        
        player_choose_color_cycle_button = Button((0, 0, 0), "->", pygame.Rect(10, 10, 10, 10), "player_choose_color_cycle", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        
        difficulty_level_easy_button = Button((0, 0, 0), "easy", pygame.Rect(10, 10, 10, 10), "difficulty_level_easy", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        difficulty_level_medium_button = Button((0, 0, 0), "medium", pygame.Rect(10, 10, 10, 10), "difficulty_level_medium", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        difficulty_level_hard_button = Button((0, 0, 0), "hard", pygame.Rect(10, 10, 10, 10), "difficulty_level_hard", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        
        open_menu_button = Button((100, 0, 0), "image", pygame.Rect(self.game_manager.screen_w - self.game_manager.settings_open_button_offset - self.game_manager.settings_open_button_size, self.game_manager.settings_open_button_offset, self.game_manager.settings_open_button_size, self.game_manager.settings_open_button_size), "open_menu", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        
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
        back_button = Button((100, 100, 200), "back", pygame.Rect(10, 10, 70, 40), "back", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)

        board_buy_settlement_button = Button((0, 0, 0), "image", pygame.Rect(700, 650, 40, 40), "board_buy_settlement", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        board_buy_city_button = Button((0, 0, 0), "image", pygame.Rect(800, 650, 40, 40), "board_buy_city", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        board_buy_road_button = Button((0, 0, 0), "image", pygame.Rect(900, 10, 10, 40), "board_buy_road", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        board_buy_development_button = Button((0, 0, 0), "image", pygame.Rect(1000, 40, 40, 40), "board_buy_development", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        board_roll_dice_button = Button((0, 0, 0), "image", pygame.Rect(1050, 600, 40, 40), "board_roll_dice", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        settings_menu_button = Button((100, 0, 0), "image", pygame.Rect(self.game_manager.screen_w - self.game_manager.settings_open_button_offset - self.game_manager.settings_open_button_size, self.game_manager.settings_open_button_offset, self.game_manager.settings_open_button_size, self.game_manager.settings_open_button_size), "settings_menu", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        
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
                Button((100, 0, 0), "Input", 
                    pygame.rect.Rect(
                        300, 
                        self.game_manager.menu_tab_margin_top, 
                        self.game_manager.menu_input_tab_size[0], 
                        self.game_manager.menu_input_tab_size[1]
                    ), 
                    "input", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager
                ),
            "accessibility": 
                Button((100, 0, 0), "Accessibility", 
                    pygame.rect.Rect(
                        400, 
                        self.game_manager.menu_tab_margin_top, 
                        self.game_manager.menu_accessibility_tab_size[0], 
                        self.game_manager.menu_accessibility_tab_size[1]
                    ), 
                    "accessibility", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager
                ),
            "gameplay": 
                Button((100, 0, 0), "Gameplay", 
                    pygame.rect.Rect(
                        self.game_manager.menu_size[0] / 2 - self.game_manager.menu_gameplay_tab_size[0] / 2, 
                        self.game_manager.menu_tab_margin_top, 
                        self.game_manager.menu_gameplay_tab_size[0], 
                        self.game_manager.menu_gameplay_tab_size[1]
                    ), "gameplay", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager
                ),
            "audio": 
                Button((100, 0, 0), "Audio", 
                    pygame.rect.Rect(
                        700, 
                        self.game_manager.menu_tab_margin_top, 
                        self.game_manager.menu_audio_tab_size[0], 
                        self.game_manager.menu_audio_tab_size[1]
                    ), "audio", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager
                ),
            "graphics": 
                Button((100, 0, 0), "Graphics", 
                    pygame.rect.Rect(
                        800, 
                        self.game_manager.menu_tab_margin_top, 
                        self.game_manager.menu_graphics_tab_size[0], 
                        self.game_manager.menu_graphics_tab_size[1]
                    ), "graphics", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager
                ),
            "close_menu": 
                Button((100, 0, 0), "Close", 
                    pygame.rect.Rect(
                        self.game_manager.menu_size[0] - self.game_manager.close_menu_size[0] - self.game_manager.close_menu_margins[0],
                        self.game_manager.close_menu_margins[1], 
                        self.game_manager.close_menu_size[0], 
                        self.game_manager.close_menu_size[1]
                    ), "close_menu", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager
                )
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
        input_buttons = {
            "test1": Button((200, 50, 100), "test1", pygame.rect.Rect(200, 100, 100, 50), "test1", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        }

    
        """
        accessability:
        -Colorblind mode: deuteranopia, protanopia, and tritanopia (multi-choice select box)
        -Font Size: small, medium, large (multi-choice select box)
        -High contrast mode (toggle)
        -TTS: Hesitant to implement because limited usage and maximal time to produce
        """
        #TODO: fill with buttons
        accessability_buttons = {
            "test2": Button((200, 50, 100), "test2", pygame.rect.Rect(200, 100, 100, 50), "test2", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
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
        graphics_buttons = {
            "test3": Button((200, 50, 100), "test3", pygame.rect.Rect(200, 100, 100, 50), "test3", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        }

    
        """
        Audio:
        -Master (slider)
        -Music (slider)
        -SFX (toggle)
        """
        #TODO: fill with buttons
        audio_buttons = {
            "test4": Button((200, 50, 100), "test4", pygame.rect.Rect(200, 100, 100, 50), "test4", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
        }

    
        """
        Gameplay:
        -HUD (ask ChatGPT)
        -Language (multi-choice select box)
        """ 
        #TODO: fill with buttons
        gameplay_buttons = {
            "test5": Button((200, 50, 100), "test5", pygame.rect.Rect(200, 100, 100, 50), "test5", self.game_manager.screen, self.game_manager.game_font, (0, 0), self.game_manager)
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
        player_num_slider = Slider(
            name="player_num_slider",
            wrapper_rect=pygame.Rect(100, 200, 300, 20),
            rect=pygame.Rect(100, 200, 300, 20),
            min_value=1,
            max_value=4,
            initial_value=self.game_manager.players_num,
            bar_color=(0, 100, 0),
            handle_color=(100, 0, 0),
            handle_radius=10,
            game_manager= self.game_manager,
            bar_image=None
        )
        return {
            "player_num_slider": player_num_slider
        }
    
    def create_menu_sliders(self) -> Dict[str, Dict[str, Slider]]:
        """
        Create sliders for the menu.
        """
        input_sliders = {
            "deadzone": Slider(
                name="deadzone",
                wrapper_rect=pygame.Rect(100, 200, 300, 20),
                rect=pygame.Rect(100, 200, 300, 20),
                min_value=0,
                max_value=1,
                initial_value=0.1,
                bar_color=(0, 100, 0),
                handle_color=(100, 0, 0),
                handle_radius=10,
                game_manager= self.game_manager,
                bar_image=None
            ),
            "controller_sensitivity": Slider(
                name="controller_sensitivity",
                wrapper_rect=pygame.Rect(100, 300, 300, 20),
                rect=pygame.Rect(100, 300, 300, 20),
                min_value=0,
                max_value=10,
                initial_value=5,
                bar_color=(0, 100, 0),
                handle_color=(100, 0, 0),
                handle_radius=10,
                game_manager= self.game_manager,
                bar_image=None
            ),
            "controller_vibration_strength": Slider(
                name="controller_vibration_strength",
                wrapper_rect=pygame.Rect(100, 400, 300, 20),
                rect=pygame.Rect(100, 400, 300, 20),
                min_value=0,
                max_value=1,
                initial_value=0.5,
                bar_color=(0, 100, 0),
                handle_color=(100, 0, 0),
                handle_radius=10,
                game_manager= self.game_manager,
                bar_image=None
            )
        }
        accessability_sliders = {}
        graphics_sliders = {
            "brightness": Slider(
                name="brightness",
                wrapper_rect=pygame.Rect(100, 200, 300, 20),
                rect=pygame.Rect(100, 200, 300, 20),
                min_value=0,
                max_value=1,
                initial_value=0.5,
                bar_color=(0, 100, 0),
                handle_color=(100, 0, 0),
                handle_radius=10,
                game_manager= self.game_manager,
                bar_image=None
            )
        }
        audio_sliders = {
            "master_volume": Slider(
                name="master_volume",
                wrapper_rect=pygame.Rect(100, 200, 300, 20),
                rect=pygame.Rect(100, 200, 300, 20),
                min_value=0,
                max_value=1,
                initial_value=0.5,
                bar_color=(0, 100, 0),
                handle_color=(100, 0, 0),
                handle_radius=10,
                game_manager= self.game_manager,
                bar_image=None
            ),
            "music_volume": Slider(
                name="music_volume",
                wrapper_rect=pygame.Rect(100, 300, 300, 20),
                rect=pygame.Rect(100, 300, 300, 20),
                min_value=0,
                max_value=1,
                initial_value=0.5,
                bar_color=(0, 100, 0),
                handle_color=(100, 0, 0),
                handle_radius=10,
                game_manager= self.game_manager,
                bar_image=None
            ),
            "sfx_volume": Slider(
                name="sfx_volume",
                wrapper_rect=pygame.Rect(100, 400, 300, 20),
                rect=pygame.Rect(100, 400, 300, 20),
                min_value=0,
                max_value=1,
                initial_value=0.5,
                bar_color=(0, 100, 0),
                handle_color=(100, 0, 0),
                handle_radius=10,
                game_manager= self.game_manager,
                bar_image=None
            )
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