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
    """Factory class for creating all UI elements (buttons, sliders, toggles, etc.)."""
    
    def __init__(self, game_manager: 'GameManager', input_manager: 'InputManager'):
        self.game_manager = game_manager
        self.input_manager = input_manager
        self.callback_registry = {}
    
    def register_callbacks(self, callbacks: dict):
        """Register all callbacks for UI elements. Called once during initialization."""
        self.callback_registry = callbacks

    def _get_callback(self, callback_name: str):
        """Get a callback function by name from the registry."""
        return self.callback_registry.get(callback_name, None)

    def _get_from_layout(self, element_type: str, state: str, name: str, tab: str | None = None):
        """Helper to retrieve element from layout or return None."""
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
        """Generic helper to create UI elements from layout config."""
        layout = getattr(self.game_manager, 'layout', None)
        if not layout:
            return {"home": {}, "setup": {}, "game": {}, "menu": {"tabs": {}, "input": {}, "accessibility": {}, "graphics": {}, "audio": {}, "gameplay": {}}}
        
        result = {}
        
        # Load non-menu states
        for state in ["home", "setup", "game"]:
            result[state] = {}
            if state in layout and element_type in layout[state]:
                for element_props in layout[state][element_type]:
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

    # --- DYNAMIC CONFIG-DRIVEN CREATION --- #

    def create_all_buttons(self, callbacks):
        """Create all buttons dynamically from config files."""
        self.register_callbacks(callbacks)
        
        # Map button names to their callbacks for when JSON doesn't have callback info
        button_name_to_callback = {
            # Tab buttons
            'input': 'change_tab_input',
            'accessibility': 'change_tab_accessibility',
            'gameplay': 'change_tab_gameplay',
            'audio': 'change_tab_audio',
            'graphics': 'change_tab_graphics',
            'close_menu': 'close_menu'
        }
        
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

    # --- SLIDER CREATION --- #

    def create_all_sliders(self, callbacks) -> Dict[str, Dict]:
        """Create all sliders dynamically from config files."""
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

    # --- TOGGLE CREATION --- #

    def create_all_toggles(self, callbacks) -> Dict[str, Dict]:
        """Create all toggles dynamically from config files."""
        def toggle_factory(props, cbs, state, tab):
            initial_on = props.get('on', self.game_manager.default_on)
            callback_name = props.get('callback')
            callback = self._get_callback(callback_name) if callback_name else None
            return Toggle(props, self.game_manager.graphics_manager.time, self.game_manager, on=initial_on, callback=callback)
        
        return self._create_elements_from_layout('toggles', toggle_factory, callbacks)

    # --- IMAGE CREATION --- #

    def create_all_images(self, callbacks) -> Dict[str, Dict]:
        """Create all images dynamically from config files."""
        def image_factory(props, cbs, state, tab):
            callback_name = props.get('callback')
            callback = self._get_callback(callback_name) if callback_name else None
            return Image(props, self.game_manager, callback=callback)
        
        return self._create_elements_from_layout('images', image_factory, callbacks)

    # --- TEXT DISPLAY CREATION --- #

    def create_all_text_displays(self, callbacks) -> Dict[str, Dict]:
        """Create all text displays dynamically from config files."""
        def text_display_factory(props, cbs, state, tab):
            callback_name = props.get('callback')
            callback = self._get_callback(callback_name) if callback_name else None
            return TextDisplay(props, self.game_manager, self.game_manager.game_font, callback=callback)
        
        return self._create_elements_from_layout('text_displays', text_display_factory, callbacks)

    # --- SCROLLABLE AREA CREATION --- #

    def create_all_scrollable_areas(self, callbacks) -> Dict[str, Dict]:
        """Create all scrollable areas dynamically from config files."""
        def scrollable_area_factory(props, cbs, state, tab):
            # Create a dummy content surface for now - users can replace it
            content_height = props.get('content_height', 600)
            content_width = props.get('viewable_content_width', 200)
            content_surface = pygame.Surface((content_width, content_height))
            
            # Create a vertical gradient to test scroll logic
            start_color = (255, 0, 0)  # Red at top
            end_color = (0, 0, 255)    # Blue at bottom
            for y in range(content_height):
                ratio = y / content_height
                r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
                pygame.draw.line(content_surface, (r, g, b), (0, y), (content_width, y))
            
            return ScrollableArea(props, self.game_manager, content_surface)
        
        return self._create_elements_from_layout('scrollable_areas', scrollable_area_factory, callbacks)

    # --- MENU CREATION --- #

    def create_all_menus(self, buttons, toggles, sliders, images, text_displays) -> dict:
        """Create all menus from menus array in layout. Returns a dict of {name: Menu}."""
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

