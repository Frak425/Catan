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
from src.ui.elements.menu import Menu
from src.managers.input.helper.mouse_input_handler import MouseInputHandler
from src.managers.input.helper.keyboard_input_handler import KeyboardInputHandler
from src.managers.input.helper.dev_mode_handler import DevModeHandler
from src.managers.input.helper.ui_factory import UIFactory
from src.managers.animation.animation_manager import AnimationManager
from src.ui.elements.scrollable_area import ScrollableArea


class InputManager:
    """
    Coordinates user input handling and manages all UI elements.
    
    Responsibilities:
    - Delegate mouse and keyboard input to specialized handlers
    - Create and manage UI elements (buttons, sliders, toggles, menus)
    - Handle menu opening/closing with exclusivity rules
    - Manage game state transitions via UI callbacks
    - Coordinate between input handlers, UI factory, and other managers
    
    Architecture:
    - Uses composition pattern with MouseInputHandler, KeyboardInputHandler, DevModeHandler
    - UIFactory creates all UI elements from layout config
    - Callbacks registered in _create_callbacks() connect UI actions to game logic
    """
    
    def init(self):
        """
        Initialize input handling subsystems and create UI elements.
        
        Setup order:
        1. Create input handler instances (mouse, keyboard, dev mode)
        2. Create all UI elements via reset_ui()
        3. Wire up dependencies between handlers and managers
        
        Note: Depends on game_manager.layout being loaded before calling this.
        """
        # Create input handler instances
        self.mouse_handler = MouseInputHandler()
        self.keyboard_handler = KeyboardInputHandler()
        self.dev_mode_handler = DevModeHandler()

        # Create UI elements from layout config
        self.reset_ui()

        # Wire up handler dependencies
        self.mouse_handler.set_managers(self.game_manager, self.graphics_manager, self.helper_manager)
        self.keyboard_handler.set_managers(self.game_manager, self.graphics_manager, self.audio_manager, self.mouse_handler)
        self.keyboard_handler.set_dev_mode_handler(self.dev_mode_handler)
        self.dev_mode_handler.set_managers(self.game_manager, self.mouse_handler, self)

    def reset_ui(self):
        """
        Create/recreate all UI elements from layout configuration.
        
        Can be called multiple times to refresh UI after config changes.
        
        Process:
        1. Create UIFactory with game_manager and callback registry
        2. Generate all UI elements (buttons, sliders, toggles, etc.) from layout
        3. Create menus with their nested UI elements
        4. Update references in graphics_manager and mouse_handler
        5. Initialize special UI elements (e.g., player number display)
        """
        # Create factory for building UI from config
        self.ui_factory = UIFactory(self.game_manager, input_manager=self)
        
        # Build callback registry for UI actions
        callbacks = self._create_callbacks()
        animations = self.game_manager.animation_manager.animations
        
        # Create all UI element collections from layout config
        self.buttons = self.ui_factory.create_all_buttons(callbacks, animations)
        self.toggles = self.ui_factory.create_all_toggles(callbacks, animations)
        self.sliders = self.ui_factory.create_all_sliders(callbacks, animations)
        self.images = self.ui_factory.create_all_images(callbacks, animations)
        self.text_displays = self.ui_factory.create_all_text_displays(callbacks, animations)
        self.scrollable_areas = self.ui_factory.create_all_scrollable_areas(callbacks, animations)
        self.menus = self.ui_factory.create_all_menus(
            #TODO: update for newer implemtation
            self.buttons["menu"], 
            self.toggles["menu"], 
            self.sliders["menu"], 
            self.images["menu"], 
            self.text_displays["menu"]
        )
        
        # Update graphics_manager's UI references for rendering
        self.graphics_manager.set_ui_by_type()
        
        # Update mouse_handler with new UI elements (if it exists)
        if hasattr(self, 'mouse_handler'):
            self.mouse_handler.set_ui_elements(
                self.buttons, self.toggles, self.sliders, 
                self.images, self.text_displays, 
                self.scrollable_areas, self.menus
            )
        
        # Update graphics_manager's UI type dictionary (if it exists)
        if hasattr(self, 'graphics_manager') and hasattr(self.graphics_manager, 'ui_by_type'):
            self.graphics_manager.ui_by_type = {
                "buttons": self.buttons,
                "images": self.images,
                "text_displays": self.text_displays,
                "sliders": self.sliders,
                "toggles": self.toggles,
                "scrollable_areas": self.scrollable_areas
            }
        
        # Perform post-creation initialization for special UI elements
        self.initialize_ui_elements()

    ## --- INPUT DELEGATION --- ##

    def handle_input(self, x: int, y: int, event_type: int) -> None:
        """
        Route mouse input to MouseInputHandler.
        
        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate  
            event_type: pygame event type (MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP)
        """
        self.mouse_handler.handle_mouse_input(x, y, event_type)

    def handle_keyboard(self, key: int) -> None:
        """
        Route keyboard input to KeyboardInputHandler.
        
        Special case: ESC key closes the topmost open menu before delegating.
        
        Args:
            key: pygame key constant (e.g., pygame.K_ESCAPE, pygame.K_SPACE)
        """
        # Handle ESC to close topmost menu
        if key == pygame.K_ESCAPE:
            open_menus = self.get_open_menus()
            if open_menus:
                # TODO: Make this configurable - some menus should not close on ESC
                # Close the topmost menu (lowest z_index = on top)
                topmost_menu = min(open_menus, key=lambda m: m.z_index)
                self.close_menu_by_name(topmost_menu.name)
                return
        
        self.keyboard_handler.handle_keyboard(key)

    ## --- CALLBACK REGISTRY --- ##

    def _create_callbacks(self) -> Dict:
        """
        Create registry mapping callback names to functions.
        
        These callbacks are assigned to UI elements when they're created from layout config.
        The layout JSON stores callback names as strings, and this registry resolves
        them to actual callable functions.
        
        Returns:
            Dict: Mapping of callback name strings to functions
            
        NOTE: update as needed when adding new UI elements with callbacks.
        Callback categories:
        - Navigation: set_game_state_*, change_tab_*
        - Game setup: start_game, set_player_num, set_diff_level_*
        - Menu control: open_menu, close_menu
        - Player config: choose_player_color_cycle
        - System: quit
        """
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

    ## --- GAME SETUP & PLAYER CONFIGURATION --- ##
    
    def player_num_increase(self):
        """Increment number of players (max 4)."""
        if (self.game_manager.players_num < 4):
            self.game_manager.players_num += 1

    def player_num_decrease(self):
        """Decrement number of players (min 2)."""
        if (self.game_manager.players_num > 2):
            self.game_manager.players_num -= 1

    def set_player_num(self, num: int) -> None:
        """
        Set number of players and update UI display.
        
        Args:
            num: Number of players (2-4)
        """
        self.game_manager.players_num = num
        self.text_displays["setup"]["player_num_text"].update_text(f"Number of Players: {num}")

    def choose_player_color_cycle(self):
        """Cycle through available player colors."""
        self.game_manager.player_color_chosen_index += 1
        self.game_manager.player_color_chosen_index %= len(self.game_manager.player_colors)

    def set_diff_level(self, level: str):
        """
        Set game difficulty level.
        
        Args:
            level: Difficulty level ("easy", "medium", "hard")
            
        TODO: Implement difficulty logic
        """
        pass

    def start_game(self):
        """Transition from setup screen to game initialization."""
        self.game_manager.game_state = "init"

    ## --- MENU MANAGEMENT --- ##

    def open_menu(self, name: str = "settings"):
        """
        Open menu by name (wrapper for backward compatibility).
        
        Args:
            name: Menu identifier (default: "settings")
        """
        self.open_menu_by_name(name)

    def close_menu(self, name: str = "settings"):
        """
        Close menu by name (wrapper for backward compatibility).
        
        Args:
            name: Menu identifier (default: "settings")
        """
        self.close_menu_by_name(name)
    
    def get_menu(self, name: str):
        """
        Retrieve menu by name.
        
        Args:
            name: Menu identifier
            
        Returns:
            Menu object or None if not found
        """
        return self.menus.get(name)
    
    def open_menu_by_name(self, name: str) -> bool:
        """
        Open menu by name with automatic exclusivity handling.
        
        If the menu has exclusivity rules (exclusive_with list), this will
        automatically close any conflicting open menus before opening.
        
        Args:
            name: Menu identifier to open
            
        Returns:
            bool: True if menu was opened successfully, False if menu doesn't exist
        """
        menu = self.get_menu(name)
        if not menu:
            print(f"Warning: Menu '{name}' not found")
            return False
        
        # Check for exclusivity - close any menus that can't be open simultaneously
        for other_menu in self.get_open_menus():
            if other_menu.name == name:
                continue
            # Check bidirectional exclusivity
            if name in other_menu.exclusive_with or other_menu.name in menu.exclusive_with:
                other_menu.close_menu()
        
        menu.open_menu()
        
        return True
    
    def close_menu_by_name(self, name: str) -> bool:
        """
        Close menu by name.
        
        Args:
            name: Menu identifier to close
            
        Returns:
            bool: True if menu was closed successfully, False if menu doesn't exist
        """
        menu = self.get_menu(name)
        if not menu:
            print(f"Warning: Menu '{name}' not found")
            return False
        
        menu.close_menu()
        
        return True
    
    def get_open_menus(self):
        """
        Get list of all currently visible menus.
        
        Returns:
            list: Menu objects that have shown=True
        """
        return [menu for menu in self.menus.values() if menu.shown]
    
    def get_menus_by_z_index(self, reverse=False) -> list[Menu]:
        """
        Get all menus sorted by z-index for rendering order.
        
        Lower z_index = on top (rendered last, appears in front).
        
        Args:
            reverse: If True, returns bottom-to-top order (higher z first)
                    If False, returns top-to-bottom order (lower z first)
                    
        Returns:
            list[Menu]: Sorted menu objects
            
        Note: Use reverse=True for drawing (draw back-to-front)
        """
        return sorted(self.menus.values(), key=lambda m: m.z_index, reverse=reverse)
    
    def close_menus_on_state_change(self):
        """
        Close all menus marked to close on game state transitions.
        
        Iterates through all menus and closes those with close_on_state_change=True.
        Typically called before transitioning between game states (home/setup/game).
        """
        for menu in self.menus.values():
            if menu.close_on_state_change and menu.shown:
                menu.close_menu()

    ## --- STATE & TAB MANAGEMENT --- ##

    def set_game_state(self, state: str):
        """
        Change the game state.
        
        Args:
            state: New game state ("home", "setup", "game")
        """
        self.game_manager.game_state = state

    def change_tab(self, new_tab):
        """
        Change active tab in settings menu.
        
        Updates the menu's active_tab and highlights the corresponding tab button.
        
        Args:
            new_tab: Tab identifier ("input", "accessibility", "gameplay", "audio", "graphics")
            
        TODO: Generalize to support multiple menus with tabs, not just settings
        """
        settings_menu = self.get_menu("settings")
        if not settings_menu:
            print("Warning: 'settings' menu not found")
            return
        
        settings_menu.active_tab = new_tab
        
        # Check if tab buttons exist before trying to update them
        if ("menu" in self.buttons and 
            "tabs" in self.buttons["menu"] and 
            new_tab in self.buttons["menu"]["tabs"]):
            self.buttons["menu"]["tabs"][new_tab].color = (0, 100, 0)  # Highlight the active tab
            for tab_name, button in self.buttons["menu"]["tabs"].items():
                if tab_name != new_tab:
                    button.color = (100, 0, 0)
        
        settings_menu.update_menu(0)

    def quit(self):
        """Signal the game to shut down by setting running flag to False."""
        self.game_manager.running = False

    ## --- DEPENDENCY INJECTION (TODO: Replace with constructor injection) --- ##

    def set_game_manager(self, game_manager: 'GameManager') -> None:
        """Inject GameManager dependency. Used for circular dependency resolution."""
        self.game_manager = game_manager

    def set_graphics_manager(self, graphics_manager: 'GraphicsManager') -> None:
        """Inject GraphicsManager dependency. Used for circular dependency resolution."""
        self.graphics_manager = graphics_manager
        
    def set_helper_manager(self, helper_manager: 'HelperManager') -> None:
        """Inject HelperManager dependency. Used for circular dependency resolution."""
        self.helper_manager = helper_manager

    def set_player_manager(self, player_manager: 'PlayerManager') -> None:
        """Inject PlayerManager dependency. Used for circular dependency resolution."""
        self.player_manager = player_manager 

    def set_audio_manager(self, audio_manager: 'AudioManager') -> None:
        """Inject AudioManager dependency. Used for circular dependency resolution."""
        self.audio_manager = audio_manager
    
    ## --- UI ELEMENT INITIALIZATION --- ##
    
    def initialize_ui_elements(self) -> None:
        """
        Perform post-creation setup for UI elements.
        
        Called after all UI elements are created to handle any special initialization:
        - Trigger callbacks to set initial display values
        - Set default active tabs
        - Initialize element states
        """
        # Initialize any UI elements that require setup after creation
        # Call the callback for setup player number slider to set initial UI text
        if "setup" in self.sliders and "player_num_slider" in self.sliders["setup"]:
            player_num_slider = self.sliders["setup"]["player_num_slider"]
            if hasattr(player_num_slider, 'callback') and player_num_slider.callback:
                player_num_slider.callback()

        self.change_tab("input")  # Set the initial active tab
