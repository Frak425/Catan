import json
from pathlib import Path
import pygame

from src.managers.animation.animation_manager import AnimationManager
from src.ui.elements.button import Button
from src.ui.elements.image import Image
from src.ui.elements.slider import Slider
from src.ui.elements.text_display import TextDisplay
from src.ui.elements.toggle import Toggle
from src.entities.board import Board
from src.ui.elements.menu import Menu
from src.managers.input.input_manager import InputManager
from src.managers.helper_manager import HelperManager
from src.managers.graphics_manager import GraphicsManager
from src.managers.player_manager import PlayerManager
from src.managers.audio_manager import AudioManager

class GameManager:
    """
    Central manager for game state, configuration, and coordination between subsystems.
    
    Responsibilities:
    - Maintain game state (home/setup/game) and player state (roll/trade/buy/place)
    - Load/save configuration files for layout and settings
    - Initialize and manage the game board
    - Provide access to game constants and defaults
    - Coordinate between other manager classes (input, graphics, audio, etc.)
    """
    
    def init(self, screen: pygame.Surface) -> None:
        """
        Initialize the game manager with essential game state and configuration.
        
        Args:
            screen: Pygame surface for rendering
            
        Sets up:
        - Configuration file paths
        - Screen dimensions and font
        - Game state machines (game_state, player_state)
        - Player settings (number, colors, difficulty)
        - UI defaults for toggles, sliders, etc.
        - Game board initialization
        """
        # Core game state
        self.running = True
        self.edited = False  # Whether user has modified default layout/settings

        self.animation_manager = AnimationManager()
        
        # Configuration file paths
        self._init_config_paths()
        
        # Screen and display settings
        self._init_display_settings(screen)
        
        # Game state machines
        self._init_game_states()
        
        # Player configuration
        self._init_player_settings()
        
        # UI positioning and defaults
        self._init_ui_defaults()
        
        # Development/debug flags
        self._init_debug_settings()
        
        # Initialize game board with players
        self.board = self.init_board()
    
    def _init_config_paths(self) -> None:
        """Set up paths to configuration files for layout and settings."""
        self.LAYOUT_CONFIG_PATH = Path("src/config/layout.json")
        self.SETTINGS_CONFIG_PATH = Path("src/config/settings.json")
        self.LAYOUT_STATE_CONFIG_PATH = Path("src/config/layout_state.json")
        self.SETTINGS_STATE_CONFIG_PATH = Path("src/config/settings_state.json")
    
    def _init_display_settings(self, screen: pygame.Surface) -> None:
        """Initialize screen dimensions and font settings."""
        self.screen = screen
        self.screen_size = (screen.get_width(), screen.get_height())
        self.screen_w = self.screen_size[0]
        self.screen_h = self.screen_size[1]
        self.font_size = 20
        self.game_font = pygame.font.SysFont('Comic Sans', self.font_size)
    
    def _init_game_states(self) -> None:
        """
        Initialize game state machines.
        
        game_state flow: home -> setup -> init -> game -> game over -> home
        player_state flow: roll -> trade -> buy -> place -> roll
        """
        self.game_state = "home"
        self.player_state = "roll"
    
    def _init_player_settings(self) -> None:
        """Set up default player configuration and game rules."""
        self.players_num = 2
        self.players_list = []
        self.players_list_index = 0
        self.player_colors = ["yellow", "blue", "green", "red"]
        self.player_color_chosen_index = 0
        self.game_difficulty = "easy"
        self.points_to_win = 10
        self.num_tiles = 19
    
    def _init_ui_defaults(self) -> None:
        """Set default values for UI elements (sliders, toggles, etc.)."""
        # Framerate options and current selection
        self.framerates = [30, 60, 120, 240]
        self.framerate_index = 1  # Default to 60 FPS
        
        # Buy menu positioning
        self.buy_selection_backdrop_offset = (self.screen_w / 8 * 5, self.screen_h / 8 * 7)
        self.buy_selection_offset = (50, 50)
        
        # Toggle defaults
        self.default_time_to_flip = 0.25
        self.default_height = 50
        self.default_center_width = 100
        self.default_fill_color = (0, 100, 0)
        self.default_handle_color = (100, 0, 0)
        self.default_toggle_gap = 7
        self.default_on = False
        self.default_guiding_lines = True
    
    def _init_debug_settings(self) -> None:
        """Initialize development and debugging flags."""
        self.dev_mode = False
        self.dev_mode_typing = False
        self.dev_mode_text = ""
        self.debugging = False

    def init_board(self) -> Board:
        """
        Create and initialize the game board with tiles and players.
        
        Creates Player objects based on players_num, then initializes the Board
        with proper sizing, tile placement, and resource assignment.
        
        Returns:
            Board: Initialized game board ready for play
        """

        # Calculate board sizing (screen_w / 27.32 determines tile size)
        global board
        board = Board(
            self.screen_w / 27.32,  # Tile size based on screen width
            self.screen_h, 
            self.screen_w, 
            self.num_tiles, 
            self.screen, 
            self.game_font, 
            self.font_size
        )
        
        # Set up board layout and assign resources
        board.assign_tile_locations()
        board.assign_tiles()
        board.assign_tile_classes()
        
        return board

    ## --- DEPENDENCY INJECTION (TODO: Replace with constructor injection) --- ##
    
    def set_input_manager(self, input_manager: InputManager):
        """Inject InputManager dependency. Used for circular dependency resolution."""
        self.input_manager = input_manager

    def set_audio_manager(self, audio_manager: AudioManager):
        """Inject AudioManager dependency. Used for circular dependency resolution."""
        self.audio_manager = audio_manager

    def set_graphics_manager(self, graphics_manager: GraphicsManager):
        """Inject GraphicsManager dependency. Used for circular dependency resolution."""
        self.graphics_manager = graphics_manager

    def set_helper_manager(self, helper_manager: HelperManager):
        """Inject HelperManager dependency. Used for circular dependency resolution."""
        self.helper_manager = helper_manager

    def set_player_manager(self, player_manager: PlayerManager):
        """Inject PlayerManager dependency. Used for circular dependency resolution."""
        self.player_manager = player_manager

    def set_driver_manager(self, driver_manager) -> None:
        """Inject DriverManager dependency. Used for circular dependency resolution."""
        self.driver_manager = driver_manager

    ## --- LAYOUT/SETTINGS GENERATION --- ##
    
    def get_layout(self) -> dict:
        """
        Generate layout configuration from current UI elements.
        
        Reads the current state of all UI elements (buttons, sliders, etc.) 
        from input_manager and converts them to a serializable dict structure
        for saving to layout.json.
        
        Returns:
            dict: Layout configuration with sections for each game state (home/setup/game)
                  plus a menus array for all Menu configurations
        """
        # Create base layout structure with empty arrays for all UI element types
        layout = self._create_empty_layout_structure()

        # Populate each section by converting UI elements to dicts
        layout["home"] = self.save_layout_by_section("home")
        layout["setup"] = self.save_layout_by_section("setup")
        layout["game"] = self.save_layout_by_section("game")
        
        # Save all menus at the top level
        layout["menus"] = [menu.get_layout() for menu in self.input_manager.menus.values()]

        return layout
    
    def _create_empty_layout_structure(self) -> dict:
        """
        Create empty layout dict structure with all required sections.
        
        Returns:
            dict: Empty layout with home/setup/game sections and menus array
        """
        section_template = {
            "buttons": [],
            "images": [],
            "sliders": [],
            "toggles": [],
            "text_displays": [],
            "scrollable_areas": [],
            "text_inputs": [],
            "multi_selects": [],
            "menus": []
        }
        
        return {
            "home": section_template.copy(),
            "setup": section_template.copy(),
            "game": section_template.copy(),
            "menus": []
        }

    def get_settings(self) -> dict:
        """
        Generate default settings configuration.
        
        Returns:
            dict: Settings organized by category (audio/graphics/gameplay/accessibility/input)
        """
        settings_defaults = {
            "audio": {},
            "graphics": {},
            "gameplay": {},
            "accessibility": {},
            "input": {}
        }

        return settings_defaults
            
    def save_layout_by_section(self, section: str) -> dict:
        """
        Convert UI elements from a specific section to serializable dict format.
        
        Takes all UI elements (buttons, sliders, toggles, etc.) from the specified
        game state section and converts their current state/properties into dicts
        that can be saved to JSON.
        
        Args:
            section: Game state section name ("home", "setup", or "game")
            
        Returns:
            dict: Section data with all UI elements as lists of property dicts
        """
        # Start with empty structure for this section
        section_data = self._create_empty_section_structure()
        
        # Convert each UI element type from objects to dicts
        section_data["buttons"] = self.convert_buttons_to_list(
            self.input_manager.buttons[section]
        )
        section_data["images"] = self.convert_images_to_list(
            self.input_manager.images[section]
        )
        section_data["sliders"] = self.convert_sliders_to_list(
            self.input_manager.sliders[section]
        )
        section_data["toggles"] = self.convert_toggles_to_list(
            self.input_manager.toggles[section]
        )
        section_data["text_displays"] = self.convert_text_displays_to_list(
            self.input_manager.text_displays[section]
        )
        section_data["scrollable_areas"] = self.convert_scrollable_areas_to_list(
            self.input_manager.scrollable_areas[section]
        )
        
        # Add references to which menus are available in this section
        if section in ["home", "setup", "game"]:
            section_data["menus"] = list(self.input_manager.menus.keys())

        # TODO: Implement text_inputs and multi_selects converters
        
        return section_data
    
    def _create_empty_section_structure(self) -> dict:
        """
        Create empty structure for a single layout section.
        
        Returns:
            dict: Empty arrays for all UI element types
        """
        return {
            "buttons": [],
            "images": [],
            "sliders": [],
            "toggles": [],
            "text_displays": [],
            "scrollable_areas": [],
            "text_inputs": [],
            "multi_selects": [],
            "menus": []
        }

    ## --- UI ELEMENT CONVERTERS (Object -> Dict) --- ##
    
    def convert_buttons_to_list(self, buttons: dict[str, Button]) -> list:
        """
        Convert Button objects to serializable dict format.
        
        Extracts properties from Button objects and attempts to preserve callback
        names by reverse-looking up in the callback registry.
        
        Args:
            buttons: Dict mapping button names to Button objects
            
        Returns:
            list: List of dicts containing button properties (name, rect, color, etc.)
        """
        layout_object_list = []
        for button_name, button in buttons.items():
            layout_object = {
                "name": button.name,
                "rect": [button.rect[0], button.rect[1], button.rect[2], button.rect[3]],
                "color": [button.color[0], button.color[1], button.color[2]],
                "text": button.text,
                "text_color": [button.text_color[0], button.text_color[1], button.text_color[2]],
                "padding": button.padding
            }
            # Store callback name if it exists (for config-driven loading)
            if hasattr(button, 'callback') and button.callback:
                # Do reverse lookup in callback registry to find the name
                callback_name = None
                if hasattr(self.input_manager, 'ui_factory') and hasattr(self.input_manager.ui_factory, 'callback_registry'):
                    for name, func in self.input_manager.ui_factory.callback_registry.items():
                        if func == button.callback:
                            callback_name = name
                            break
                
                # Fallback to __name__ if reverse lookup fails (but skip if it's "<lambda>")
                if not callback_name:
                    callback_name = getattr(button.callback, '__name__', None)
                    if callback_name == "<lambda>":
                        callback_name = None
                
                if callback_name:
                    layout_object["callback"] = callback_name
            layout_object_list.append(layout_object)
        return layout_object_list

    def convert_images_to_list(self, images: dict[str, Image]) -> list:
        """
        Convert Image objects to serializable dict format.
        
        Args:
            images: Dict mapping image names to Image objects
            
        Returns:
            list: List of dicts containing image properties (name, rect, file_path)
        """
        layout_object_list = []
        for image_name, image in images.items():
            layout_object = {
                "name": image.name,
                "rect": [image.rect[0], image.rect[1], image.rect[2], image.rect[3]],
                "image_path": image.image_path,
            }
            layout_object_list.append(layout_object)
        return layout_object_list

    def convert_sliders_to_list(self, sliders: dict[str, Slider]) -> list:
        """
        Convert Slider objects to serializable dict format.
        
        Args:
            sliders: Dict mapping slider names to Slider objects
            
        Returns:
            list: List of dicts containing slider properties (name, rect, min/max values, colors)
        """
        layout_object_list = []
        for slider_name, slider in sliders.items():
            layout_object = {
                "name": slider.name,
                "rect": [slider.rect[0], slider.rect[1], slider.rect[2], slider.rect[3]],
                "min_value": slider.min_value,
                "max_value": slider.max_value,
                "color": [slider.color[0], slider.color[1], slider.color[2]],
                "handle_color": [slider.handle_color[0], slider.handle_color[1], slider.handle_color[2]],
                "handle_radius": slider.handle_radius
            }
            # Store callback name if it exists
            if hasattr(slider, 'callback') and slider.callback:
                callback_name = None
                if hasattr(self.input_manager, 'ui_factory') and hasattr(self.input_manager.ui_factory, 'callback_registry'):
                    for name, func in self.input_manager.ui_factory.callback_registry.items():
                        if func == slider.callback:
                            callback_name = name
                            break
                if not callback_name:
                    callback_name = getattr(slider.callback, '__name__', None)
                    if callback_name == "<lambda>":
                        callback_name = None
                if callback_name:
                    layout_object["callback"] = callback_name
            layout_object_list.append(layout_object)
        return layout_object_list

    def convert_toggles_to_list(self, toggles: dict[str, Toggle]) -> list:
        """
        Convert Toggle objects to serializable dict format.
        
        Args:
            toggles: Dict mapping toggle names to Toggle objects
            
        Returns:
            list: List of dicts containing toggle properties (name, rect, animation settings)
        """
        layout_object_list = []
        for toggle_name, toggle in toggles.items():
            layout_object = {
                "name": toggle.name,
                "rect": [toggle.rect[0], toggle.rect[1], toggle.rect[2], toggle.rect[3]],
                "guiding_lines": toggle.guiding_lines,
                "height": toggle.height,
                "center_width": toggle.center_width,
                "color": [toggle.color[0], toggle.color[1], toggle.color[2]],
                "handle_color": [toggle.handle_color[0], toggle.handle_color[1], toggle.handle_color[2]],
                "toggle_gap": toggle.toggle_gap,
                "time_to_flip": toggle.time_to_flip
            }
            # Store callback name if it exists
            if hasattr(toggle, 'callback') and toggle.callback:
                callback_name = None
                if hasattr(self.input_manager, 'ui_factory') and hasattr(self.input_manager.ui_factory, 'callback_registry'):
                    for name, func in self.input_manager.ui_factory.callback_registry.items():
                        if func == toggle.callback:
                            callback_name = name
                            break
                if not callback_name:
                    callback_name = getattr(toggle.callback, '__name__', None)
                    if callback_name == "<lambda>":
                        callback_name = None
                if callback_name:
                    layout_object["callback"] = callback_name
            layout_object_list.append(layout_object)
        return layout_object_list

    def convert_text_displays_to_list(self, text_displays: dict[str, TextDisplay]) -> list:
        """
        Convert TextDisplay objects to serializable dict format.
        
        Args:
            text_displays: Dict mapping text display names to TextDisplay objects
            
        Returns:
            list: List of dicts containing text display properties (name, rect, text, colors)
        """
        layout_object_list = []
        for text_display_name, text_display in text_displays.items():
            layout_object = {
                "name": text_display.name,
                "rect": [text_display.rect[0], text_display.rect[1], text_display.rect[2], text_display.rect[3]],
                "color": [text_display.color[0], text_display.color[1], text_display.color[2]],
                "text": text_display.text,
                "text_color": [text_display.text_color[0], text_display.text_color[1], text_display.text_color[2]],
                "padding": text_display.padding
            }
            layout_object_list.append(layout_object)
        return layout_object_list

    def convert_scrollable_areas_to_list(self, scrollable_areas: dict) -> list:
        """Convert scrollable area dictionary to list format for JSON serialization."""
        from src.ui.elements.scrollable_area import ScrollableArea
        layout_object_list = []
        for area_name, area in scrollable_areas.items():
            if isinstance(area, ScrollableArea):
                layout_object = area.get_layout()
                layout_object_list.append(layout_object)
        return layout_object_list

    #TODO: Implement after creating TextInput and MultiSelect classes
    def convert_text_inputs_to_list(self, text_inputs: list) -> list:
        return []

    def convert_multi_selects_to_list(self, multi_selects: list) -> list:
        """TODO: Convert MultiSelect objects to dict format once implemented."""
        return []

    ## --- CONFIG FILE I/O --- ##

    def load_config(self, file: str, overriding: bool) -> None:
        """
        Load configuration from JSON file, creating it if it doesn't exist.
        
        Loads either layout or settings configuration from disk. If the file doesn't
        exist, generates default config using get_layout() or get_settings() and saves it.
        
        Args:
            file: Config type - either "layout" or "settings"
            overriding: If True, uses default config path. If False, uses state/user path
        """
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

    def save_config(self, file: str, overriding: bool) -> None:
        """
        Save current configuration to JSON file.
        
        Regenerates config from current game state using reload_config() and
        writes it to the appropriate file path.
        
        Args:
            file: Config type - either "layout" or "settings"
            overriding: If True, saves to default path. If False, saves to state/user path
        """
        CONFIG_PATH = self.config_path_by_name(file, overriding)

        with open(CONFIG_PATH, "w") as f:
            json.dump(self.reload_config(CONFIG_PATH), f, indent=4)

    def config_path_by_name(self, file: str, overriding: bool) -> Path:
        """
        Get file path for specified config type.
        
        Returns either the default config path or the user/state config path
        depending on the overriding flag.
        
        Args:
            file: Config type - either "layout" or "settings"
            overriding: If True, returns default path. If False, returns state/user path
            
        Returns:
            Path: Path object pointing to the config file
        """
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
        """
        Get reference to in-memory config data by name.
        
        Args:
            file: Config type - either "layout" or "settings"
            
        Returns:
            dict: The loaded layout or settings configuration
        """
        if file == "layout":
            return self.layout
        elif file == "settings":
            return self.settings

    def reload_config(self, path: Path) -> dict:
        """
        Generate fresh config data based on file path.
        
        Determines which config type to generate (layout or settings) based on
        the provided path and returns freshly generated config from current game state.
        
        Args:
            path: Path to config file (used to determine config type)
            
        Returns:
            dict: Freshly generated layout or settings config, or empty dict if path unknown
        """
        if path == self.LAYOUT_STATE_CONFIG_PATH:
            return self.get_layout()
        elif path == self.SETTINGS_STATE_CONFIG_PATH:
            return self.get_settings()
        elif path == self.LAYOUT_CONFIG_PATH:
            return self.get_layout()
        elif path == self.SETTINGS_CONFIG_PATH:
            return self.get_settings()
        
        return {}
    
    def restore_config(self, file: str) -> None:
        """
        Restore config to defaults and recreate UI.
        
        Loads the default (non-state) version of the config and resets the UI
        to reflect the default layout.
        
        Args:
            file: Config type - either "layout" or "settings"
        """
        self.load_config(file, True)

        self.input_manager.reset_ui()