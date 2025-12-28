import pygame
import pygame
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from game_manager import GameManager
    from input_manager import InputManager

from src.ui.elements.button import Button
from src.ui.elements.slider import Slider
from src.ui.elements.toggle import Toggle
from src.ui.elements.image import Image
from src.ui.elements.text_display import TextDisplay
from src.ui.elements.menu import Menu
from src.ui.elements.scrollable_area import ScrollableArea


class UIFactory:
    """
    Factory class for creating all UI elements from JSON layout configurations.
    
    Responsibilities:
    - Parse layout.json and create typed UI element instances (Button, Slider, Toggle, etc.)
    - Map element names to callback functions from InputManager
    - Organize elements by state (home/setup/game/menu) and menu tabs
    - Handle default values when config is incomplete
    
    Layout Structure Expected:
    - layout.json contains states: ["home", "setup", "game"] with element arrays
    - layout.json contains menus: array of menu configs with tabs
    - Tabs: ["tabs", "input", "accessibility", "graphics", "audio", "gameplay"]
    - Each element type (buttons, sliders, toggles, etc.) is organized by state/tab
    
    Architecture:
    - Uses factory pattern to create UI elements dynamically from config
    - Callbacks are registered once and retrieved by name during creation
    - Element creation is standardized through _create_elements_from_layout()
    """
    
    def __init__(self, game_manager: 'GameManager', input_manager: 'InputManager'):
        """
        Initialize UIFactory with manager dependencies.
        
        Args:
            game_manager: Central game state manager (provides layout, fonts, settings)
            input_manager: Input coordination manager (provides UI element references)
        """
        self.game_manager = game_manager
        self.input_manager = input_manager
        self.callback_registry = {}  # Populated by register_callbacks()
    
    ## --- CALLBACK MANAGEMENT --- ##
    
    def register_callbacks(self, callbacks: dict):
        """
        Register all callbacks for UI elements. Called once during initialization.
        
        Args:
            callbacks: Dict mapping callback names to functions
                      (e.g., {'close_menu': func, 'set_player_num': func})
        
        Note: Callbacks are created by InputManager._create_callbacks() and
              mapped to UI elements by name during element creation.
        """
        self.callback_registry = callbacks

    def _get_callback(self, callback_name: str):
        """
        Get a callback function by name from the registry.
        
        Args:
            callback_name: Name of callback (e.g., 'close_menu', 'set_player_num')
        
        Returns:
            Callable or None: The registered callback function, or None if not found
        """
        return self.callback_registry.get(callback_name, None)

    ## --- LAYOUT ACCESS HELPERS --- ##
    
    def _get_from_layout(self, element_type: str, state: str, name: str, tab: str | None = None):
        """
        Helper to retrieve element config from layout structure by name.
        
        Args:
            element_type: Type of element ('buttons', 'sliders', 'toggles', etc.)
            state: State name ('home', 'setup', 'game', 'menu')
            name: Element name to find (e.g., 'close_menu', 'volume_slider')
            tab: Optional menu tab name (e.g., 'audio', 'graphics')
        
        Returns:
            dict or None: Element config dict from layout, or None if not found
        
        Layout Navigation:
        - Non-menu: layout[state][element_type] -> find by name
        - Menu: layout[state][tab][element_type] -> find by name
        """
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

    def _create_elements_from_layout(self, element_type: str, factory_func, callbacks: dict) -> Dict[str, Dict]:
        """
        Generic helper to create UI elements from layout config using factory pattern.
        
        Args:
            element_type: Type of elements to create ('buttons', 'sliders', etc.)
            factory_func: Factory function that creates individual elements
                         Signature: (props, callbacks, state, tab) -> UIElement
            callbacks: Dict of callback functions to pass to factory
        
        Returns:
            Dict[str, Dict]: Nested structure of created elements:
                {
                    "home": {name: element, ...},
                    "setup": {name: element, ...},
                    "game": {name: element, ...},
                    "menu": {
                        "tabs": {name: element, ...},
                        "input": {name: element, ...},
                        "accessibility": {name: element, ...},
                        "graphics": {name: element, ...},
                        "audio": {name: element, ...},
                        "gameplay": {name: element, ...}
                    }
                }
        
        Process:
        1. Return empty structure if no layout loaded
        2. Iterate through non-menu states (home, setup, game)
        3. For each state, extract element_type array and create elements
        4. Iterate through menu tabs from layout.menus array
        5. For each tab, extract elements dict and create elements
        
        Note: Non-menu states use arrays of elements, menu tabs use dicts keyed by name
        """
        layout = getattr(self.game_manager, 'layout', None)
        if not layout:
            return {"home": {}, "setup": {}, "game": {}, "menu": {"tabs": {}, "input": {}, "accessibility": {}, "graphics": {}, "audio": {}, "gameplay": {}}}
        
        result = {}
        
        # Load non-menu states
        for state in ["home", "setup", "game"]:
            result[state] = {}
            if state in layout and element_type in layout[state]:
                elements_list = layout[state][element_type]
                for element_props in elements_list:
                    name = element_props.get('name')
                    element = factory_func(element_props, callbacks, state, None)
                    if element:
                        result[state][name] = element
        
        # Load menu elements from the menus array
        menu_tabs = ["tabs", "input", "accessibility", "graphics", "audio", "gameplay"]
        result["menu"] = {tab: {} for tab in menu_tabs}
        if "menus" in layout and isinstance(layout["menus"], list):
            for menu_config in layout["menus"]:
                # Each menu has element_type as key, then tabs inside
                # Structure: menu_config[element_type][tab] = {name: element_config}
                if element_type in menu_config:
                    for tab in menu_tabs:
                        if tab in menu_config[element_type]:
                            # The config is a dict of name->properties, not a list
                            for name, element_props in menu_config[element_type][tab].items():
                                element = factory_func(element_props, callbacks, "menu", tab)
                                if element:
                                    result["menu"][tab][name] = element
        
        return result

    ## --- ELEMENT FACTORIES (CONFIG-DRIVEN CREATION) --- ##

    def _get_default_button_callbacks(self) -> dict:
        """
        Get default button name -> callback name mapping for fallback.
        
        Returns:
            dict: Mapping of button names to callback names
        
        Note: Used when layout.json doesn't specify callback for a button.
              Primarily for tab navigation buttons in menu system.
        """
        return {
            # Tab navigation buttons
            'input': 'change_tab_input',
            'accessibility': 'change_tab_accessibility',
            'gameplay': 'change_tab_gameplay',
            'audio': 'change_tab_audio',
            'graphics': 'change_tab_graphics',
            'close_menu': 'close_menu'
        }
    
    def create_all_buttons(self, callbacks):
        """
        Create all buttons dynamically from layout config.
        
        Args:
            callbacks: Dict of callback functions from InputManager
        
        Returns:
            Dict[str, Dict]: Button instances organized by state and tab
        
        Process:
        1. Register callbacks for lookup during creation
        2. Define factory function that creates Button instances
        3. Handle callback mapping (from config or fallback to defaults)
        4. Use _create_elements_from_layout to iterate and create all buttons
        5. Validate that tab buttons exist (critical for menu navigation)
        
        Button Callback Resolution:
        - First check element config for 'callback' property
        - If missing, use _get_default_button_callbacks() mapping
        - If still no callback, button is created without callback (visual only)
        """
        self.register_callbacks(callbacks)
        button_name_to_callback = self._get_default_button_callbacks()
        
        def button_factory(props, cbs, state, tab):
            callback_name = props.get('callback')
            
            # If no callback in JSON, try to infer from button name
            if not callback_name:
                button_name = props.get('name')
                callback_name = button_name_to_callback.get(button_name)
            
            callback = self._get_callback(callback_name) if callback_name else None
            
            return Button(props, self.game_manager.game_font, self.game_manager, callback=callback)
        
        result = self._create_elements_from_layout('buttons', button_factory, callbacks)
        
        # Note: Tab buttons should always be loaded from layout.json
        # If no tabs found in config, the layout.json is incomplete
        if not result["menu"]["tabs"]:
            print("Warning: No tab buttons found in layout.json. Menu tabs will not work.")
        
        return result

    def create_all_sliders(self, callbacks) -> Dict[str, Dict]:
        """
        Create all sliders dynamically from layout config.
        
        Args:
            callbacks: Dict of callback functions from InputManager
        
        Returns:
            Dict[str, Dict]: Slider instances organized by state and tab
        
        Slider Configuration:
        - initial_value: Starting value (defaults to min_value if not specified)
        - callback: Function called when slider value changes
        - Special handling for 'set_player_num' callback (wraps with int conversion)
        
        Note: Player number slider gets lambda wrapper to convert float to int
        """
        def slider_factory(props, cbs, state, tab):
            initial_value = props.get('initial_value', props.get('min_value', 0))
            callback_name = props.get('callback')
            
            slider = Slider(props, initial_value, self.game_manager, None)
            
            # Handle special callbacks like player_num_slider that need the value parameter
            if callback_name == 'set_player_num':
                slider.callback = lambda s=slider: cbs['set_player_num'](int(s.value))
            elif callback_name:
                slider.callback = self._get_callback(callback_name)
            
            return slider
        
        return self._create_elements_from_layout('sliders', slider_factory, callbacks)

    def create_all_toggles(self, callbacks) -> Dict[str, Dict]:
        """
        Create all toggles (on/off switches) dynamically from layout config.
        
        Args:
            callbacks: Dict of callback functions from InputManager
        
        Returns:
            Dict[str, Dict]: Toggle instances organized by state and tab
        
        Toggle Configuration:
        - on: Initial state (defaults to game_manager.default_on if not specified)
        - callback: Function called when toggle is switched
        - Requires graphics_manager.time for animation timing
        """
        def toggle_factory(props, cbs, state, tab):
            initial_on = props.get('on', self.game_manager.default_on)
            callback_name = props.get('callback')
            callback = self._get_callback(callback_name) if callback_name else None
            return Toggle(props, self.game_manager.graphics_manager.time, self.game_manager, on=initial_on, callback=callback)
        
        return self._create_elements_from_layout('toggles', toggle_factory, callbacks)

    def create_all_images(self, callbacks) -> Dict[str, Dict]:
        """
        Create all image display elements dynamically from layout config.
        
        Args:
            callbacks: Dict of callback functions from InputManager
        
        Returns:
            Dict[str, Dict]: Image instances organized by state and tab
        
        Image Configuration:
        - callback: Optional function called when image is clicked (for clickable images)
        - Can be used for decorative images (no callback) or interactive images (with callback)
        """
        def image_factory(props, cbs, state, tab):
            callback_name = props.get('callback')
            callback = self._get_callback(callback_name) if callback_name else None
            return Image(props, self.game_manager, callback=callback)
        
        return self._create_elements_from_layout('images', image_factory, callbacks)

    def create_all_text_displays(self, callbacks) -> Dict[str, Dict]:
        """
        Create all text display elements dynamically from layout config.
        
        Args:
            callbacks: Dict of callback functions from InputManager
        
        Returns:
            Dict[str, Dict]: TextDisplay instances organized by state and tab
        
        TextDisplay Configuration:
        - callback: Optional function called when text is clicked (for interactive text)
        - Uses game_manager.game_font for rendering
        - Can display static text or dynamic text (updated via callback)
        """
        def text_display_factory(props, cbs, state, tab):
            callback_name = props.get('callback')
            callback = self._get_callback(callback_name) if callback_name else None
            return TextDisplay(props, self.game_manager, self.game_manager.game_font, callback=callback)
        
        return self._create_elements_from_layout('text_displays', text_display_factory, callbacks)

    def _create_test_gradient_surface(self, width: int, height: int) -> pygame.Surface:
        """
        Create a vertical gradient surface for testing scrollable areas.
        
        Args:
            width: Surface width in pixels
            height: Surface height in pixels
        
        Returns:
            pygame.Surface: Surface with red-to-blue gradient (for visual testing)
        
        Note: This is a placeholder. Production code should provide actual content.
        """
        surface = pygame.Surface((width, height))
        start_color = (255, 0, 0)  # Red at top
        end_color = (0, 0, 255)    # Blue at bottom
        
        for y in range(height):
            ratio = y / height
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
        return surface
    
    def create_all_scrollable_areas(self, callbacks) -> Dict[str, Dict]:
        """
        Create all scrollable area elements dynamically from layout config.
        
        Args:
            callbacks: Dict of callback functions from InputManager
        
        Returns:
            Dict[str, Dict]: ScrollableArea instances organized by state and tab
        
        ScrollableArea Configuration:
        - content_height: Total height of scrollable content (default: 600)
        - viewable_content_width: Width of visible area (default: 200)
        - Content surface is initialized with test gradient (should be replaced)
        
        Note: Current implementation creates placeholder gradient surfaces.
              Production use requires updating content_surface after creation.
        """
        def scrollable_area_factory(props, cbs, state, tab):
            content_height = props.get('content_height', 600)
            content_width = props.get('viewable_content_width', 200)
            content_surface = self._create_test_gradient_surface(content_width, content_height)
            
            return ScrollableArea(props, self.game_manager, content_surface)
        
        return self._create_elements_from_layout('scrollable_areas', scrollable_area_factory, callbacks)

    ## --- MENU ASSEMBLY --- ##
    
    def create_all_menus(self, buttons, toggles, sliders, images, text_displays) -> dict:
        """
        Create all menus from layout.menus array and assemble with UI elements.
        
        Args:
            buttons: All created button instances (organized by state/tab)
            toggles: All created toggle instances (organized by state/tab)
            sliders: All created slider instances (organized by state/tab)
            images: All created image instances (organized by state/tab)
            text_displays: All created text display instances (organized by state/tab)
        
        Returns:
            dict: Menu instances keyed by name (e.g., {'settings': Menu})
        
        Process:
        1. Iterate through layout.menus array
        2. For each menu config, create Menu instance with all element collections
        3. Menu class handles filtering elements for its tabs
        4. If no menus in config, create default 'settings' menu for compatibility
        
        Menu Structure:
        - Each Menu contains tabs (input, accessibility, graphics, audio, gameplay)
        - Tabs contain filtered subsets of buttons, toggles, sliders, etc.
        - Menu handles rendering and tab switching logic
        """
        layout = getattr(self.game_manager, 'layout', None)
        menus = {}
        
        if layout and "menus" in layout and isinstance(layout["menus"], list):
            for menu_config in layout["menus"]:
                menu_name = menu_config.get("name", "menu")
                menu = Menu(
                    layout_props=menu_config,
                    game_manager=self.game_manager,
                    buttons=buttons,
                    toggles=toggles,
                    sliders=sliders,
                    images=images,
                    text_displays=text_displays
                )
                menus[menu_name] = menu
        
        # If no menus found in layout, create default settings menu for backwards compatibility
        if not menus:
            menu = Menu(
                layout_props={},
                game_manager=self.game_manager,
                buttons=buttons,
                toggles=toggles,
                sliders=sliders,
                images=images,
                text_displays=text_displays
            )
            menus["settings"] = menu
        
        return menus

