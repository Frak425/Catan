import pygame
from typing import Dict
from typing import TYPE_CHECKING
from src.managers.base_manager import BaseManager
from src.ui.ui_element import UIElement
if TYPE_CHECKING:
    from src.managers.game.game_manager import GameManager
    from src.managers.graphics.graphics_manager import GraphicsManager
    from src.managers.helper.helper_manager import HelperManager
    from src.managers.audio.audio_manager import AudioManager
    from src.managers.player.player_manager import PlayerManager

# Import the new handler classes
from src.ui.elements.menu import Menu
from src.managers.input.helper.mouse_input_handler import MouseInputHandler
from src.managers.input.helper.keyboard_input_handler import KeyboardInputHandler
from src.managers.input.helper.dev_mode_handler import DevModeHandler
from src.managers.input.helper.ui_factory import UIFactory
from src.managers.animation.animation_manager import AnimationManager
from src.ui.elements.scrollable_area import ScrollableArea

#import ui classes for type completion
from src.ui.elements.button import Button
from src.ui.elements.toggle import Toggle
from src.ui.elements.slider import Slider


class InputManager(BaseManager):
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
    
    def __init__(self):
        super().__init__()
        
    def initialize(self) -> None:
        """Initialize manager after all dependencies are injected."""
        self.game_manager: GameManager = self.get_dependency('game_manager')
        self.graphics_manager: GraphicsManager = self.get_dependency('graphics_manager')
        self.helper_manager: HelperManager = self.get_dependency('helper_manager')
        self.audio_manager: AudioManager = self.get_dependency('audio_manager')
        self.player_manager: PlayerManager = self.get_dependency('player_manager')
        
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
        drivers = self.game_manager.driver_manager.drivers
        
        # Create all UI element collections from layout config
        self.buttons = self.ui_factory.create_all_buttons(callbacks, animations, drivers)
        self.toggles = self.ui_factory.create_all_toggles(callbacks, animations, drivers)
        self.sliders = self.ui_factory.create_all_sliders(callbacks, animations, drivers)
        self.images = self.ui_factory.create_all_images(callbacks, animations, drivers)
        self.text_displays = self.ui_factory.create_all_text_displays(callbacks, animations, drivers)
        self.scrollable_areas = self.ui_factory.create_all_scrollable_areas(callbacks, animations, drivers)
        self.menus = self.ui_factory.create_all_menus(
            self.buttons,
            self.toggles,
            self.sliders,
            self.images,
            self.text_displays
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
        - Player config: player_color_index_*, choose_player_color_cycle
        - System: quit
        """
        return {
            # Main menu callbacks
            'set_game_state_setup': lambda: self.set_game_state("setup"),
            'set_game_state_home': lambda: self.set_game_state("home"),
            'quit': self.quit,
            
            # Setup screen callbacks
            'start_game': self.start_game,
            'player_num_increase': self.player_num_increase,
            'player_num_decrease': self.player_num_decrease,
            'player_color_index_increase': self.player_color_index_increase,
            'player_color_index_decrease': self.player_color_index_decrease,
            'color_index_increase': self.player_color_index_increase,
            'color_index_decrease': self.player_color_index_decrease,
            'points_to_win_increase': self.points_to_win_increase,
            'points_to_win_decrease': self.points_to_win_decrease,
            'set_diff_level_easy': lambda: self._update_diff_level_ui("set_diff_level_easy", "set_diff_level_medium", "set_diff_level_hard"),
            'set_diff_level_medium': lambda: self._update_diff_level_ui("set_diff_level_medium", "set_diff_level_easy", "set_diff_level_hard"),
            'set_diff_level_hard': lambda: self._update_diff_level_ui("set_diff_level_hard", "set_diff_level_easy", "set_diff_level_medium"),
            'set_robber_mode_friendly': lambda: self._update_robber_mode_ui("set_robber_mode_friendly", "set_robber_mode_standard"),
            'set_robber_mode_standard': lambda: self._update_robber_mode_ui("set_robber_mode_standard", "set_robber_mode_friendly"),
            # Backward compatibility with older layout naming.
            'set_robber_mode_normal': lambda: self._update_robber_mode_ui("set_robber_mode_standard", "set_robber_mode_friendly"),
            'set_dice_mode_random': lambda: self._update_dice_mode_ui("set_dice_mode_random", "set_dice_mode_balanced"),
            'set_dice_mode_balanced': lambda: self._update_dice_mode_ui("set_dice_mode_balanced", "set_dice_mode_random"),
            'turn_order_increase': self.turn_order_increase,
            'turn_order_decrease': self.turn_order_decrease,
            'time_limit_toggle': lambda: self._update_time_limit_ui(),
            'open_menu': lambda: self.open_menu('settings'),
            'close_menu': lambda: self.close_menu('settings'),
            
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

            self._update_player_num_ui()

    def player_num_decrease(self):
        """Decrement number of players (min 2)."""
        if (self.game_manager.players_num > 2):
            self.game_manager.players_num -= 1

            self._update_player_num_ui()
    
    def set_player_num(self, num: int) -> None:
        """
        Set number of players and update UI display.
        
        Args:
            num: Number of players (2-4)
        """
        self.game_manager.players_num = num
        self.text_displays["setup"]["player_num_text"].update_text(f"Number of Players: {num}")

    def player_color_index_increase(self):
        self.game_manager.player_color_chosen_index = (self.game_manager.player_color_chosen_index + 1) % len(self.game_manager.player_colors)

        self._update_player_color_ui()
    
    def player_color_index_decrease(self):
        self.game_manager.player_color_chosen_index = (self.game_manager.player_color_chosen_index - 1) % len(self.game_manager.player_colors)

        self._update_player_color_ui()

    def points_to_win_increase(self):
        if self.game_manager.points_to_win < 13:
            self.game_manager.points_to_win += 1
            self._update_points_to_win_ui()

    def points_to_win_decrease(self):
        if self.game_manager.points_to_win > 8:
            self.game_manager.points_to_win -= 1
            self._update_points_to_win_ui()

    def turn_order_increase(self):
        self.game_manager.turn_order = (self.game_manager.turn_order % 4) + 1
        self._update_turn_order_ui()

    def turn_order_decrease(self):
        self.game_manager.turn_order = ((self.game_manager.turn_order - 2) % 4) + 1
        self._update_turn_order_ui()

    def _update_points_to_win_ui(self) -> None:
        min_points = 8
        max_points = 13
        increase_target = 'points_to_win_increase'
        decrease_target = 'points_to_win_decrease'
        value_target = 'points_to_win'

        points = getattr(self.game_manager, 'points_to_win', min_points)
        points = max(min_points, min(points, max_points))
        self.game_manager.points_to_win = points

        value_element = self._find_ui_element(value_target)
        if value_element:
            update_text = getattr(value_element, 'update_text', None)
            if callable(update_text):
                update_text(f"{points}")

        decrease_element = self._find_ui_element(decrease_target)
        if not decrease_element:
            return
        if points <= min_points:
            self.deactivate_ui_element(decrease_target)
        else:
            self.activate_ui_element(decrease_target)

        increase_element = self._find_ui_element(increase_target)
        if not increase_element:
            return
        if points >= max_points:
            self.deactivate_ui_element(increase_target)
        else:
            self.activate_ui_element(increase_target)

    def _update_player_color_ui(self) -> None:
        """Sync selected player color visibility and control active states."""
        colors = list(getattr(self.game_manager, 'player_colors', []))
        if not colors:
            return

        max_index = len(colors) - 1
        index = max(0, min(self.game_manager.player_color_chosen_index, max_index))
        self.game_manager.player_color_chosen_index = index
        selected_color = colors[index]

        for color in colors:
            element_name = f"player_color_{color}"
            element = self._find_ui_element(element_name)
            if not element:
                continue
            if color == selected_color:
                element.show()
            else:
                element.hide()

    def _update_player_num_ui(self) -> None:
        """Sync player number display text and control active states."""
        num = getattr(self.game_manager, 'players_num', 2)
        self.buttons["setup"]["player_num"].update_text(f"{num}")

        decrease_target = 'player_num_decrease'
        increase_target = 'player_num_increase'

        decrease_element = self._find_ui_element(decrease_target)
        increase_element = self._find_ui_element(increase_target)

        if decrease_element:
            if num > 2:
                self.activate_ui_element(decrease_target)
            else:
                self.deactivate_ui_element(decrease_target)

        if increase_element:
            if num < 4:
                self.activate_ui_element(increase_target)
            else:
                self.deactivate_ui_element(increase_target)

    def _update_diff_level_ui(self, target: str, other1: str, other2: str) -> None:
        #if target is clicked, deactivate target and activate the other two
        #change later to use a different state (e.g. mouse_button_down instead of deactivated)
        target_element = self._find_ui_element(target)
        other1_element = self._find_ui_element(other1)
        other2_element = self._find_ui_element(other2)

        if target_element and other1_element and other2_element:
            target_element.deactivate()
            other1_element.activate()
            other2_element.activate()

    def _update_robber_mode_ui(self, target: str, other: str) -> None:
        # mutually exclusive buttons for robber mode
        # consider switching to toggle for better UX
        target_element = self._find_ui_element(target)
        other_element = self._find_ui_element(other)

        if target_element and other_element:
            target_element.deactivate()
            other_element.activate()

    def _update_dice_mode_ui(self, target: str, other: str) -> None:
        #mutually exclusive buttons for dice mode
        #consider switching to toggle for better UX
        target_element = self._find_ui_element(target)
        other_element = self._find_ui_element(other)

        if target_element and other_element:
            target_element.deactivate()
            other_element.activate()

    def _update_turn_order_ui(self) -> None:
        target_element: Button = self._find_ui_element("turn_order_text") # type: ignore
        if target_element:
            target_element.update_text(f"{self.game_manager.turn_order}")

    def _update_time_limit_ui(self) -> None:
        toggle_element: Toggle = self._find_ui_element("time_limit_toggle") # type: ignore
        slider_element: Slider = self._find_ui_element("time_limit_slider") # type: ignore
        if toggle_element and slider_element:
            if toggle_element.on:
                slider_element.activate()
            else:
                slider_element.deactivate()

    def deactivate_ui_element(self, target: str):
        element = self._find_ui_element(target)
        if element:
            element.deactivate()

    def activate_ui_element(self, target: str):
        element = self._find_ui_element(target)
        if element:
            element.activate()

    def hide_ui_element(self, target: str):
        element = self._find_ui_element(target)
        if element:
            element.hide()

    def show_ui_element(self, target: str):
        element = self._find_ui_element(target)
        if element:
            element.show()

    def _iter_ui_elements(self):
        """Yield all UI elements from state collections, menu collections, and menus."""
        seen = set()

        def walk(value):
            if isinstance(value, dict):
                for nested in value.values():
                    yield from walk(nested)
                return

            if isinstance(value, UIElement):
                obj_id = id(value)
                if obj_id in seen:
                    return
                seen.add(obj_id)
                yield value

        collections = [
            self.buttons,
            self.toggles,
            self.sliders,
            self.images,
            self.text_displays,
            self.scrollable_areas,
            self.menus,
        ]

        for collection in collections:
            if isinstance(collection, dict):
                yield from walk(collection)

    def _find_ui_element(self, target: str):
        """Find first UI element where key name or element.name matches target."""
        for element in self._iter_ui_elements():
            if getattr(element, 'name', None) == target:
                return element
        return None

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
        Change active tab across open menus that support the tab.
        
        Updates each matching menu's `active_tab` and highlights the corresponding
        tab button for that specific menu.
        
        Args:
            new_tab: Tab identifier ("input", "accessibility", "gameplay", "audio", "graphics")
            
        Note: This supports multi-menu layouts by iterating open menus.
        """
        open_menus = self.get_open_menus()
        if not open_menus:
            print("Warning: No open menus found")
            return

        menus_collection = {}
        if isinstance(self.buttons, dict):
            possible_collection = self.buttons.get("menus", {})
            if isinstance(possible_collection, dict):
                menus_collection = possible_collection

        updated_any = False
        for menu in open_menus:
            menu_button_tabs = {}
            if isinstance(menus_collection, dict):
                menu_button_tabs = menus_collection.get(menu.name, {}).get("tabs", {})

            if not isinstance(menu_button_tabs, dict) or new_tab not in menu_button_tabs:
                continue

            menu.active_tab = new_tab
            menu_button_tabs[new_tab].color = (0, 100, 0)  # Highlight active tab
            for tab_name, button in menu_button_tabs.items():
                if tab_name != new_tab:
                    button.color = (100, 0, 0)

            menu.update_menu(0)
            updated_any = True

        if not updated_any:
            print(f"Warning: No open menu contains tab '{new_tab}'")

    def quit(self):
        """Signal the game to shut down by setting running flag to False."""
        self.game_manager.running = False
  
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

        self._update_player_num_ui()
        self._update_player_color_ui()
        self._update_points_to_win_ui()
        self._update_robber_mode_ui('set_robber_mode_friendly', 'set_robber_mode_standard')
        self._update_diff_level_ui('set_diff_level_easy', 'set_diff_level_medium', 'set_diff_level_hard')
        self._update_dice_mode_ui('set_dice_mode_random', 'set_dice_mode_balanced')
        self._update_turn_order_ui()
        self._update_time_limit_ui()

        self.change_tab("input")  # Set the initial active tab
