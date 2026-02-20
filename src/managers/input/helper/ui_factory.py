import pygame
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from src.managers.game.game_manager import GameManager
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

    def _resolve_callback(self, props: dict, fallback_name: str | None = None):
        """
        Resolve callback using registry-first priority.

        Priority order:
        1) Element name (registry key) - overrides JSON callback field
        2) JSON callback field
        3) Optional fallback callback name
        """
        element_name = str(props.get('name', '')).strip()
        callback_name = props.get('callback')
        callback_name = str(callback_name).strip() if callback_name else None

        if element_name:
            callback = self._get_callback(element_name)
            if callback:
                return callback

        if callback_name:
            callback = self._get_callback(callback_name)
            if callback:
                return callback

        if fallback_name:
            return self._get_callback(fallback_name)

        return None

    def _attach_sprite_animation(self, element, props: dict, animations: dict) -> None:
        """
        Attach sprite animation to a UI element.
        
        Args:
            element: UI element instance to attach animation to
            props: Element properties dict containing 'name'
            animations: Sprite animations dictionary keyed by element name
        """
        element_name = props.get('name')
        if element_name and element_name in animations:
            element.set_animation(animations[element_name])

    def _attach_drivers(self, element, props: dict, drivers: dict) -> None:
        """
        Attach animation drivers to a UI element.
        
        Args:
            element: UI element instance to attach drivers to
            props: Element properties dict containing 'name'
            drivers: Animation drivers dictionary keyed by element name
        """
        element_name = props.get('name')
        if element_name and element_name in drivers:
            for driver in drivers[element_name]:
                element.add_driver(driver)

    ## --- ELEMENT FACTORIES (CONFIG-DRIVEN CREATION) --- ##

    def _create_state_elements(self, layout: dict, element_type: str, factory_func, callbacks: dict) -> Dict[str, Dict]:
        """
        Create elements for non-menu states (home/setup/game).
        """
        result = {}
        for state in ["home", "setup", "game"]:
            result[state] = {}
            if state in layout and element_type in layout[state]:
                elements_list = layout[state][element_type]
                for element_props in elements_list:
                    name = element_props.get('name')
                    element = factory_func(element_props, callbacks, state, None)
                    if element:
                        result[state][name] = element
        return result

    def _resolve_menu_tabs(self, menu_config: dict, element_config, default_tabs: list[str]) -> list[str]:
        """
        Resolve tab names for a menu from config.
        """
        tabs_from_menu = menu_config.get("tabs", [])
        if not isinstance(tabs_from_menu, list):
            tabs_from_menu = []

        tabs = list(tabs_from_menu)
        if isinstance(element_config, dict):
            for tab_name in element_config.keys():
                if tab_name not in tabs:
                    tabs.append(tab_name)

        if not tabs:
            tabs = list(element_config.keys()) if isinstance(element_config, dict) else default_tabs

        return tabs

    def _create_menu_elements(self, layout: dict, element_type: str, factory_func, callbacks: dict) -> Dict[str, Dict]:
        """
        Create elements for menu tabs (multi-menu support).
        """
        result = {"menus": {}}
        default_tabs = ["tabs", "input", "accessibility", "graphics", "audio", "gameplay"]

        menus = layout.get("menus", [])
        if isinstance(menus, list):
            for menu_config in menus:
                menu_name = menu_config.get("name", "menu")
                element_config = menu_config.get(element_type, {})
                tabs = self._resolve_menu_tabs(menu_config, element_config, default_tabs)

                result["menus"][menu_name] = {tab: {} for tab in tabs}

                if isinstance(element_config, dict):
                    for tab in tabs:
                        tab_elements = element_config.get(tab, {})
                        if isinstance(tab_elements, dict):
                            for name, element_props in tab_elements.items():
                                element = factory_func(element_props, callbacks, "menu", tab)
                                if element:
                                    result["menus"][menu_name][tab][name] = element
                        elif isinstance(tab_elements, list):
                            for element_props in tab_elements:
                                name = element_props.get("name")
                                element = factory_func(element_props, callbacks, "menu", tab)
                                if element:
                                    result["menus"][menu_name][tab][name] = element

        return result

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
                    "menus": {
                        "settings": {
                            "tabs": {name: element, ...},
                            "input": {name: element, ...},
                            "accessibility": {name: element, ...},
                            "graphics": {name: element, ...},
                            "audio": {name: element, ...},
                            "gameplay": {name: element, ...}
                        }
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
            return {"home": {}, "setup": {}, "game": {}, "menus": {}}

        result = self._create_state_elements(layout, element_type, factory_func, callbacks)
        menu_result = self._create_menu_elements(layout, element_type, factory_func, callbacks)

        result.update(menu_result)
        return result
    
    def create_all_buttons(self, callbacks, animations: dict, drivers: dict):
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
        - If still no callback, button is created without callback (visual only)
        """
        self.register_callbacks(callbacks)
        
        def button_factory(props, cbs, state, tab):
            button_name = str(props.get('name', '')).strip()
            callback = self._resolve_callback(props)

            button = Button(props, self.game_manager.font, self.game_manager, callback=callback)
            
            # Attach sprite animation and drivers
            self._attach_sprite_animation(button, props, animations)
            self._attach_drivers(button, props, drivers)
            
            return button
        
        result = self._create_elements_from_layout('buttons', button_factory, callbacks)
        
        # Note: Tab buttons should always be loaded from layout.json
        # If no tabs found in config, the layout.json is incomplete
        menu_tabs = {}
        menus_result = result.get("menus", {})
        if isinstance(menus_result, dict):
            settings_menu_tabs = menus_result.get("settings", {}).get("tabs", {})
            if isinstance(settings_menu_tabs, dict):
                menu_tabs = settings_menu_tabs
            elif menus_result:
                first_menu = next(iter(menus_result.values()))
                if isinstance(first_menu, dict):
                    menu_tabs = first_menu.get("tabs", {}) if isinstance(first_menu.get("tabs", {}), dict) else {}

        if not menu_tabs:
            print("Warning: No tab buttons found in layout.json. Menu tabs will not work.")
        
        return result

    def create_all_sliders(self, callbacks, animations: dict, drivers: dict) -> Dict[str, Dict]:
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
            
            slider = Slider(props, initial_value, self.game_manager, None)
            
            callback_name = props.get('callback')
            callback_name = str(callback_name).strip() if callback_name else None
            element_name = str(props.get('name', '')).strip()

            # Handle special callbacks that need the slider value parameter
            if callback_name == 'set_player_num' or element_name == 'player_num_slider':
                slider.callback = lambda s=slider: cbs['set_player_num'](int(s.value))
            else:
                slider.callback = self._resolve_callback(props)
            
            # Attach sprite animation and drivers
            self._attach_sprite_animation(slider, props, animations)
            self._attach_drivers(slider, props, drivers)
            
            return slider
        
        return self._create_elements_from_layout('sliders', slider_factory, callbacks)

    def create_all_toggles(self, callbacks, animations: dict, drivers: dict) -> Dict[str, Dict]:
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
            callback = self._resolve_callback(props)
            toggle = Toggle(props, self.game_manager.graphics_manager.time, self.game_manager, on=initial_on, callback=callback)
            
            # Attach sprite animation and drivers
            self._attach_sprite_animation(toggle, props, animations)
            self._attach_drivers(toggle, props, drivers)
            
            return toggle
        
        return self._create_elements_from_layout('toggles', toggle_factory, callbacks)

    def create_all_images(self, callbacks, animations: dict, drivers: dict) -> Dict[str, Dict]:
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
            callback = self._resolve_callback(props)
            image = Image(props, self.game_manager, callback=callback)
            
            # Attach sprite animation and drivers
            self._attach_sprite_animation(image, props, animations)
            self._attach_drivers(image, props, drivers)
                    
            return image
        
        return self._create_elements_from_layout('images', image_factory, callbacks)

    def create_all_text_displays(self, callbacks, animations: dict, drivers: dict) -> Dict[str, Dict]:
        """
        Create all text display elements dynamically from layout config.
        
        Args:
            callbacks: Dict of callback functions from InputManager
        
        Returns:
            Dict[str, Dict]: TextDisplay instances organized by state and tab
        
        TextDisplay Configuration:
        - callback: Optional function called when text is clicked (for interactive text)
        - Uses game_manager.font for rendering
        - Can display static text or dynamic text (updated via callback)
        """
        def text_display_factory(props, cbs, state, tab):
            callback = self._resolve_callback(props)
            text_display = TextDisplay(props, self.game_manager, self.game_manager.font, callback=callback)
            
            # Attach sprite animation and drivers
            self._attach_sprite_animation(text_display, props, animations)
            self._attach_drivers(text_display, props, drivers)
            
            return text_display
        
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
    
    def create_all_scrollable_areas(self, callbacks, animations: dict, drivers: dict) -> Dict[str, Dict]:
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

        # Support both old (single menu) and new (multi-menu) element collections
        buttons_by_menu = buttons.get("menus", {}) if isinstance(buttons, dict) else {}
        toggles_by_menu = toggles.get("menus", {}) if isinstance(toggles, dict) else {}
        sliders_by_menu = sliders.get("menus", {}) if isinstance(sliders, dict) else {}
        images_by_menu = images.get("menus", {}) if isinstance(images, dict) else {}
        text_displays_by_menu = text_displays.get("menus", {}) if isinstance(text_displays, dict) else {}

        if layout and "menus" in layout and isinstance(layout["menus"], list):
            for menu_config in layout["menus"]:
                menu_name = menu_config.get("name", "menu")

                menu_buttons = buttons_by_menu.get(menu_name, buttons)
                menu_toggles = toggles_by_menu.get(menu_name, toggles)
                menu_sliders = sliders_by_menu.get(menu_name, sliders)
                menu_images = images_by_menu.get(menu_name, images)
                menu_text_displays = text_displays_by_menu.get(menu_name, text_displays)

                menu = Menu(
                    layout_props=menu_config,
                    game_manager=self.game_manager,
                    buttons=menu_buttons,
                    toggles=menu_toggles,
                    sliders=menu_sliders,
                    images=menu_images,
                    text_displays=menu_text_displays
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

