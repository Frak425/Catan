import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_manager import GameManager
    from src.managers.input.helper.mouse_input_handler import MouseInputHandler
    from input_manager import InputManager

from src.ui.elements.scrollable_area import ScrollableArea
from src.ui.elements.image import Image
from src.ui.elements.toggle import Toggle
from src.ui.elements.slider import Slider
from src.ui.elements.button import Button
from src.ui.elements.text_display import TextDisplay
from src.ui.elements.menu import Menu


class DevModeHandler:
    """Handles all developer mode functionality including typing and command parsing."""
    game_manager: 'GameManager'
    mouse_handler: 'MouseInputHandler'
    def __init__(self):
        # Manager references (set after initialization)
        pass

    def set_managers(self, game_manager: 'GameManager', mouse_handler: 'MouseInputHandler', input_manager: 'InputManager'):
        """Set manager references."""
        self.game_manager = game_manager
        self.mouse_handler = mouse_handler
        self.input_manager = input_manager

    def add_letter_key(self, key: int) -> None:
        """Add a letter key to the dev mode text input."""
        if not self.game_manager.dev_mode_typing:
            return
            
        key_map = {
            pygame.K_a: "a", pygame.K_b: "b", pygame.K_c: "c", pygame.K_d: "d",
            pygame.K_e: "e", pygame.K_f: "f", pygame.K_g: "g", pygame.K_h: "h",
            pygame.K_i: "i", pygame.K_j: "j", pygame.K_k: "k", pygame.K_l: "l",
            pygame.K_m: "m", pygame.K_n: "n", pygame.K_o: "o", pygame.K_p: "p",
            pygame.K_q: "q", pygame.K_r: "r", pygame.K_s: "s", pygame.K_t: "t",
            pygame.K_u: "u", pygame.K_v: "v", pygame.K_w: "w", pygame.K_x: "x",
            pygame.K_y: "y", pygame.K_z: "z"
        }
        
        if key in key_map:
            self.game_manager.dev_mode_text += key_map[key]

    def add_number_key(self, key: int) -> None:
        """Add a number key to the dev mode text input."""
        if not self.game_manager.dev_mode_typing:
            return
            
        key_map = {
            pygame.K_0: "0", pygame.K_1: "1", pygame.K_2: "2", pygame.K_3: "3",
            pygame.K_4: "4", pygame.K_5: "5", pygame.K_6: "6", pygame.K_7: "7",
            pygame.K_8: "8", pygame.K_9: "9"
        }
        
        if key in key_map:
            self.game_manager.dev_mode_text += key_map[key]

    def add_special_key(self, key: int) -> None:
        """Add a special character key to the dev mode text input."""
        if not self.game_manager.dev_mode_typing:
            return
            
        key_map = {
            pygame.K_COMMA: ",",
            pygame.K_PERIOD: ".",
            pygame.K_MINUS: "-",
            pygame.K_PLUS: "+",
            pygame.K_EQUALS: "=",
            pygame.K_SLASH: "/",
            pygame.K_BACKSLASH: "\\",
            pygame.K_COLON: ":",
            pygame.K_SEMICOLON: ";",
            pygame.K_UNDERSCORE: "_",
            pygame.K_SPACE: " "
        }
        
        if key in key_map:
            self.game_manager.dev_mode_text += key_map[key]

    def update_ui(self):
        self.input_manager.mouse_handler.set_ui_elements(
            self.input_manager.buttons,
            self.input_manager.toggles,
            self.input_manager.sliders,
            self.input_manager.images,
            self.input_manager.text_displays,
            self.input_manager.scrollable_areas,
            self.input_manager.menu
        )
    """
        Parse and execute dev mode commands.
        
        Available commands:
        Position & Size:
        - x+number -> set x position. Example: x150
        - y+number -> set y position. Example: y300
        - w+number -> set width. Example: w200
        - h+number -> set height. Example: h100
        
        Colors:
        - c+r,g,b -> set background/fill color. Example: c255,0,0 (red)
        - tc+r,g,b -> set text color. Example: tc0,255,0 (green)
        - hc+r,g,b -> set handle color (toggles). Example: hc100,100,100
        
        Text:
        - t+text -> set text. Example: tHello World
        - fs+number -> set font size. Example: fs24
        - align+value -> set text alignment (left/center/right). Example: aligncenter
        
        Slider:
        - sv+number -> set slider value. Example: sv75
        - smin+number -> set slider min value. Example: smin0
        - smax+number -> set slider max value. Example: smax200
        
        Toggle:
        - ton -> turn toggle on
        - toff -> turn toggle off
        - tflip -> flip toggle state
        
        General:
        - n+name -> set element name. Example: nmy_button
        - a+number -> set alpha/opacity (0-255). Example: a200
        - del -> delete active element
        - radius+type(opt)+number -> set border radius. Example: radius10, radiustop_left5
        
        System:
        - add+type -> add new element (button/slider/toggle/image/text_display)
        - overridel -> save layout config
        - overrides -> save settings config
        - refreshui -> refresh UI elements
        - centertext -> center text in element
        """
        
    def parse_typing(self) -> None:
        """Parse and execute dev mode commands."""
        text = self.game_manager.dev_mode_text
        print(f"Dev Mode Command: {text}")
        
        # Commands that don't require an active element
        if text.startswith("add"):
            self._handle_add_element(text)
            return
        elif text == "overridel":
            self.game_manager.save_config("layout", True)
            return
        elif text == "overrides":
            self.game_manager.save_config("settings", True)
            return
        elif text == "refreshui":
            self.game_manager.input_manager.reset_ui()
            return
        elif text == "toggle_debug":
            self.game_manager.debugging = not self.game_manager.debugging
            return
        
        if not self.mouse_handler.active:
            print("No active element selected.")
            return
        
        # Use command mapping for cleaner parsing
        self._execute_command(text)

    def _execute_command(self, text: str) -> None:
        """Execute command using pattern matching and dynamic attribute setting."""
        assert self.mouse_handler.active is not None, "No active element selected."
        # Direct attribute setting: attr_name+value
        # Examples: x100, y50, w200, h150
        simple_attrs = {
            'x': ('rect.x', int),
            'y': ('rect.y', int),
            'w': ('rect.width', int),
            'h': ('rect.height', int),
        }
        
        for prefix, (attr_path, value_type) in simple_attrs.items():
            if text.startswith(prefix) and text[len(prefix):].lstrip('-').isdigit():
                self._set_nested_attr(attr_path, value_type(text[len(prefix):]))
                return
        
        # Color commands: c+r,g,b
        if text.startswith("tc") and ',' in text:
            self._set_color_attr('text_color', text[2:])
        elif text.startswith("hc") and ',' in text:
            self._set_color_attr('handle_color', text[2:])
        elif text.startswith("c") and ',' in text:
            self._set_color_attr('color', text[1:])
        
        # Slider commands
        elif text.startswith("smin"):
            self._set_attr('min_value', int(text[4:]))
        elif text.startswith("smax"):
            self._set_attr('max_value', int(text[4:]))
        elif text.startswith("sv"):
            self._set_slider_value(text)
        
        # Toggle commands
        elif text == "ton":
            self._set_attr('on', True)
        elif text == "toff":
            self._set_attr('on', False)
        elif text == "tflip":
            if isinstance(self.mouse_handler.active, Toggle):
                self.mouse_handler.active.on = not self.mouse_handler.active.on
        
        # Text command
        elif text.startswith("t") and not text.startswith("tc"):
            self._set_text(text)
        
        # Other commands...
        elif text == "del":
            self._delete_active()
        elif text == "print_info":
            self.mouse_handler.active.print_info()
        """
            elif text == "centertext":
            self._center_text()
        """
        if isinstance(self.mouse_handler.active, ScrollableArea):
            self.mouse_handler.active.calculate_dependent_properties()

    def _set_attr(self, attr_name: str, value) -> None:
        """Dynamically set an attribute if it exists."""
        if hasattr(self.mouse_handler.active, attr_name):
            setattr(self.mouse_handler.active, attr_name, value)
            print(f"Set {attr_name} to {value}")
        else:
            print(f"Active element does not have attribute: {attr_name}")

        if isinstance(self.mouse_handler.active, ScrollableArea):
            self.mouse_handler.active.calculate_dependent_properties()

    def _set_nested_attr(self, attr_path: str, value) -> None:
        """Set nested attributes like 'rect.x'."""
        parts = attr_path.split('.')
        obj = self.mouse_handler.active
        
        # Navigate to the parent object
        for part in parts[:-1]:
            if not hasattr(obj, part):
                print(f"Attribute path not found: {attr_path}")
                return
            obj = getattr(obj, part)
        
        # Set the final attribute
        final_attr = parts[-1]
        if hasattr(obj, final_attr):
            setattr(obj, final_attr, value)
            print(f"Set {attr_path} to {value}")
        else:
            print(f"Attribute not found: {attr_path}")

        if isinstance(self.mouse_handler.active, ScrollableArea):
            self.mouse_handler.active.calculate_dependent_properties()

    def _set_color_attr(self, attr_name: str, color_str: str) -> None:
        """Set a color attribute from comma-separated RGB string."""
        try:
            r, g, b = map(int, color_str.split(','))
            self._set_attr(attr_name, (r, g, b))
            
            # Special handling for text color to regenerate surface
            if attr_name == 'text_color' and isinstance(self.mouse_handler.active, (TextDisplay, Button)):
                if isinstance(self.mouse_handler.active, TextDisplay):
                    self.mouse_handler.active.text_surface = self.mouse_handler.active.font.render(
                        self.mouse_handler.active.text, True, self.mouse_handler.active.text_color
                    )
                    self.mouse_handler.active.text_rect = self.mouse_handler.active.text_surface.get_rect()
        except (ValueError, IndexError):
            print(f"Invalid color format. Use: {attr_name[0]}r,g,b")

    def _set_x_position(self, text: str) -> None:
        assert self.mouse_handler.active is not None
        """Set x position of active element."""
        try:
            value = int(text[1:])
            self.mouse_handler.active.rect.x = value
        except ValueError:
            pass

    def _set_y_position(self, text: str) -> None:
        assert self.mouse_handler.active is not None
        """Set y position of active element."""
        try:
            value = int(text[1:])
            self.mouse_handler.active.rect.y = value
        except ValueError:
            pass

    def _set_width(self, text: str) -> None:
        assert self.mouse_handler.active is not None
        """Set width of active element."""
        try:
            value = int(text[1:])
            self.mouse_handler.active.rect.width = value
        except ValueError:
            pass

    def _set_height(self, text: str) -> None:
        assert self.mouse_handler.active is not None
        """Set height of active element."""
        try:
            value = int(text[1:])
            self.mouse_handler.active.rect.height = value
        except ValueError:
            pass

    def _set_text(self, text: str) -> None:
        """Set text of active element."""
        new_text = text[1:]
        if isinstance(self.mouse_handler.active, (TextDisplay, Button)):
            self.mouse_handler.active.update_text(new_text)

    def _set_text_color(self, text: str) -> None:
        """Set text color of active element."""
        try:
            color_values = text[2:].split(",")
            r = int(color_values[0])
            g = int(color_values[1])
            b = int(color_values[2])
            if isinstance(self.mouse_handler.active, (TextDisplay, Button)):
                self.mouse_handler.active.text_color = (r, g, b)
                # Regenerate text surface for TextDisplay
                if isinstance(self.mouse_handler.active, TextDisplay):
                    self.mouse_handler.active.text_surface = self.mouse_handler.active.font.render(
                        self.mouse_handler.active.text, True, self.mouse_handler.active.text_color
                    )
                    self.mouse_handler.active.text_rect = self.mouse_handler.active.text_surface.get_rect()
        except (ValueError, IndexError):
            pass

    def _set_color(self, text: str) -> None:
        """Set background/fill color of active element."""
        try:
            color_values = text[1:].split(",")
            r = int(color_values[0])
            g = int(color_values[1])
            b = int(color_values[2])
            
            # For buttons, text displays, toggles, sliders, and menu
            if isinstance(self.mouse_handler.active, (TextDisplay, Button, Toggle, Slider)):
                self.mouse_handler.active.color = (r, g, b)
            elif isinstance(self.mouse_handler.active, Menu):
                self.mouse_handler.active.bckg_color = (r, g, b)
        except (ValueError, IndexError):
            pass

    def _set_handle_color(self, text: str) -> None:
        """Set handle color for toggles and sliders."""
        try:
            color_values = text[2:].split(",")
            r = int(color_values[0])
            g = int(color_values[1])
            b = int(color_values[2])
            
            if isinstance(self.mouse_handler.active, (Toggle, Slider)):
                self.mouse_handler.active.handle_color = (r, g, b)
        except (ValueError, IndexError):
            pass

    def _set_font_size(self, text: str) -> None:
        """Set font size for text elements."""
        try:
            size = int(text[2:])
            if isinstance(self.mouse_handler.active, (TextDisplay, Button)):
                new_font = pygame.font.Font(None, size)
                self.mouse_handler.active.font = new_font
                
                # Regenerate text surface
                if isinstance(self.mouse_handler.active, TextDisplay):
                    self.mouse_handler.active.text_surface = new_font.render(
                        self.mouse_handler.active.text, True, self.mouse_handler.active.text_color
                    )
                    self.mouse_handler.active.text_rect = self.mouse_handler.active.text_surface.get_rect()
                elif isinstance(self.mouse_handler.active, Button):
                    self.mouse_handler.active.update_text(self.mouse_handler.active.text)
        except ValueError:
            pass

    def _set_alignment(self, text: str) -> None:
        """Set text alignment for text elements."""
        alignment = text[5:].lower()
        if alignment in ["left", "center", "right"]:
            if isinstance(self.mouse_handler.active, (TextDisplay, Button)):
                self.mouse_handler.active.text_align = alignment
                
                # Reposition text based on alignment
                if alignment == "left":
                    self.mouse_handler.active.text_rect.left = self.mouse_handler.active.surface.get_rect().left
                elif alignment == "center":
                    self.mouse_handler.active.text_rect.center = self.mouse_handler.active.surface.get_rect().center
                elif alignment == "right":
                    self.mouse_handler.active.text_rect.right = self.mouse_handler.active.surface.get_rect().right

    def _set_name(self, text: str) -> None:
        """Set name of active element."""
        new_name = text[1:]
        if isinstance(self.mouse_handler.active, (Button, TextDisplay, Slider, Toggle, Image, Menu)):
            self.mouse_handler.active.name = new_name

    def _set_alpha(self, text: str) -> None:
        """Set alpha/opacity of active element."""
        try:
            alpha = int(text[1:])
            alpha = max(0, min(255, alpha))  # Clamp between 0-255
            
            if isinstance(self.mouse_handler.active, (Button, TextDisplay, Image)):
                self.mouse_handler.active.surface.set_alpha(alpha)
        except ValueError:
            pass

    def _set_slider_value(self, text: str) -> None:
        """Set current value of slider."""
        try:
            value = float(text[2:])
            if isinstance(self.mouse_handler.active, Slider):
                self.mouse_handler.active.value = max(
                    self.mouse_handler.active.min_value,
                    min(self.mouse_handler.active.max_value, value)
                )
        except ValueError:
            pass

    def _set_slider_min(self, text: str) -> None:
        """Set minimum value of slider."""
        try:
            min_val = int(text[4:])
            if isinstance(self.mouse_handler.active, Slider):
                self.mouse_handler.active.min_value = min_val
                # Ensure current value is still valid
                if self.mouse_handler.active.value < min_val:
                    self.mouse_handler.active.value = min_val
        except ValueError:
            pass

    def _set_slider_max(self, text: str) -> None:
        """Set maximum value of slider."""
        try:
            max_val = int(text[4:])
            if isinstance(self.mouse_handler.active, Slider):
                self.mouse_handler.active.max_value = max_val
                # Ensure current value is still valid
                if self.mouse_handler.active.value > max_val:
                    self.mouse_handler.active.value = max_val
        except ValueError:
            pass

    def _toggle_on(self) -> None:
        """Turn toggle on."""
        if isinstance(self.mouse_handler.active, Toggle):
            self.mouse_handler.active.on = True

    def _toggle_off(self) -> None:
        """Turn toggle off."""
        if isinstance(self.mouse_handler.active, Toggle):
            self.mouse_handler.active.on = False

    def _toggle_flip(self) -> None:
        """Flip toggle state."""
        if isinstance(self.mouse_handler.active, Toggle):
            self.mouse_handler.active.on = not self.mouse_handler.active.on

    def _set_border_radius(self, text: str) -> None:
        """Set border radius of active element."""
        try:
            radius = int(text[1:])
            if isinstance(self.mouse_handler.active, (Button, TextDisplay)):
                self.mouse_handler.active.border_radius = radius
        except ValueError:
            pass

    def _set_border_top_left_radius(self, text: str) -> None:
        """Set top left border radius of active element."""
        try:
            radius = int(text[4:])
            if isinstance(self.mouse_handler.active, (Button, TextDisplay)):
                self.mouse_handler.active.border_top_left_radius = radius
        except ValueError:
            pass

    def _set_border_top_right_radius(self, text: str) -> None:
        """Set top right border radius of active element."""
        try:
            radius = int(text[5:])
            if isinstance(self.mouse_handler.active, (Button, TextDisplay)):
                self.mouse_handler.active.border_top_right_radius = radius
        except ValueError:
            pass

    def _set_border_bottom_left_radius(self, text: str) -> None:
        """Set bottom left border radius of active element."""
        try:
            radius = int(text[5:])
            if isinstance(self.mouse_handler.active, (Button, TextDisplay)):
                self.mouse_handler.active.border_bottom_left_radius = radius
        except ValueError:
            pass

    def _set_border_bottom_right_radius(self, text: str) -> None:
        """Set bottom right border radius of active element."""
        try:
            radius = int(text[6:])
            if isinstance(self.mouse_handler.active, (Button, TextDisplay)):
                self.mouse_handler.active.border_bottom_right_radius = radius
        except ValueError:
            pass

    def _delete_active(self) -> None:
        """Delete the currently active UI element."""
        if not self.mouse_handler.active:
            return
        
        # Don't allow deleting the menu itself
        if isinstance(self.mouse_handler.active, Menu):
            print("Cannot delete menu")
            return
        
        # Determine which collection the active element belongs to
        collections = [
            self.input_manager.buttons,
            self.input_manager.toggles,
            self.input_manager.sliders,
            self.input_manager.images,
            self.input_manager.text_displays,
        ]
        
        for collection in collections:
            for state, elements in collection.items():
                if state == "menu":
                    # For buttons in menu tabs
                    for tab, tab_elements in elements.items():
                        if self.mouse_handler.active.name in tab_elements:
                            del tab_elements[self.mouse_handler.active.name]
                            self.mouse_handler.active = None
                            return
                else:
                    # For lists of elements
                    if self.mouse_handler.active.name in elements:
                        del elements[self.mouse_handler.active.name]
                        self.mouse_handler.active = None
                        return
        
    def _handle_add_element(self, text: str) -> None:
        """Handle adding new UI elements."""
        import time
        element_type = text[3:]
        
        # Generate unique name with timestamp
        timestamp = int(time.time() * 1000) % 100000

        elements_by_type = {
            "button": self.input_manager.buttons,
            "slider": self.input_manager.sliders,
            "image": self.input_manager.images,
            "text_display": self.input_manager.text_displays,
            "toggle": self.input_manager.toggles
        }
        
        if element_type == "button":
            layout_props = {
                "name": f"new_button_{timestamp}",
                "rect": [100, 100, 150, 50],
                "color": [0, 100, 0],
                "text": "new button",
            }
            new_element = Button(layout_props, self.game_manager.game_font, self.game_manager, callback=None, shown=True)
        
        elif element_type == "slider":
            layout_props = {
                "name": f"new_slider_{timestamp}",
                "rect": [100, 100, 200, 40],
                "color": [100, 0, 0],
                "min_value": 0,
                "max_value": 100,
                "initial_value": 50,
                "handle_color": [200, 200, 200],
                "color": [100, 0, 0],
            }
            new_element = Slider(layout_props, 50, self.game_manager)
        
        elif element_type == "text_display":
            layout_props = {
                "name": f"new_text_display_{timestamp}",
                "rect": [100, 100, 200, 50],
                "color": [200, 200, 200],
                "text": "new text display",
            }
            new_element = TextDisplay(layout_props, self.game_manager, self.game_manager.game_font, shown=True)
        
        elif element_type == "image":
            layout_props = {
                "name": f"new_image_{timestamp}",
                "rect": [100, 100, 100, 100],
                "image_path": "path/to/image.png",
            }
            new_element = Image(layout_props, self.game_manager)
        
        elif element_type == "toggle":
            layout_props = {
                "name": f"new_toggle_{timestamp}",
                "rect": [100, 100, 150, 50],
                "guiding_lines": self.game_manager.default_guiding_lines,
                "height": self.game_manager.default_height,
                "center_width": self.game_manager.default_center_width,
                "color": list(self.game_manager.default_fill_color),
                "handle_color": list(self.game_manager.default_handle_color),
                "toggle_gap": self.game_manager.default_toggle_gap,
                "time_to_flip": self.game_manager.default_time_to_flip
            }
            new_element = Toggle(layout_props, self.game_manager.graphics_manager.time, self.game_manager, on=False, callback=None, shown=True)
            
        else:
            print(f"Unknown element type: {element_type}")
            return

        if self.input_manager.menu.open:
            tab = self.input_manager.menu.active_tab
            if tab not in elements_by_type[element_type]["menu"]:
                elements_by_type[element_type]["menu"][tab] = {}
            elements_by_type[element_type]["menu"][tab][new_element.name] = new_element
        else:
            state = self.game_manager.game_state
            if state not in self.input_manager.buttons:
                elements_by_type[element_type][state] = {}
            elements_by_type[element_type][state][new_element.name] = new_element

        self.update_ui()
        print(f"Added {new_element.__class__.__name__}: {new_element.name}")