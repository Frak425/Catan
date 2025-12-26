import pygame
from typing import Dict
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_manager import GameManager
    from graphics_manager import GraphicsManager
    from helper_manager import HelperManager
    from src.managers.audio_manager import AudioManager
    from src.managers.player_manager import PlayerManager

# Import the new handler classes
from src.managers.input.helper.mouse_input_handler import MouseInputHandler
from src.managers.input.helper.keyboard_input_handler import KeyboardInputHandler
from src.managers.input.helper.dev_mode_handler import DevModeHandler
from src.managers.input.helper.ui_factory import UIFactory


class InputManager:
    """
    Main input manager that coordinates between specialized handler classes.
    """
    
    def init(self):
        # Initialize handler classes
        self.mouse_handler = MouseInputHandler()
        self.keyboard_handler = KeyboardInputHandler()
        self.dev_mode_handler = DevModeHandler()

        #initialize ui elements, can call again to update ui
        self.reset_ui()

        self.mouse_handler.set_managers(self.game_manager, self.graphics_manager, self.helper_manager)

        # Set up mouse handler with required managers
        self.keyboard_handler.set_managers(self.game_manager, self.graphics_manager, self.audio_manager, self.mouse_handler)
        self.keyboard_handler.set_dev_mode_handler(self.dev_mode_handler)
        # Set up dev mode handler
        self.dev_mode_handler.set_managers(self.game_manager, self.mouse_handler, self)

    def reset_ui(self):
        self.ui_factory = UIFactory(self.game_manager, input_manager=self)
        # Create all UI elements using the factory
        callbacks = self._create_callbacks()
        self.buttons = self.ui_factory.create_all_buttons(callbacks)
        self.toggles = self.ui_factory.create_all_toggles(callbacks)
        self.sliders = self.ui_factory.create_all_sliders(callbacks)
        self.images = self.ui_factory.create_all_images(callbacks)
        self.text_displays = self.ui_factory.create_all_text_displays(callbacks)
        self.menu = self.ui_factory.create_menu(self.buttons["menu"], self.toggles["menu"], self.sliders["menu"], self.images["menu"], self.text_displays["menu"])
        self.graphics_manager.set_ui_by_type()
        
        # Update mouse handler with new UI elements (if mouse_handler exists)
        if hasattr(self, 'mouse_handler'):
            self.mouse_handler.set_ui_elements(self.buttons, self.toggles, self.sliders, self.images, self.text_displays, self.menu)
        
        # Update graphics manager's UI references (if graphics_manager exists)
        if hasattr(self, 'graphics_manager') and hasattr(self.graphics_manager, 'ui_by_type'):
            self.graphics_manager.ui_by_type = {
                "buttons": self.buttons,
                "images": self.images,
                "text_displays": self.text_displays,
                "sliders": self.sliders,
                "toggles": self.toggles
            }
        
        # Initialize UI elements
        self.initialize_ui_elements()

    def handle_input(self, x: int, y: int, event_type: int) -> None:
        """Delegate mouse input handling to MouseInputHandler."""
        self.mouse_handler.handle_mouse_input(x, y, event_type)

    def handle_keyboard(self, key: int) -> None:
        """Delegate keyboard input handling to KeyboardInputHandler."""
        # Special handling for escape to close menu
        if key == pygame.K_ESCAPE and self.graphics_manager.menu_open:
            self.close_menu()
            return
        
        self.keyboard_handler.handle_keyboard(key)

    def _create_callbacks(self) -> Dict:
        """Create a dictionary of all callback functions for UI elements."""
        return {
            # Main menu callbacks
            'set_game_state_setup': lambda: self.set_game_state("setup"),
            'set_game_state_home': lambda: self.set_game_state("home"),
            'quit': self.quit,
            
            # Setup screen callbacks
            'start_game': self.start_game,
            'choose_player_color_cycle': self.choose_player_color_cycle,
            'set_diff_level_easy': lambda: self.set_diff_level("easy"),
            'set_diff_level_medium': lambda: self.set_diff_level("medium"),
            'set_diff_level_hard': lambda: self.set_diff_level("hard"),
            'open_menu': self.open_menu,
            'close_menu': self.close_menu,
            'set_player_num': self.set_player_num,
            
            # Menu tab callbacks
            'change_tab_input': lambda: self.change_tab("input"),
            'change_tab_accessibility': lambda: self.change_tab("accessibility"),
            'change_tab_gameplay': lambda: self.change_tab("gameplay"),
            'change_tab_audio': lambda: self.change_tab("audio"),
            'change_tab_graphics': lambda: self.change_tab("graphics"),
        }

    ## --- EVENT FUNCTIONS --- ##
    
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

    def set_diff_level(self, level: str):
        # TODO: Implement
        pass

    def start_game(self):
        self.game_manager.game_state = "init"

    def open_menu(self):
        self.menu.open_menu()
        self.graphics_manager.menu_open = True
        self.buttons["setup"]["open_menu"].hide()

    def close_menu(self):
        self.menu.close_menu()
        self.graphics_manager.menu_open = False
        self.buttons["setup"]["open_menu"].show()

    def set_game_state(self, state: str):
        self.game_manager.game_state = state

    def change_tab(self, new_tab):
        self.menu.active_tab = new_tab
        self.buttons["menu"]["tabs"][new_tab].color = (0, 100, 0)  # Highlight the active tab
        for tab_name, button in self.buttons["menu"]["tabs"].items():
            if tab_name != new_tab:
                button.color = (100, 0, 0)
        self.menu.update_menu(0)

    def quit(self):
        self.game_manager.running = False

    ## --- MANAGER SETTERS --- ##

    def set_game_manager(self, game_manager: 'GameManager') -> None:
        self.game_manager = game_manager

    def set_graphics_manager(self, graphics_manager: 'GraphicsManager') -> None:
        self.graphics_manager = graphics_manager
        
    def set_helper_manager(self, helper_manager: 'HelperManager') -> None:
        self.helper_manager = helper_manager

    def set_player_manager(self, player_manager: 'PlayerManager') -> None:
        self.player_manager = player_manager 

    def set_audio_manager(self, audio_manager: 'AudioManager') -> None:
        self.audio_manager = audio_manager
        # Set up keyboard handler with required managers
    
    def initialize_ui_elements(self) -> None:
        # Initialize any UI elements that require setup after creation
        # Call the callback for setup player number slider to set initial UI text
        player_num_slider = self.sliders["setup"]["player_num_slider"]
        if hasattr(player_num_slider, 'callback') and player_num_slider.callback:
            player_num_slider.callback()

        self.change_tab("input")  # Set the initial active tab
