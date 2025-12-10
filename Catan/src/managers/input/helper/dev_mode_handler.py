import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_manager import GameManager
    from src.managers.input.helper.mouse_input_handler import MouseInputHandler
    from input_manager import InputManager

from src.ui.image import Image
from src.ui.toggle import Toggle
from src.ui.slider import Slider
from src.ui.button import Button
from src.ui.text_display import TextDisplay


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
        - x+number -> set x position to number. Example: x150 sets x to 150
        - y+number -> set y position to number. Example: y300 sets y to 300
        - w+number -> set width to number. Example: w200 sets width to 200
        - h+number -> set height to number. Example: h100 sets height to 100
        - c+number,number,number -> set color to rgb values. Example: c255,0,0 sets color to red
        - t+text -> set text to text. Example: tHello sets text to Hello
        - tc+number,number,number -> set text color to rgb values. Example: tc0,255,0 sets text color to green
        """
        if not self.mouse_handler.active:
            return
            
        text = self.game_manager.dev_mode_text
        print(f"Dev Mode Command: {text}")
        
        if text.startswith("x"):
            self._set_x_position(text)
        elif text.startswith("y"):
            self._set_y_position(text)
        elif text.startswith("w"):
            self._set_width(text)
        elif text.startswith("h"):
            self._set_height(text)
        elif text.startswith("t"):
            self._set_text(text)
        elif text.startswith("tc"):
            self._set_text_color(text)
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
                    self.game_manager.input_manager.buttons["menu"][self.input_manager.menu.active_tab].append(new_button)
                else:
                    self.game_manager.input_manager.buttons[self.game_manager.game_state]["new_button"].append(new_button)

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
            
            elif element_type == "display_text":
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
            
        elif text == "overridel":
            self.game_manager.save_config("layout", True)
        elif text == "overrides":
            self.game_manager.save_config("settings", True)
        elif text == "refreshui":
            self.game_manager.input_manager.reset_ui()

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
        except (ValueError, IndexError):
            pass

    def update_ui(self):
        self.input_manager.mouse_handler.set_ui_elements(
            self.input_manager.buttons,
            self.input_manager.toggles,
            self.input_manager.sliders,
            self.input_manager.images,
            self.input_manager.text_displays,
            self.input_manager.menu
        )