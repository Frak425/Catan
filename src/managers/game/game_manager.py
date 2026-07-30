from dataclasses import asdict, dataclass
import json
from pathlib import Path
import pygame
from typing import Any

from src.managers.base_manager import BaseManager
from src.managers.animation.animation_manager import AnimationManager
from src.ui.elements.button import Button
from src.ui.elements.image import Image
from src.ui.elements.slider import Slider
from src.ui.elements.text_display import TextDisplay
from src.ui.elements.toggle import Toggle
from src.ui.elements.menu import Menu
from src.managers.input.input_manager import InputManager
from src.managers.helper.helper_manager import HelperManager
from src.managers.graphics.graphics_manager import GraphicsManager
from src.managers.player.player_manager import PlayerManager
from src.managers.audio.audio_manager import AudioManager

class GameManager(BaseManager):
    """
    Central manager for game state, configuration, and coordination between subsystems.
    
    Responsibilities:
    - Maintain game state (home/setup/game) and player state (roll/trade/buy/place)
    - Load/save configuration files for layout and settings
    - Initialize and manage the game board
    - Provide access to game constants and defaults
    - Coordinate between other manager classes (input, graphics, audio, etc.)
    """
    
    def __init__(self):
        super().__init__()
        
    def import_dependencies(self, screen: pygame.Surface) -> None:
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
       
        self.input_manager = self.get_dependency('input_manager')
        self.audio_manager = self.get_dependency('audio_manager')
        self.graphics_manager = self.get_dependency('graphics_manager')
        self.helper_manager = self.get_dependency('helper_manager')
        self.player_manager = self.get_dependency('player_manager')
        self.animation_manager = self.get_dependency('animation_manager')
        self.driver_manager = self.get_dependency('driver_manager')

        # Core game state
        self.running = True
        self.edited = False  # Whether user has modified default layout/settings

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
        self.game_font = 'Comic Sans'
        self.font = pygame.font.SysFont(self.game_font, self.font_size)
    
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
        self.num_players = 2
        self.players_list = []
        self.players_list_index = 0
        self.player_colors = ["red", "green", "blue", "yellow"]
        self.player_color_chosen_index = 0
        self.game_difficulty = "easy"
        self.points_to_win = 10
        self.num_tiles = 19
        self.turn_order = 1

    #TODO: Generalize because this essentially acts as "find selected from ui"
    def _selected_choice_from_setup_buttons(self, choices: dict[str, str], default: str) -> str:
        """
        Resolve the selected value from setup-page mutually exclusive buttons.

        Current setup UI convention marks the selected option as deactivated
        (`button.active == False`) while non-selected options stay active.

        Args:
            choices: Mapping of setup button names to semantic values.
            default: Fallback value if setup buttons are unavailable/ambiguous.

        Returns:
            str: Selected semantic value.
        """
        setup_buttons = getattr(getattr(self, "input_manager", None), "buttons", {}).get("setup", {})

        if not isinstance(setup_buttons, dict):
            return default

        selected_values = []
        for button_name, value in choices.items():
            button = setup_buttons.get(button_name)
            if button is not None and hasattr(button, "active") and button.active is False:
                selected_values.append(value)

        if len(selected_values) == 1:
            return selected_values[0]

        return default

    def collect_setup_game_settings(self) -> GameConfig:
        """
        Collect current setup-page selections and return new game settings.

        Data sources:
        - Setup buttons/toggles/sliders in `input_manager`
        - Existing `game_manager` state as fallback/default values

        Returns:
            dict[str, Any]: New game settings snapshot.
        """
        setup_toggles = getattr(getattr(self, "input_manager", None), "toggles", {}).get("setup", {})
        setup_sliders = getattr(getattr(self, "input_manager", None), "sliders", {}).get("setup", {})

        time_limit_toggle = setup_toggles.get("time_limit_toggle") if isinstance(setup_toggles, dict) else None
        time_limit_slider = setup_sliders.get("time_limit_slider") if isinstance(setup_sliders, dict) else None

        settings = GameConfig(
            num_players= self.num_players,
            player_color= self.player_colors[self.player_color_chosen_index % len(self.player_colors)],
            difficulty= self._selected_choice_from_setup_buttons({"set_diff_level_easy": "easy", "set_diff_level_medium": "medium", "set_diff_level_hard": "hard",}, default=self.game_difficulty),
            points_to_win= int(self.points_to_win),
            dice_mode= self._selected_choice_from_setup_buttons({"set_dice_mode_random": "random", "set_dice_mode_balanced": "balanced",}, default="random"),
            robber_mode= self._selected_choice_from_setup_buttons({"set_robber_mode_friendly": "friendly", "set_robber_mode_standard": "standard",}, default="friendly"),
            turn_order= int(self.turn_order),
            time_limit_enabled= bool(getattr(time_limit_toggle, "on", False)),
            time_limit_seconds= int(round(getattr(time_limit_slider, "value", 0)))
        )

        return settings
    
    def _init_ui_defaults(self) -> None:
        """Set default values for UI elements (sliders, toggles, etc.)."""
        # Framerate options and current selection
        self.framerates = [30, 60, 120, 240]
        self.framerate_index = 2  # Default to 60 FPS
        
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
        return [asdict(button.get_layout()) for button in buttons.values()]

    def convert_images_to_list(self, images: dict[str, Image]) -> list:
        """
        Convert Image objects to serializable dict format.
        
        Args:
            images: Dict mapping image names to Image objects
            
        Returns:
            list: List of dicts containing image properties (name, rect, file_path)
        """
        return [asdict(image.get_layout()) for image in images.values()]

    def convert_sliders_to_list(self, sliders: dict[str, Slider]) -> list:
        """
        Convert Slider objects to serializable dict format.
        
        Args:
            sliders: Dict mapping slider names to Slider objects
            
        Returns:
            list: List of dicts containing slider properties (name, rect, min/max values, colors)
        """
        return [asdict(slider.get_layout()) for slider in sliders.values()]

    def convert_toggles_to_list(self, toggles: dict[str, Toggle]) -> list:
        """
        Convert Toggle objects to serializable dict format.
        
        Args:
            toggles: Dict mapping toggle names to Toggle objects
            
        Returns:
            list: List of dicts containing toggle properties (name, rect, animation settings)
        """
        return [asdict(toggle.get_layout()) for toggle in toggles.values()]

    def convert_text_displays_to_list(self, text_displays: dict[str, TextDisplay]) -> list:
        """
        Convert TextDisplay objects to serializable dict format.
        
        Args:
            text_displays: Dict mapping text display names to TextDisplay objects
            
        Returns:
            list: List of dicts containing text display properties (name, rect, text, colors)
        """
        return [asdict(text_display.get_layout()) for text_display in text_displays.values()]

    def convert_scrollable_areas_to_list(self, scrollable_areas: dict) -> list:
        """Convert scrollable area dictionary to list format for JSON serialization."""
        return [asdict(area.get_layout()) for area in scrollable_areas.values()]
    
    def convert_tiles_to_list(self, tiles: dict) -> list:
        return [asdict(tile.get_layout()) for tile in tiles.values()]

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

@dataclass
class GameConfig:
    num_players: int = 4
    player_color: str = ""
    difficulty: str = ""
    points_to_win: int = 10
    dice_mode: str = ""
    robber_mode: str = "friendly"
    turn_order: int = 1
    time_limit_enabled: bool = False
    time_limit_seconds: int = 60
