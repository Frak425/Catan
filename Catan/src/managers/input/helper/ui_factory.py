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
        
        # Load menu state (with tabs)
        menu_tabs = ["tabs", "input", "accessibility", "graphics", "audio", "gameplay"]
        result["menu"] = {tab: {} for tab in menu_tabs}
        if "menu" in layout:
            for tab in menu_tabs:
                if tab in layout["menu"] and element_type in layout["menu"][tab]:
                    for element_props in layout["menu"][tab][element_type]:
                        name = element_props.get('name')
                        element = factory_func(element_props, callbacks, "menu", tab)
                        if element:
                            result["menu"][tab][name] = element
        
        return result

    # --- DYNAMIC CONFIG-DRIVEN CREATION --- #

    def create_all_buttons(self, callbacks):
        """Create all buttons dynamically from config files."""
        self.register_callbacks(callbacks)
        
        def button_factory(props, cbs, state, tab):
            callback_name = props.get('callback')
            callback = self._get_callback(callback_name) if callback_name else None
            return Button(props, self.game_manager.game_font, self.game_manager, callback=callback)
        
        result = self._create_elements_from_layout('buttons', button_factory, callbacks)
        
        # Load menu tab buttons from config (or create defaults if not present)
        layout = getattr(self.game_manager, 'layout', None)
        if layout and "menu" in layout and "tabs" in layout["menu"] and 'buttons' in layout["menu"]["tabs"]:
            # Load from config
            result["menu"]["tabs"] = {}
            for button_props in layout["menu"]["tabs"]['buttons']:
                name = button_props.get('name')
                callback_name = button_props.get('callback')
                callback = self._get_callback(callback_name) if callback_name else None
                button = Button(button_props, self.game_manager.game_font, self.game_manager, callback=callback)
                result["menu"]["tabs"][name] = button
        else:
            # Create default tab buttons if not in config
            result["menu"]["tabs"] = {
                "input": Button(
                    {"name": "input", "rect": [300, self.game_manager.menu_tab_margin_top, self.game_manager.menu_input_tab_size[0], self.game_manager.menu_input_tab_size[1]], "color": [100, 0, 0], "text": "Input"},
                    self.game_manager.game_font, self.game_manager, callback=callbacks['change_tab_input']
                ),
                "accessibility": Button(
                    {"name": "accessibility", "rect": [400, self.game_manager.menu_tab_margin_top, self.game_manager.menu_accessibility_tab_size[0], self.game_manager.menu_accessibility_tab_size[1]], "color": [100, 0, 0], "text": "Accessibility"},
                    self.game_manager.game_font, self.game_manager, callback=callbacks['change_tab_accessibility']
                ),
                "gameplay": Button(
                    {"name": "gameplay", "rect": [self.game_manager.menu_size[0] / 2 - self.game_manager.menu_gameplay_tab_size[0] / 2, self.game_manager.menu_tab_margin_top, self.game_manager.menu_gameplay_tab_size[0], self.game_manager.menu_gameplay_tab_size[1]], "color": [100, 0, 0], "text": "Gameplay"},
                    self.game_manager.game_font, self.game_manager, callback=callbacks['change_tab_gameplay']
                ),
                "audio": Button(
                    {"name": "audio", "rect": [700, self.game_manager.menu_tab_margin_top, self.game_manager.menu_audio_tab_size[0], self.game_manager.menu_audio_tab_size[1]], "color": [100, 0, 0], "text": "Audio"},
                    self.game_manager.game_font, self.game_manager, callback=callbacks['change_tab_audio']
                ),
                "graphics": Button(
                    {"name": "graphics", "rect": [800, self.game_manager.menu_tab_margin_top, self.game_manager.menu_graphics_tab_size[0], self.game_manager.menu_graphics_tab_size[1]], "color": [100, 0, 0], "text": "Graphics"},
                    self.game_manager.game_font, self.game_manager, callback=callbacks['change_tab_graphics']
                ),
                "close_menu": Button(
                    {"name": "close_menu", "rect": [self.game_manager.menu_size[0] - self.game_manager.close_menu_size[0] - self.game_manager.close_menu_margins[0], self.game_manager.close_menu_margins[1], self.game_manager.close_menu_size[0], self.game_manager.close_menu_size[1]], "color": [100, 0, 0], "text": "Close"},
                    self.game_manager.game_font, self.game_manager, callback=callbacks['close_menu']
                )
            }
        
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

    # --- MENU CREATION --- #

    def create_menu(self, buttons, toggles, sliders) -> Menu:
        """Create the main menu."""
        menu = Menu(
            self.game_manager.menu_rect,
            self.game_manager.game_font,
            buttons["menu"],
            toggles["menu"],
            sliders["menu"],
            self.game_manager.init_location,
            self.game_manager.final_location,
            bckg_color=self.game_manager.menu_background_color
        )
        return menu

