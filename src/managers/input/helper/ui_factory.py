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
                    element = factory_func(element_props, callbacks, state)
                    if element:
                        result[state][name] = element
        return result

    def _resolve_menu_tabs(self, menu_config: dict, element_config) -> list[str]:
        """
        Resolve tab names for a menu from config.
        """
        # getting the list of tab names (menus -> tabs)
        tabs_from_menu = menu_config.get("tabs", [])
        if not isinstance(tabs_from_menu, list):
            tabs_from_menu = []


        tabs = list(tabs_from_menu)
        if isinstance(element_config, dict):
            for tab_name in element_config.keys():
                if tab_name not in tabs:
                    tabs.append(tab_name)

        if not tabs:
            tabs = list(element_config.keys()) if isinstance(element_config, dict) else []

        return tabs

    def _create_menu_elements(self, layout: dict, element_type: str, factory_func, callbacks: dict) -> Dict[str, Dict[str, Menu]]:
        """
        Create menu instances for each game-state section.

        The new layout structure stores menus inside the same state sections
        as other UI elements (home/setup/game). For transition support, this
        also accepts the legacy top-level `menus` array when state sections do
        not contain menu objects yet.
        """
        result: Dict[str, Dict[str, Menu]] = {"home": {}, "setup": {}, "game": {}}

        if not isinstance(layout, dict):
            return result

        legacy_menus = layout.get("menus", [])
        legacy_menu_lookup = {}
        if isinstance(legacy_menus, list):
            for menu_config in legacy_menus:
                if isinstance(menu_config, dict):
                    menu_name = menu_config.get("name")
                    if menu_name:
                        legacy_menu_lookup[menu_name] = menu_config

        for state in ["home", "setup", "game"]:
            state_menu_configs = []
            state_layout = layout.get(state, {})
            if isinstance(state_layout, dict):
                menus_from_state = state_layout.get("menus", [])
                if isinstance(menus_from_state, list):
                    for menu_config in menus_from_state:
                        if isinstance(menu_config, dict):
                            state_menu_configs.append(menu_config)
                        elif isinstance(menu_config, str) and menu_config in legacy_menu_lookup:
                            state_menu_configs.append(legacy_menu_lookup[menu_config])

            # Backward compatibility: if the state has no embedded menus yet,
            # fall back to any menu objects declared at the top level.
            if not state_menu_configs and legacy_menu_lookup:
                state_menu_configs = list(legacy_menu_lookup.values())

            for menu_config in state_menu_configs:
                menu_name = menu_config.get("name", "menu")
                menu = factory_func(menu_config, callbacks, state)
                if menu:
                    result[state][menu_name] = menu

        return result

    def _create_elements_from_layout(self, element_type: str, factory_func, callbacks: dict) -> Dict[str, Dict]:
        """
        Generic helper to create UI elements from layout config using factory pattern.
        
        Args:
            element_type: Type of elements to create ('buttons', 'sliders', etc.)
            factory_func: Factory function that creates individual elements
                         Signature: (props, callbacks, state) -> UIElement
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
          4. Menus are handled separately by create_all_menus() because they now
              live inside each state section instead of a top-level bucket
        5. For each tab, extract elements dict and create elements
        
        Note: Non-menu states use arrays of elements, menu tabs use dicts keyed by name
        """
        layout = getattr(self.game_manager, 'layout', None)
        if not layout:
            return {"home": {}, "setup": {}, "game": {}}

        result = self._create_state_elements(layout, element_type, factory_func, callbacks)

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
        #TODO: move to appropiate init place
        self.register_callbacks(callbacks)
        
        def button_factory(props, cbs, state):
            button_name = str(props.get('name', '')).strip()
            callback = self._resolve_callback(props)

            button = Button(props, self.game_manager.font, self.game_manager, callback=callback)
            
            # Attach sprite animation and drivers
            self._attach_sprite_animation(button, props, animations)
            self._attach_drivers(button, props, drivers)
            
            return button
        
        result = self._create_elements_from_layout('buttons', button_factory, callbacks)
        
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
        def slider_factory(props, cbs, state):
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
        def toggle_factory(props, cbs, state):
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
        def image_factory(props, cbs, state):
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
        def text_display_factory(props, cbs, state):
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
        def scrollable_area_factory(props, cbs, state):
            content_height = props.get('content_height', 600)
            content_width = props.get('viewable_content_width', 200)
            content_surface = self._create_test_gradient_surface(content_width, content_height)
            
            return ScrollableArea(props, self.game_manager, content_surface)
        
        return self._create_elements_from_layout('scrollable_areas', scrollable_area_factory, callbacks)

    ## --- MENU ASSEMBLY --- ##
    
    def create_all_menus(self, buttons, toggles, sliders, images, text_displays, callbacks, animations: dict, drivers: dict) -> dict[str, dict]:
        """
        Create all menus from state-level layout sections and assemble UI elements.
        
        Args:
            buttons: All created button instances (organized by state/tab)
            toggles: All created toggle instances (organized by state/tab)
            sliders: All created slider instances (organized by state/tab)
            images: All created image instances (organized by state/tab)
            text_displays: All created text display instances (organized by state/tab)
        
        Returns:
            dict[str, dict[str, Menu]]: Menu instances keyed by state then menu name
        
        Process:
        1. Read menus from each state section (home/setup/game)
        2. Fall back to top-level menus for older layout files
        3. For each menu config, create a Menu instance with all element collections
        4. Menu class handles filtering elements for its tabs
        
        Menu Structure:
        - Each Menu contains tabs (input, accessibility, graphics, audio, gameplay)
        - Tabs contain filtered subsets of buttons, toggles, sliders, etc.
        - Menu handles rendering and tab switching logic
        """

        def _build_collection(collection_config, element_factory):
            result = {}
            if not isinstance(collection_config, dict):
                return result

            for tab_name, tab_elements in collection_config.items():
                tab_result = {}

                if isinstance(tab_elements, dict):
                    iterable = tab_elements.items()
                elif isinstance(tab_elements, list):
                    iterable = ((element_props.get("name"), element_props) for element_props in tab_elements if isinstance(element_props, dict))
                else:
                    iterable = []

                for element_name, element_props in iterable:
                    if not isinstance(element_props, dict):
                        continue
                    if not element_name:
                        element_name = element_props.get("name")
                    if not element_name:
                        continue

                    element = element_factory(element_props)
                    if element:
                        tab_result[element_name] = element

                result[tab_name] = tab_result

            return result

        def menu_factory_func(props, cbs, state):
            buttons_config = props.get("buttons", {})
            toggles_config = props.get("toggles", {})
            sliders_config = props.get("sliders", {})
            images_config = props.get("images", {})
            text_displays_config = props.get("text_displays", {})

            def button_element_factory(element_props):
                callback = self._resolve_callback(element_props)
                button = Button(element_props, self.game_manager.font, self.game_manager, callback=callback)
                self._attach_sprite_animation(button, element_props, animations)
                self._attach_drivers(button, element_props, drivers)
                return button

            def toggle_element_factory(element_props):
                initial_on = element_props.get('on', self.game_manager.default_on)
                callback = self._resolve_callback(element_props)
                toggle = Toggle(element_props, self.game_manager.graphics_manager.time, self.game_manager, on=initial_on, callback=callback)
                self._attach_sprite_animation(toggle, element_props, animations)
                self._attach_drivers(toggle, element_props, drivers)
                return toggle

            def slider_element_factory(element_props):
                initial_value = element_props.get('initial_value', element_props.get('min_value', 0))
                slider = Slider(element_props, initial_value, self.game_manager, None)

                callback_name = element_props.get('callback')
                callback_name = str(callback_name).strip() if callback_name else None
                element_name = str(element_props.get('name', '')).strip()

                if callback_name == 'set_player_num' or element_name == 'player_num_slider':
                    slider.callback = lambda s=slider: cbs['set_player_num'](int(s.value))
                else:
                    slider.callback = self._resolve_callback(element_props)

                self._attach_sprite_animation(slider, element_props, animations)
                self._attach_drivers(slider, element_props, drivers)
                return slider

            def image_element_factory(element_props):
                callback = self._resolve_callback(element_props)
                image = Image(element_props, self.game_manager, callback=callback)
                self._attach_sprite_animation(image, element_props, animations)
                self._attach_drivers(image, element_props, drivers)
                return image

            def text_display_element_factory(element_props):
                callback = self._resolve_callback(element_props)
                text_display = TextDisplay(element_props, self.game_manager, self.game_manager.font, callback=callback)
                self._attach_sprite_animation(text_display, element_props, animations)
                self._attach_drivers(text_display, element_props, drivers)
                return text_display

            buttons_by_tab = _build_collection(buttons_config, button_element_factory)
            toggles_by_tab = _build_collection(toggles_config, toggle_element_factory)
            sliders_by_tab = _build_collection(sliders_config, slider_element_factory)
            images_by_tab = _build_collection(images_config, image_element_factory)
            text_displays_by_tab = _build_collection(text_displays_config, text_display_element_factory)

            menu = Menu(props, self.game_manager, buttons_by_tab, toggles_by_tab, sliders_by_tab, images_by_tab, text_displays_by_tab)
            self._attach_sprite_animation(menu, props, animations)
            self._attach_drivers(menu, props, drivers)
            return menu

        layout = getattr(self.game_manager, 'layout', None)
        if not layout:
            return {"home": {}, "setup": {}, "game": {}}

        return self._create_menu_elements(layout, 'menus', menu_factory_func, callbacks)
