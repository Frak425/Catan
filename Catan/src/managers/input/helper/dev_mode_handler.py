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
from src.ui.layout_utils import save_ui_hierarchy, restore_ui_hierarchy


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
            self.input_manager.menus
        )
   
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
        elif text == "savehierarchy":
            self._save_hierarchy()
            return
        elif text == "loadhierarchy":
            self._load_hierarchy()
            return
        elif text == "listmenus":
            self._list_menus()
            return
        elif text.startswith("deletemenu"):
            self._delete_menu(text)
            return
        elif text.startswith("addexclusion"):
            self._add_exclusion(text)
            return
        elif text.startswith("removeexclusion"):
            self._remove_exclusion(text)
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
        
        # Handle simple attribute commands
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
            self._set_attr('value', int(text[2:]))
        
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
            self._set_attr('text', text[1:])
        
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

    def _delete_active(self) -> None:
        """Delete the currently active UI element."""
        if not self.mouse_handler.active:
            return
        
        # Don't allow deleting the menu itself
        if isinstance(self.mouse_handler.active, Menu):
            print("Cannot delete menu")
            return
        
        element_to_delete = self.mouse_handler.active
        
        # Remove from parent in hierarchy
        if element_to_delete.parent:
            element_to_delete.parent.remove_child(element_to_delete)
            print(f"Removed {element_to_delete.name} from parent hierarchy")
        
        # Remove from legacy collection dictionaries
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
                        if element_to_delete.name in tab_elements:
                            del tab_elements[element_to_delete.name]
                            print(f"Removed from menu tab: {tab}")
                else:
                    # For lists of elements
                    if element_to_delete.name in elements:
                        del elements[element_to_delete.name]
                        print(f"Removed from state: {state}")
        
        self.mouse_handler.active = None
        self.update_ui()
        
    def _handle_add_element(self, text: str) -> None:
        """Handle adding new UI elements and integrate with hierarchy."""
        import time
        element_type = text[3:]
        
        # Generate unique name with timestamp
        timestamp = int(time.time() * 1000) % 100000

        elements_by_type = {
            "button": self.input_manager.buttons,
            "slider": self.input_manager.sliders,
            "image": self.input_manager.images,
            "text_display": self.input_manager.text_displays,
            "toggle": self.input_manager.toggles,
            "scrollable_area": self.input_manager.scrollable_areas
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
        
        elif element_type == "scrollable_area":
            layout_props = {
                "name": f"new_scrollable_area_{timestamp}",
                "rect": [100, 100, 400, 300],
                "exterior_padding": 10,
                "slider_side": "right"
            }
            content_surface = pygame.Surface((400, 600))
            new_element = ScrollableArea(layout_props, self.game_manager, content_surface)
            
        else:
            print(f"Unknown element type: {element_type}")
            return

        # Add to legacy dictionary structure
        # Check if we're adding to a specific menu
        target_menu = None
        for menu in self.input_manager.get_open_menus():
            tab = menu.active_tab
            if tab not in elements_by_type[element_type]["menu"]:
                elements_by_type[element_type]["menu"][tab] = {}
            # Use first open menu for now (could be enhanced to detect which menu was clicked)
            target_menu = menu
            break
        
        if target_menu:
            tab = target_menu.active_tab
            elements_by_type[element_type]["menu"][tab][new_element.name] = new_element
            
            # Add to menu hierarchy
            target_menu.add_child(new_element)
            print(f"Added {new_element.name} to menu '{target_menu.name}' tab: {tab} and hierarchy")
        else:
            state = self.game_manager.game_state
            if state not in elements_by_type[element_type]:
                elements_by_type[element_type][state] = {}
            elements_by_type[element_type][state][new_element.name] = new_element
            print(f"Added {new_element.name} to state: {state}")
            
            # If there's an active parent element, add as child
            if self.mouse_handler.active and isinstance(self.mouse_handler.active, (Menu, ScrollableArea)):
                if isinstance(self.mouse_handler.active, ScrollableArea):
                    self.mouse_handler.active.add_element(new_element)
                    print(f"Added {new_element.name} to scrollable area: {self.mouse_handler.active.name}")
                else:
                    self.mouse_handler.active.add_child(new_element)
                    print(f"Added {new_element.name} as child of: {self.mouse_handler.active.name}")

        self.update_ui()
        print(f"Added {new_element.__class__.__name__}: {new_element.name}")
    
    def _save_hierarchy(self) -> None:
        """Save the current UI hierarchy to a JSON file."""
        import json
        
        # Collect root elements (elements without parents)
        root_elements = []
        
        # All menus are root elements
        if hasattr(self.input_manager, 'menus') and self.input_manager.menus:
            root_elements.extend(self.input_manager.menus.values())
        
        # Collect other potential root elements from each state
        for collection in [self.input_manager.buttons, self.input_manager.toggles, 
                          self.input_manager.sliders, self.input_manager.images, 
                          self.input_manager.text_displays, self.input_manager.scrollable_areas]:
            for state, elements in collection.items():
                if state != "menu":  # Skip menu as we already added it
                    if isinstance(elements, dict):
                        for element in elements.values():
                            if element.parent is None and element not in root_elements:
                                root_elements.append(element)
        
        # Save the hierarchy
        hierarchy_data = save_ui_hierarchy(root_elements)
        
        # Save to file
        with open("src/config/ui_hierarchy.json", "w") as f:
            json.dump(hierarchy_data, f, indent=2)
        
        print(f"Saved UI hierarchy with {len(root_elements)} root elements to ui_hierarchy.json")
        print(f"Total elements saved: {len(hierarchy_data)}")
    
    def _load_hierarchy(self) -> None:
        """Load UI hierarchy from a JSON file."""
        import json
        
        try:
            with open("src/config/ui_hierarchy.json", "r") as f:
                hierarchy_data = json.load(f)
            
            # Restore the hierarchy
            element_registry = restore_ui_hierarchy(hierarchy_data, self.game_manager)
            
            print(f"Loaded {len(element_registry)} elements from hierarchy")
            
            # Update input manager references
            # Note: This is a simplified approach - you may need to rebuild
            # the state-based dictionaries from the loaded elements
            self.game_manager.input_manager.reset_ui()
            
            print("UI hierarchy loaded successfully. Use 'refreshui' to fully update.")
        except FileNotFoundError:
            print("No saved hierarchy found at src/config/ui_hierarchy.json")
        except Exception as e:
            print(f"Error loading hierarchy: {e}")
    
    def _list_menus(self) -> None:
        """List all available menus with their properties."""
        if not hasattr(self.input_manager, 'menus'):
            print("No menus found")
            return
        
        print(f"\n=== Available Menus ({len(self.input_manager.menus)}) ===")
        for name, menu in self.input_manager.menus.items():
            status = "OPEN" if menu.shown else "closed"
            print(f"  {name}: z_index={menu.z_index}, {status}, exclusive_with={menu.exclusive_with}")
    
    def _delete_menu(self, command: str) -> None:
        """Delete a menu. Usage: deletemenu <menu_name>"""
        parts = command.split()
        if len(parts) < 2:
            print("Usage: deletemenu <menu_name>")
            return
        
        menu_name = parts[1]
        if menu_name not in self.input_manager.menus:
            print(f"Menu '{menu_name}' not found")
            return
        
        # Close the menu if it's open
        if self.input_manager.menus[menu_name].shown:
            self.input_manager.close_menu_by_name(menu_name)
        
        # Remove from menus dict
        del self.input_manager.menus[menu_name]
        print(f"Deleted menu: {menu_name}")
    
    def _add_exclusion(self, command: str) -> None:
        """Add exclusivity between two menus. Usage: addexclusion <menu1> <menu2>"""
        parts = command.split()
        if len(parts) < 3:
            print("Usage: addexclusion <menu1> <menu2>")
            return
        
        menu1_name = parts[1]
        menu2_name = parts[2]
        
        menu1 = self.input_manager.get_menu(menu1_name)
        menu2 = self.input_manager.get_menu(menu2_name)
        
        if not menu1:
            print(f"Menu '{menu1_name}' not found")
            return
        if not menu2:
            print(f"Menu '{menu2_name}' not found")
            return
        
        # Add bidirectional exclusivity
        if menu2_name not in menu1.exclusive_with:
            menu1.exclusive_with.append(menu2_name)
        if menu1_name not in menu2.exclusive_with:
            menu2.exclusive_with.append(menu1_name)
        
        print(f"Added exclusivity between '{menu1_name}' and '{menu2_name}'")
    
    def _remove_exclusion(self, command: str) -> None:
        """Remove exclusivity between two menus. Usage: removeexclusion <menu1> <menu2>"""
        parts = command.split()
        if len(parts) < 3:
            print("Usage: removeexclusion <menu1> <menu2>")
            return
        
        menu1_name = parts[1]
        menu2_name = parts[2]
        
        menu1 = self.input_manager.get_menu(menu1_name)
        menu2 = self.input_manager.get_menu(menu2_name)
        
        if not menu1:
            print(f"Menu '{menu1_name}' not found")
            return
        if not menu2:
            print(f"Menu '{menu2_name}' not found")
            return
        
        # Remove bidirectional exclusivity
        if menu2_name in menu1.exclusive_with:
            menu1.exclusive_with.remove(menu2_name)
        if menu1_name in menu2.exclusive_with:
            menu2.exclusive_with.remove(menu1_name)
        
        print(f"Removed exclusivity between '{menu1_name}' and '{menu2_name}'")