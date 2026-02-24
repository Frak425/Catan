import pygame
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.managers.game.game_manager import GameManager
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
    """
    Handles all developer mode functionality including typing commands and UI manipulation.
    
    Responsibilities:
    - Process text input in dev mode typing mode
    - Parse and execute dev mode commands
    - Dynamically modify UI element properties
    - Create and delete UI elements at runtime
    - Manage UI hierarchy (save/load/restore)
    - Control menu exclusivity and relationships
    
    Command Categories:
    NOTE: Commands are case-sensitive and space-sensitive.
    NOTE: Update as needed when adding new UI elements or properties.
    1. CONFIG MANAGEMENT:
       - overridel: Force save layout config
       - overrides: Force save settings config
       - savehierarchy: Export UI hierarchy to JSON
       - loadhierarchy: Import UI hierarchy from JSON
       - refreshui: Reload all UI elements
       - toggle_debug: Toggle debugging mode
    
    2. ELEMENT CREATION/DELETION:
       - add<type>: Create new element (button, slider, toggle, text_display, image, scrollable_area)
       - del: Delete currently active element
    
    3. MENU MANAGEMENT:
       - listmenus: Show all menus with properties
       - deletemenu <name>: Remove menu by name
       - addexclusion <menu1> <menu2>: Make menus mutually exclusive
       - removeexclusion <menu1> <menu2>: Remove exclusivity
    
    4. ELEMENT PROPERTIES (requires active element):
       Position/Size:
       - x<value>: Set X position (e.g., x100)
       - y<value>: Set Y position (e.g., y50)
       - w<value>: Set width (e.g., w200)
       - h<value>: Set height (e.g., h150)
       
       Colors:
       - c<r,g,b>: Set color (e.g., c255,0,0)
       - tc<r,g,b>: Set text color (e.g., tc0,0,0)
       - hc<r,g,b>: Set handle color (e.g., hc200,200,200)
       
       Text:
       - t<text>: Set text content (e.g., tHello World)
       
       Slider:
       - smin<value>: Set min value (e.g., smin0)
       - smax<value>: Set max value (e.g., smax100)
       - sv<value>: Set current value (e.g., sv50)
       
       Toggle:
       - ton: Set toggle to ON
       - toff: Set toggle to OFF
       - tflip: Flip toggle state
       
       Debug:
       - print_info: Print element details to console
    
    Architecture:
    - Commands entered via typing mode (T key in dev mode)
    - Text buffer stored in game_manager.dev_mode_text
    - RETURN key submits command to parse_typing()
    - Commands modify active element (selected via mouse click)
    - Changes reflected immediately in UI
    """
    game_manager: 'GameManager'
    mouse_handler: 'MouseInputHandler'
    ## --- INITIALIZATION --- ##
    
    def __init__(self):
        """
        Initialize DevModeHandler.
        
        Note: Manager references set separately via set_managers() to avoid circular imports.
        """
        pass  # All dependencies injected via setters

    ## --- DEPENDENCY INJECTION --- ##

    def set_managers(self, game_manager: 'GameManager', mouse_handler: 'MouseInputHandler', input_manager: 'InputManager'):
        """
        Set manager dependencies required for dev mode operations.
        
        Args:
            game_manager: Central game state (dev_mode flags, text buffer, config I/O)
            mouse_handler: Mouse input state (active element for command execution)
            input_manager: Input coordination (UI element collections, menu management)
        
        Note: Must be called before parse_typing() to avoid AttributeError.
        """
        self.game_manager = game_manager
        self.mouse_handler = mouse_handler
        self.input_manager = input_manager

    ## --- TEXT INPUT HANDLERS --- ##

    def add_letter_key(self, key: int) -> None:
        """
        Add a letter key to the dev mode text input buffer.
        
        Args:
            key: pygame key constant (pygame.K_a through pygame.K_z)
        
        Process:
        - Check if in typing mode (early return if not)
        - Map key constant to lowercase letter
        - Append letter to game_manager.dev_mode_text
        
        Note: Only processes lowercase letters. Called from KeyboardInputHandler
              during typing mode for every key press.
        """
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
        """
        Add a number key to the dev mode text input buffer.
        
        Args:
            key: pygame key constant (pygame.K_0 through pygame.K_9)
        
        Process:
        - Check if in typing mode (early return if not)
        - Map key constant to numeric character
        - Append digit to game_manager.dev_mode_text
        
        Note: Used for numeric command arguments like x100, y50, smax200.
        """
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
        r"""
        Add a special character key to the dev mode text input buffer.
        
        Args:
            key: pygame key constant for special characters
        
        Supported Characters:
        - Punctuation: , . - + = / \ : ;
        - Underscore: _
        - Space: (spacebar)
        
        Process:
        - Check if in typing mode (early return if not)
        - Map key constant to character
        - Append character to game_manager.dev_mode_text
        
        Note: Used for text commands, RGB colors (commas), and menu names (spaces/underscores).
        """
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

    ## --- UI REFRESH --- ##
    
    def update_ui(self):
        """
        Refresh mouse handler's UI element references after modification.
        
        Process:
        - Re-call mouse_handler.set_ui_elements() with current collections
        - Ensures mouse handler has latest element references
        - Required after add/delete operations
        
        Note: Called automatically after _handle_add_element() and _delete_active().
              Ensures hit detection works with modified UI element collections.
        """
        self.input_manager.mouse_handler.set_ui_elements(
            self.input_manager.buttons,
            self.input_manager.toggles,
            self.input_manager.sliders,
            self.input_manager.images,
            self.input_manager.text_displays,
            self.input_manager.scrollable_areas,
            self.input_manager.menus
        )
   
    ## --- COMMAND PARSING --- ##
   
    def parse_typing(self) -> None:
        """
        Parse and execute dev mode commands from text buffer.
        
        Command Categories:
        1. No-active-element commands (processed first):
           - add<type>: Create new UI element
           - overridel/overrides: Force config save
           - savehierarchy/loadhierarchy: Export/import UI structure
           - listmenus: Show all menus
           - deletemenu: Remove menu
           - addexclusion/removeexclusion: Manage menu relationships
           - refreshui: Reload UI elements
           - toggle_debug: Toggle debug mode
        
        2. Active-element commands (require selection):
           - Position/size: x, y, w, h
           - Colors: c, tc, hc
           - Text: t
           - Slider: smin, smax, sv
           - Toggle: ton, toff, tflip
           - Debug: del, print_info
        
        Process:
        1. Get command text from game_manager.dev_mode_text
        2. Print command for debugging
        3. Check no-active-element commands first
        4. If no match and no active element, print error and return
        5. Execute active-element command via _execute_command()
        
        Note: Commands are case-sensitive and space-sensitive.
        """
        text = self.game_manager.dev_mode_text
        print(f"Dev Mode Command: {text}")
        
        # Commands that don't require an active element
        if text.startswith("add "):
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

    ## --- COMMAND EXECUTION --- ##

    def _execute_command(self, text: str) -> None:
        """
        Execute command using pattern matching and dynamic attribute setting.
        
        Args:
            text: Command string from typing buffer (already validated non-empty)
        
        Command Patterns:
        
        Simple Attributes (prefix + numeric value):
        - x<num>: Set rect.x (e.g., x100, x-50)
        - y<num>: Set rect.y (e.g., y200)
        - w<num>: Set rect.width (e.g., w150)
        - h<num>: Set rect.height (e.g., h75)
        
        Color Attributes (prefix + r,g,b):
        - c<r,g,b>: Set element color
        - tc<r,g,b>: Set text color (regenerates text surface)
        - hc<r,g,b>: Set handle color (for sliders/toggles)
        
        Slider Commands:
        - smin<num>: Set min_value
        - smax<num>: Set max_value
        - sv<num>: Set current value
        
        Toggle Commands:
        - ton: Set toggle.on = True
        - toff: Set toggle.on = False
        - tflip: Flip toggle state
        
        Text Command:
        - t<text>: Set element text (e.g., tHello World)
        
        Special Commands:
        - del: Delete active element
        - print_info: Print element details
        
        Note: For ScrollableArea elements, automatically calls
              calculate_dependent_properties() after property changes.
        """
        assert self.mouse_handler.active is not None, "No active element selected."

        # Generic dynamic setter: "set <attr_path> <value>"
        # Examples:
        #   set rect.x 100
        #   set color 255,0,0
        #   set text Hello world
        # This infers the target type from the current attribute value.
        if text.startswith("set "):
            parts = text.split(" ", 2)
            if len(parts) < 3:
                print("Usage: set <attr_path> <value>")
                return
            _, attr_path, raw_value = parts

            # Infer type based on current value (if any)
            value = self._infer_and_parse_value(attr_path, raw_value)
            if "." in attr_path:
                self._set_nested_attr(attr_path, value)
            else:
                self._set_attr(attr_path, value)
            return
        
        if text == "tflip":
            if isinstance(self.mouse_handler.active, Toggle):
                self.mouse_handler.active.on = not self.mouse_handler.active.on
        
        
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

    ## --- ATTRIBUTE SETTERS --- ##

    def _invalidate_active_rect_cache(self) -> None:
        """Invalidate active element absolute rect cache after dev-mode edits."""
        active = getattr(self.mouse_handler, "active", None)
        if active is not None and hasattr(active, "_invalidate_absolute_rect"):
            active._invalidate_absolute_rect()

    def _set_attr(self, attr_name: str, value) -> None:
        """
        Dynamically set an attribute on the active element if it exists.
        
        Args:
            attr_name: Name of attribute to set (e.g., 'text', 'on', 'value')
            value: Value to set (type depends on attribute)
        
        Process:
        1. Check if active element has attribute
        2. If exists, set attribute value
        3. Print confirmation or error message
        4. If element is ScrollableArea, recalculate dependent properties
        
        Common Attributes:
        - text: String displayed in Button/TextDisplay
        - on: Boolean state for Toggle
        - value: Numeric value for Slider
        - min_value/max_value: Slider range bounds
        """
        changed = False
        if hasattr(self.mouse_handler.active, attr_name):
            setattr(self.mouse_handler.active, attr_name, value)
            changed = True
            print(f"Set {attr_name} to {value}")
        else:
            print(f"Active element does not have attribute: {attr_name}")

        if changed:
            self._invalidate_active_rect_cache()

        if isinstance(self.mouse_handler.active, ScrollableArea):
            self.mouse_handler.active.calculate_dependent_properties()

    def _set_nested_attr(self, attr_path: str, value) -> None:
        """
        Set nested attributes using dot notation (e.g., 'rect.x').
        
        Args:
            attr_path: Dot-separated path to attribute (e.g., 'rect.x', 'rect.width')
            value: Value to set at the target attribute
        
        Process:
        1. Split path by dots (e.g., 'rect.x' -> ['rect', 'x'])
        2. Navigate through parent attributes (e.g., active.rect)
        3. Set final attribute on parent object (e.g., rect.x = value)
        4. If element is ScrollableArea, recalculate dependent properties
        
        Common Paths:
        - rect.x, rect.y: Position
        - rect.width, rect.height: Size
        
        Note: Validates attribute existence at each level of the path.
        """
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
        changed = False
        if hasattr(obj, final_attr):
            setattr(obj, final_attr, value)
            changed = True
            print(f"Set {attr_path} to {value}")
        else:
            print(f"Attribute not found: {attr_path}")

        if changed:
            self._invalidate_active_rect_cache()

        if isinstance(self.mouse_handler.active, ScrollableArea):
            self.mouse_handler.active.calculate_dependent_properties()

    def _get_nested_attr(self, attr_path: str) -> Any:
        """Safely get a nested attribute (e.g. 'rect.x') from the active element.

        Returns None if any part of the path is missing.
        """
        obj: Any = self.mouse_handler.active
        for part in attr_path.split('.'):
            if not hasattr(obj, part):
                return None
            obj = getattr(obj, part)
        return obj

    def _infer_and_parse_value(self, attr_path: str, raw: str) -> Any:
        """Infer target type from current attribute and parse raw string accordingly.

        - If current value is bool: accept true/false/on/off/1/0
        - If int/float: parse numeric
        - If tuple/list of numbers (e.g. colors): parse "r,g,b" -> tuple[int, int, int]
        - Fallback: keep raw string
        """
        # Try nested first, then direct attribute
        current = self._get_nested_attr(attr_path)
        if current is None and hasattr(self.mouse_handler.active, attr_path):
            current = getattr(self.mouse_handler.active, attr_path)

        # No existing value: try simple numeric parse, then fallback to string
        if current is None:
            if raw.lstrip('-').isdigit():
                return int(raw)
            try:
                return float(raw)
            except ValueError:
                return raw

        # Bool
        if isinstance(current, bool):
            lowered = raw.lower()
            if lowered in ("true", "on", "1"):
                return True
            if lowered in ("false", "off", "0"):
                return False
            return bool(raw)

        # Int / float
        if isinstance(current, int):
            try:
                return int(raw)
            except ValueError:
                try:
                    return int(float(raw))
                except ValueError:
                    return current

        if isinstance(current, float):
            try:
                return float(raw)
            except ValueError:
                return current

        # Tuple/list of numbers (e.g. colors, positions)
        if isinstance(current, (tuple, list)) and raw.count(',') >= 1:
            try:
                parts = [p.strip() for p in raw.split(',')]
                # Match length if possible, otherwise use all parts
                if len(current) and len(parts) != len(current):
                    # Still try; extra/missing values may be intentional during dev
                    pass
                nums = [int(p) if p.lstrip('-').isdigit() else float(p) for p in parts]
                return type(current)(nums)  # preserve tuple vs list
            except ValueError:
                return current

        # Fallback: string
        return raw

    def _set_color_attr(self, attr_name: str, color_str: str) -> None:
        """
        Set a color attribute from comma-separated RGB string.
        
        Args:
            attr_name: Name of color attribute ('color', 'text_color', 'handle_color')
            color_str: RGB values as 'r,g,b' (e.g., '255,0,0' for red)
        
        Process:
        1. Parse RGB string to tuple (r, g, b)
        2. Set attribute using _set_attr()
        3. Special handling for text_color: Regenerate text surface
        4. If parse fails, print error message
        
        Special Cases:
        - text_color on TextDisplay: Regenerates text_surface with new color
        - text_color on Button: Regenerates button text rendering
        
        Format:
        - Valid: '255,0,0' (red), '0,255,0' (green), '128,128,128' (gray)
        - Invalid: '255 0 0' (spaces), 'red' (named colors), '255,0' (incomplete)
        """
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

    ## --- ELEMENT LIFECYCLE --- ##

    def _delete_active(self) -> None:
        """
        Delete the currently active UI element.
        
        Process:
        1. Validate active element exists
        2. Prevent deletion of Menu elements (protection)
        3. Remove from parent hierarchy (if has parent)
        4. Remove from all InputManager collection dictionaries
        5. Clear active element reference
        6. Update UI to reflect changes
        
        Collection Cleanup:
        - Iterates through: buttons, toggles, sliders, images, text_displays
        - Checks both game states (home/setup/game) and menu tabs
        - Removes element by name from matching collections
        
        Note: Menu elements cannot be deleted via 'del' command.
              Use 'deletemenu <name>' command instead.
        """
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
            self.input_manager.scrollable_areas,
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

    def _get_elements_by_type(self) -> dict:
        """Return input manager element collections keyed by dev-mode type name."""
        return {
            "button": self.input_manager.buttons,
            "slider": self.input_manager.sliders,
            "image": self.input_manager.images,
            "text_display": self.input_manager.text_displays,
            "toggle": self.input_manager.toggles,
            "scrollable_area": self.input_manager.scrollable_areas
        }

    def _create_new_button(self, timestamp: int) -> Button:
        layout_props = {
            "name": f"new_button_{timestamp}",
            "rect": [100, 100, 150, 50],
            "color": [0, 100, 0],
            "text": "new button",
        }
        return Button(layout_props, self.game_manager.font, self.game_manager, callback=None, shown=True)

    def _create_new_slider(self, timestamp: int) -> Slider:
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
        return Slider(layout_props, 50, self.game_manager)

    def _create_new_text_display(self, timestamp: int) -> TextDisplay:
        layout_props = {
            "name": f"new_text_display_{timestamp}",
            "rect": [100, 100, 200, 50],
            "color": [200, 200, 200],
            "text": "new text display",
        }
        return TextDisplay(layout_props, self.game_manager, self.game_manager.font, shown=True)

    def _create_new_image(self, timestamp: int) -> Image:
        layout_props = {
            "name": f"new_image_{timestamp}",
            "rect": [100, 100, 100, 100],
            "image_path": None,
        }
        return Image(layout_props, self.game_manager)

    def _create_new_toggle(self, timestamp: int) -> Toggle:
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
        return Toggle(layout_props, self.game_manager.graphics_manager.time, self.game_manager, on=False, callback=None, shown=True)

    def _create_new_scrollable_area(self, timestamp: int) -> ScrollableArea:
        layout_props = {
            "name": f"new_scrollable_area_{timestamp}",
            "rect": [100, 100, 400, 300],
            "exterior_padding": 10,
            "slider_side": "right"
        }
        content_surface = pygame.Surface((400, 600))
        return ScrollableArea(layout_props, self.game_manager, content_surface)

    def _create_new_element(self, element_type: str, timestamp: int):
        """Create a new UI element instance for the requested type."""
        creators = {
            "button": self._create_new_button,
            "slider": self._create_new_slider,
            "text_display": self._create_new_text_display,
            "image": self._create_new_image,
            "toggle": self._create_new_toggle,
            "scrollable_area": self._create_new_scrollable_area,
        }

        creator = creators.get(element_type)
        if not creator:
            return None
        return creator(timestamp)

    def _find_target_menu_for_new_element(self, element_type: str, elements_by_type: dict):
        """Return first open target menu and ensure active tab collection exists."""
        for menu in self.input_manager.get_open_menus():
            tab = menu.active_tab
            if "menus" not in elements_by_type[element_type]:
                elements_by_type[element_type]["menus"] = {}
            if menu.name not in elements_by_type[element_type]["menus"]:
                elements_by_type[element_type]["menus"][menu.name] = {}
            if tab not in elements_by_type[element_type]["menus"][menu.name]:
                elements_by_type[element_type]["menus"][menu.name][tab] = {}
            return menu
        return None

    def _add_new_element_to_menu(self, element_type: str, new_element, target_menu, elements_by_type: dict) -> None:
        """Attach a newly created element to menu collections and hierarchy."""
        tab = target_menu.active_tab
        elements_by_type[element_type]["menus"][target_menu.name][tab][new_element.name] = new_element
        target_menu.add_child(new_element)
        print(f"Added {new_element.name} to menu '{target_menu.name}' tab: {tab} and hierarchy")

    def _add_new_element_to_state(self, element_type: str, new_element, elements_by_type: dict) -> None:
        """Attach a newly created element to current state collections and optional parent."""
        state = self.game_manager.game_state
        if state not in elements_by_type[element_type]:
            elements_by_type[element_type][state] = {}
        elements_by_type[element_type][state][new_element.name] = new_element
        print(f"Added {new_element.name} to state: {state}")

        if self.mouse_handler.active and isinstance(self.mouse_handler.active, (Menu, ScrollableArea)):
            if isinstance(self.mouse_handler.active, ScrollableArea):
                self.mouse_handler.active.add_element(new_element)
                print(f"Added {new_element.name} to scrollable area: {self.mouse_handler.active.name}")
            else:
                self.mouse_handler.active.add_child(new_element)
                print(f"Added {new_element.name} as child of: {self.mouse_handler.active.name}")
        
    def _handle_add_element(self, text: str) -> None:
        """
        Handle adding new UI elements dynamically and integrate with hierarchy.
        
        Args:
            text: Command string starting with 'add' (e.g., 'addbutton', 'addslider')
        
        Supported Element Types:
        - button: Interactive button with text
        - slider: Horizontal/vertical value slider
        - text_display: Read-only text display
        - image: Image display element
        - toggle: On/off switch with animation
        - scrollable_area: Scrollable container with gradient content
        
        Process:
        1. Extract element type from command (e.g., 'addbutton' -> 'button')
        2. Generate unique name with timestamp
        3. Create element with default properties
        4. Add to appropriate collection (menu tab or game state)
        5. Add to UI hierarchy (as menu child or under active parent)
        6. Update UI references
        
        Default Properties:
        - Position: (100, 100)
        - Size: Varies by element type
        - Colors: Default from game_manager or hardcoded
        - Name: <type>_<timestamp> (e.g., 'new_button_12345')
        
        Placement Logic:
        - If menu is open: Add to active tab of first open menu
        - Else: Add to current game state
        - If active element is Menu/ScrollableArea: Add as child
        """
        import time
        element_type = text[4:]
        timestamp = int(time.time() * 1000) % 100000

        elements_by_type = self._get_elements_by_type()
        new_element = self._create_new_element(element_type, timestamp)
        if not new_element:
            print(f"Unknown element type: {element_type}")
            return

        target_menu = self._find_target_menu_for_new_element(element_type, elements_by_type)
        if target_menu:
            self._add_new_element_to_menu(element_type, new_element, target_menu, elements_by_type)
        else:
            self._add_new_element_to_state(element_type, new_element, elements_by_type)

        self.update_ui()
        print(f"Added {new_element.__class__.__name__}: {new_element.name}")
    
    ## --- HIERARCHY PERSISTENCE --- ##
    
    def _save_hierarchy(self) -> None:
        """
        Save the current UI hierarchy to a JSON file for persistence.
        
        Process:
        1. Collect all root elements (elements without parents):
           - All menus are root elements
           - Any state elements without parents
        2. Call save_ui_hierarchy() to serialize hierarchy
        3. Write to src/config/ui_hierarchy.json
        4. Print summary (root count, total element count)
        
        JSON Structure:
        - Hierarchical tree structure
        - Each element includes: type, name, properties, children
        - Preserves parent-child relationships
        - Can be restored with _load_hierarchy()
        
        Use Case:
        - Backup UI layout during development
        - Share UI configurations between devs
        - Recover from accidental deletions
        """
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
        """
        Load UI hierarchy from a JSON file and restore element tree.
        
        Process:
        1. Read src/config/ui_hierarchy.json
        2. Call restore_ui_hierarchy() to deserialize and recreate elements
        3. Get element registry of all restored elements
        4. Call input_manager.reset_ui() to rebuild collections
        5. Print summary and instructions
        
        Error Handling:
        - FileNotFoundError: Prints message if no saved hierarchy exists
        - General exceptions: Prints error message with details
        
        Note: After loading, use 'refreshui' command to fully update UI references.
              The hierarchy is restored but InputManager collections may need rebuild.
        
        Use Case:
        - Restore UI after accidental deletion
        - Load shared UI configuration
        - Reset to known good state during development
        """
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
    
    ## --- MENU MANAGEMENT --- ##
    
    def _list_menus(self) -> None:
        """
        List all available menus with their properties for debugging.
        
        Output Format:
        - Total menu count
        - For each menu:
          - Name: Menu identifier
          - z_index: Draw order (lower = on top)
          - Status: OPEN or closed
          - exclusive_with: List of mutually exclusive menu names
        
        Example Output:
        ```
        === Available Menus (2) ===
          settings: z_index=100, OPEN, exclusive_with=['pause']
          pause: z_index=150, closed, exclusive_with=['settings']
        ```
        """
        if not hasattr(self.input_manager, 'menus'):
            print("No menus found")
            return
        
        print(f"\n=== Available Menus ({len(self.input_manager.menus)}) ===")
        for name, menu in self.input_manager.menus.items():
            status = "OPEN" if menu.shown else "closed"
            print(f"  {name}: z_index={menu.z_index}, {status}, exclusive_with={menu.exclusive_with}")
    
    def _delete_menu(self, command: str) -> None:
        """
        Delete a menu by name. Usage: deletemenu <menu_name>
        
        Args:
            command: Full command string (e.g., 'deletemenu settings')
        
        Process:
        1. Parse menu name from command
        2. Validate menu exists
        3. Close menu if currently open
        4. Remove from input_manager.menus dictionary
        5. Print confirmation
        
        Validation:
        - Requires at least 2 parts (command + name)
        - Menu must exist in menus dictionary
        
        Note: Unlike '_delete_active', this can delete Menu elements directly.
              Does not remove from hierarchy - only from menus collection.
        """
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
        """
        Add mutual exclusivity between two menus. Usage: addexclusion <menu1> <menu2>
        
        Args:
            command: Full command string (e.g., 'addexclusion settings pause')
        
        Process:
        1. Parse two menu names from command
        2. Validate both menus exist
        3. Add menu2 to menu1.exclusive_with list
        4. Add menu1 to menu2.exclusive_with list (bidirectional)
        5. Print confirmation
        
        Effect:
        - When menu1 opens, menu2 will auto-close
        - When menu2 opens, menu1 will auto-close
        - Prevents both menus from being open simultaneously
        
        Use Case:
        - Prevent overlapping menus (e.g., settings vs pause)
        - Enforce single-menu contexts (e.g., only one modal at a time)
        """
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
        """
        Remove mutual exclusivity between two menus. Usage: removeexclusion <menu1> <menu2>
        
        Args:
            command: Full command string (e.g., 'removeexclusion settings pause')
        
        Process:
        1. Parse two menu names from command
        2. Validate both menus exist
        3. Remove menu2 from menu1.exclusive_with list
        4. Remove menu1 from menu2.exclusive_with list (bidirectional)
        5. Print confirmation
        
        Effect:
        - Both menus can now be open simultaneously
        - Removes auto-close behavior when other menu opens
        
        Use Case:
        - Allow overlapping menus during development
        - Test multi-menu interactions
        - Fix over-constrained menu relationships
        """
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