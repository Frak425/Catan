import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_manager import GameManager
    from src.managers.input.helper.mouse_input_handler import MouseInputHandler
    from input_manager import InputManager

from src.ui.elements.image import Image
from src.ui.elements.toggle import Toggle
from src.ui.elements.slider import Slider
from src.ui.elements.button import Button
from src.ui.elements.text_display import TextDisplay


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

    def parse_typing(self) -> None:
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
        
        System:
        - add+type -> add new element (button/slider/toggle/image/text_display)
        - overridel -> save layout config
        - overrides -> save settings config
        - refreshui -> refresh UI elements
        - centertext -> center text in element
        """
        if not self.mouse_handler.active:
            return
            
        text = self.game_manager.dev_mode_text
        print(f"Dev Mode Command: {text}")
        
        # Color commands (check tc before t, hc before h)
        if text.startswith("tc"):
            self._set_text_color(text)
        elif text.startswith("hc"):
            self._set_handle_color(text)
        elif text.startswith("c"):
            self._set_color(text)
        
        # Slider commands (check before general s commands)
        elif text.startswith("smin"):
            self._set_slider_min(text)
        elif text.startswith("smax"):
            self._set_slider_max(text)
        elif text.startswith("sv"):
            self._set_slider_value(text)
        
        # Toggle commands (check before general t commands)
        elif text == "ton":
            self._toggle_on()
        elif text == "toff":
            self._toggle_off()
        elif text == "tflip":
            self._toggle_flip()
        
        # Text commands
        elif text.startswith("t") and not text.startswith("tc"):
            self._set_text(text)
        
        # Font size
        elif text.startswith("fs"):
            self._set_font_size(text)
        
        # Alignment
        elif text.startswith("align"):
            self._set_alignment(text)
        
        # Name
        elif text.startswith("n"):
            self._set_name(text)
        
        # Alpha
        elif text.startswith("a"):
            self._set_alpha(text)
        
        # Add elements
        elif text.startswith("add"):
            # Example: addbutton, addtoggle, addslider, addtextdisplay
            element_type = text[3:]
            if element_type == "button":
                layoout_props = {
                    "name": "new_button",
                    "rect": [
                        0, 0, 150, 50
                    ],
                    "color": [0, 100, 0],
                    "text": "new button",
                }
                new_button = Button(layoout_props, self.game_manager.game_font, self.game_manager, callback=None, shown=True)
                if self.input_manager.menu.open:
                    self.game_manager.input_manager.buttons["menu"][self.input_manager.menu.active_tab]["new_button"] = new_button
                else:
                    self.game_manager.input_manager.buttons[self.game_manager.game_state]["new_button"] = new_button

                self.update_ui()
            
            elif element_type == "slider":
                layout_props = {
                    "name": "new_slider",
                    "rect": [
                        0, 0, 200, 40
                    ],
                    "color": [100, 0, 0],
                    "min_value": 0,
                    "max_value": 100,
                    "initial_value": 50,
                }
                new_slider = Slider(layout_props, 50, self.game_manager)
                if self.input_manager.menu.open:
                    self.game_manager.input_manager.sliders["menu"][self.input_manager.menu.active_tab].append(new_slider)
                else:
                    self.game_manager.input_manager.sliders[self.game_manager.game_state]["new_slider"].append(new_slider)
                self.update_ui()
            
            elif element_type == "text_display":
                layout_props = {
                    "name": "new_text_display",
                    "rect": [
                        0, 0, 200, 50
                    ],
                    "color": [200, 200, 200],
                    "text": "new text display",
                }
                new_text_display = TextDisplay(layout_props,self.game_manager, self.game_manager.game_font, shown=True)
                if self.input_manager.menu.open:
                    self.game_manager.input_manager.text_displays["menu"][self.input_manager.menu.active_tab].append(new_text_display)
                else:
                    self.game_manager.input_manager.text_displays[self.game_manager.game_state]["new_text_display"].append(new_text_display)
                
            elif element_type == "image":
                layout_props = {
                    "name": "new_image",
                    "rect": [
                        0, 0, 100, 100
                    ],
                    "image_path": "path/to/image.png",
                }
                # Assuming Image class exists
                new_image = Image(layout_props, self.game_manager)
                if self.input_manager.menu.open:
                    self.game_manager.input_manager.images["menu"][self.input_manager.menu.active_tab].append(new_image)
                else:
                    self.game_manager.input_manager.images[self.game_manager.game_state]["new_image"].append(new_image)
                self.update_ui()
            
            elif element_type == "toggle":
                layout_props = {
                    "name": "new_toggle",
                    "rect": [100, 300, 150, 50], 
                    "guiding_lines": self.game_manager.default_guiding_lines,
                    "height": self.game_manager.default_height, 
                    "center_width": self.game_manager.default_center_width, 
                    "fill_color": list(self.game_manager.default_fill_color),
                    "handle_color": list(self.game_manager.default_handle_color), 
                    "toggle_gap": self.game_manager.default_toggle_gap, 
                    "time_to_flip": self.game_manager.default_time_to_flip
                }
                new_toggle = Toggle(layout_props, self.game_manager.graphics_manager.time, self.game_manager, on=False, callback=None, shown=True)
                if self.input_manager.menu.open:
                    self.game_manager.input_manager.toggles["menu"][self.input_manager.menu.active_tab].append(new_toggle)
                else:
                    self.game_manager.input_manager.toggles[self.game_manager.game_state]["new_toggle"].append(new_toggle)
                self.update_ui()
    
        # Position and size
        elif text.startswith("x"):
            self._set_x_position(text)
        elif text.startswith("y"):
            self._set_y_position(text)
        elif text.startswith("w"):
            self._set_width(text)
        elif text.startswith("h"):
            self._set_height(text)
        
        # System commands
        elif text == "overridel":
            self.game_manager.save_config("layout", True)
        elif text == "overrides":
            self.game_manager.save_config("settings", True)
        elif text == "refreshui":
            self.game_manager.input_manager.reset_ui()
        elif text == "centertext":
            if hasattr(self.mouse_handler.active, 'text_rect') and hasattr(self.mouse_handler.active, 'surface'):
                assert isinstance(self.mouse_handler.active, TextDisplay) or isinstance(self.mouse_handler.active, Button)
                self.mouse_handler.active.text_rect.center = self.mouse_handler.active.surface.get_rect().center

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
        if hasattr(self.mouse_handler.active, 'update_text'):
            assert isinstance(self.mouse_handler.active, TextDisplay) or isinstance(self.mouse_handler.active, Button)
            self.mouse_handler.active.update_text(new_text)

    def _set_text_color(self, text: str) -> None:
        """Set text color of active element."""
        try:
            color_values = text[2:].split(",")
            r = int(color_values[0])
            g = int(color_values[1])
            b = int(color_values[2])
            if hasattr(self.mouse_handler.active, 'text_color'):
                assert isinstance(self.mouse_handler.active, TextDisplay) or isinstance(self.mouse_handler.active, Button)
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
            
            # For buttons and text displays
            if hasattr(self.mouse_handler.active, 'color'):
                assert isinstance(self.mouse_handler.active, TextDisplay) or isinstance(self.mouse_handler.active, Button)
                self.mouse_handler.active.color = (r, g, b)
            
            # For toggles (use color now)
            if isinstance(self.mouse_handler.active, Toggle):
                self.mouse_handler.active.color = (r, g, b)
            
            # For sliders (use color now)
            if isinstance(self.mouse_handler.active, Slider):
                self.mouse_handler.active.color = (r, g, b)
        except (ValueError, IndexError):
            pass

    def _set_handle_color(self, text: str) -> None:
        """Set handle color for toggles."""
        try:
            color_values = text[2:].split(",")
            r = int(color_values[0])
            g = int(color_values[1])
            b = int(color_values[2])
            
            if hasattr(self.mouse_handler.active, 'handle_color'):
                assert isinstance(self.mouse_handler.active, Toggle)
                self.mouse_handler.active.handle_color = (r, g, b)
        except (ValueError, IndexError):
            pass

    def _set_font_size(self, text: str) -> None:
        """Set font size for text elements."""
        try:
            size = int(text[2:])
            if hasattr(self.mouse_handler.active, 'font'):
                new_font = pygame.font.Font(None, size)
                assert isinstance(self.mouse_handler.active, TextDisplay) or isinstance(self.mouse_handler.active, Button)
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
            if hasattr(self.mouse_handler.active, 'alignment'):
                assert isinstance(self.mouse_handler.active, TextDisplay) or isinstance(self.mouse_handler.active, Button)
                self.mouse_handler.active.text_align = alignment
            
            # Reposition text based on alignment
            if hasattr(self.mouse_handler.active, 'text_rect') and hasattr(self.mouse_handler.active, 'surface'):
                assert isinstance(self.mouse_handler.active, TextDisplay) or isinstance(self.mouse_handler.active, Button)
                if alignment == "left":
                    self.mouse_handler.active.text_rect.left = self.mouse_handler.active.surface.get_rect().left
                elif alignment == "center":
                    self.mouse_handler.active.text_rect.center = self.mouse_handler.active.surface.get_rect().center
                elif alignment == "right":
                    self.mouse_handler.active.text_rect.right = self.mouse_handler.active.surface.get_rect().right

    def _set_name(self, text: str) -> None:
        """Set name of active element."""
        new_name = text[1:]
        if hasattr(self.mouse_handler.active, 'name'):
            assert isinstance(self.mouse_handler.active, (Button, TextDisplay, Slider, Toggle, Image))
            self.mouse_handler.active.name = new_name

    def _set_alpha(self, text: str) -> None:
        """Set alpha/opacity of active element."""
        try:
            alpha = int(text[1:])
            alpha = max(0, min(255, alpha))  # Clamp between 0-255
            
            if hasattr(self.mouse_handler.active, 'surface'):
                assert isinstance(self.mouse_handler.active, (Button, TextDisplay, Image))
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

    def _delete_active(self) -> None:
        """Delete the currently active UI element."""
        if not self.mouse_handler.active:
            return
        
        # Determine which collection the active element belongs to
        collections = [
            self.input_manager.buttons,
            self.input_manager.toggles,
            self.input_manager.sliders,
            self.input_manager.images,
            self.input_manager.text_displays
        ]
        
        for collection in collections:
            for state, elements in collection.items():
                if isinstance(elements, dict):
                    # For buttons in menu tabs
                    for tab, tab_elements in elements.items():
                        if self.mouse_handler.active.name in tab_elements:
                            del tab_elements[self.mouse_handler.active.name]
                            self.mouse_handler.active = None
                            return
                else:
                    # For lists of elements
                    for i, element in enumerate(elements):
                        if element == self.mouse_handler.active:
                            del elements[i]
                            self.mouse_handler.active = None
                            return

    def update_ui(self):
        self.input_manager.mouse_handler.set_ui_elements(
            self.input_manager.buttons,
            self.input_manager.toggles,
            self.input_manager.sliders,
            self.input_manager.images,
            self.input_manager.text_displays,
            self.input_manager.menu
        )