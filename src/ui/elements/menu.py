import pygame
from typing import Dict, TYPE_CHECKING
from src.managers import *
from src.ui.ui_element import UIElement
from src.ui.elements.button import Button
from src.ui.elements.toggle import Toggle
from src.ui.elements.slider import Slider
from src.ui.elements.image import Image
from src.ui.elements.text_display import TextDisplay

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

#import pytweening as tween

class Menu(UIElement):
    """
    Container for tabbed UI elements with multi-menu system support.
    
    Features:
    - Tab-based organization (input, accessibility, gameplay, audio, graphics)
    - Element collections per tab: buttons, toggles, sliders, images, text_displays
    - Tab switching: only active tab's elements are shown
    - Multi-menu system: z_index priority, modal blocking, exclusivity
    - Open/close with init_location and final_location
    - Animation system (partially implemented)
    
    Architecture:
    - Uses location (init/final) instead of rect.x/rect.y for positioning
    - All child elements organized by tab in dictionaries
    - Tab buttons always visible, other elements shown/hidden per active_tab
    - Children added to hierarchy for parent-child coordinate transforms
    
    Multi-Menu System:
    - z_index: Lower = higher priority (0 = top)
    - modal: If True, blocks input to other menus
    - exclusive_with: List of menu names that can't be open simultaneously
    - close_on_state_change: Auto-close when game state changes
    
    Positioning:
    - Menu uses location tuple (x, y) instead of rect.x/rect.y
    - init_location: Closed position (often off-screen)
    - final_location: Open position (on-screen)
    - get_absolute_rect() overridden to use location
    
    Tab Organization:
    - Element dicts: {tab_name: {element_name: element}}
    - Special "tabs" key for tab buttons (always visible)
    - Active tab controls which elements are shown
    """
    def __init__(self, layout_props: dict, game_manager: 'GameManager', buttons: Dict[str, Dict[str, Button]], toggles: Dict[str, Dict[str, Toggle]], sliders: Dict[str, Dict[str, Slider]], images: Dict[str, Dict[str, Image]], text_displays: Dict[str, Dict[str, TextDisplay]], time: int = 0) -> None:
        """
        Initialize menu with element collections and tab system.
        
        Args:
            layout_props: Configuration from layout.json
            game_manager: Central game state manager
            buttons: {tab_name: {button_name: Button}} - organized by tab
            toggles: {tab_name: {toggle_name: Toggle}}
            sliders: {tab_name: {slider_name: Slider}}
            images: {tab_name: {image_name: Image}}
            text_displays: {tab_name: {text_display_name: TextDisplay}}
            time: Initial time for animation (milliseconds)
        
        Properties:
        - tabs: List of tab names (order matters for display)
        - active_tab: Currently visible tab
        - location: Current position (init_location when closed, final_location when open)
        - init_location: Position when menu is closed
        - final_location: Position when menu is open
        - z_index: Menu priority (lower = on top, 0 = highest)
        - exclusive_with: Menu names that can't be open simultaneously
        - modal: If True, blocks input to lower priority menus
        - close_on_state_change: Auto-close on game state change
        - anim_length: Animation duration in seconds (not fully implemented)
        
        Element Organization:
        - Special "tabs" key in buttons dict for tab switcher buttons
        - Each tab has its own element collections
        - Only active tab's elements are visible
        """
        # Set defaults before reading layout
        self.name = "menu"
        self.rect = pygame.Rect(0, 0, 800, 600)
        self.backdrop = None
        self.bckg_color = (200, 200, 200)
        self.game_font = game_manager.game_font
        
        self.init_location = (0, 0)
        self.final_location = (0, 0)
        
        # IN PROGRESS: adding tabs to the settings menu to further organize the settings
        self.tabs = ["input", "accessibility", "gameplay", "audio", "graphics"]
        self.active_tab = "input"
        self.buttons = buttons
        self.toggles = toggles
        self.sliders = sliders
        self.images = images
        self.text_displays = text_displays
        
        # Multi-menu system properties
        self.z_index = 0  # Lower number = on top (0 is highest priority)
        self.exclusive_with = []  # List of menu names that can't be open simultaneously
        self.modal = False  # If True, blocks input to other menus
        self.close_on_state_change = True  # If True, closes when game state changes
        
        self.anim_length = 0.5  # in seconds
        self.start_time = None
        self.elapsed_time = 0
        self.anim_reversed = False
        
        # Initialize parent class (this calls read_layout internally)
        # Start with shown=False since menu should be closed by default
        super().__init__(layout_props, game_manager, callback=None, shown=False)
        
        # Read layout properties to update locations from config
        self.read_layout(layout_props)
        
        # Set initial location AFTER reading layout so init_location has the correct value
        self.location = self.init_location
        
        # Create menu surface
        self.menu_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        
        if self.backdrop:
            self.menu_surface.blit(pygame.transform.scale(self.backdrop, self.rect.size), (0, 0))
        else:
            self.menu_surface.fill(self.bckg_color)
        
        # Add all UI elements to the hierarchy
        self._add_children_to_hierarchy()
        
        self.update_menu(time)
    
    ## --- HIERARCHY SETUP --- ##
    
    def _add_children_to_hierarchy(self):
        """
        Add all UI elements to parent-child hierarchy for coordinate transforms.
        
        Adds tab buttons (always visible) and all elements from each tab.
        Children use parent's get_absolute_rect() for positioning.
        """
        # Add tab buttons
        if "tabs" in self.buttons:
            for button in self.buttons["tabs"].values():
                self.add_child(button)
        
        # Add elements for each tab
        for tab in self.tabs:
            if tab in self.buttons:
                for button in self.buttons[tab].values():
                    self.add_child(button)
            if tab in self.toggles:
                for toggle in self.toggles[tab].values():
                    self.add_child(toggle)
            if tab in self.sliders:
                for slider in self.sliders[tab].values():
                    self.add_child(slider)
            if tab in self.images:
                for image in self.images[tab].values():
                    self.add_child(image)
            if tab in self.text_displays:
                for text_display in self.text_displays[tab].values():
                    self.add_child(text_display)
    
    ## --- MENU CONTROL --- ##
    
    def open_menu(self):
        """Open menu by moving to final_location and showing."""
        self.location = self.final_location
        self.shown = True  # Make menu visible
        self._invalidate_absolute_rect()  # Recalculate positions

    def close_menu(self):
        """Close menu by moving to init_location and hiding."""
        self.location = self.init_location
        self.shown = False  # Hide menu
        self._invalidate_absolute_rect()  # Recalculate positions

    def update_menu(self, time: int):
        """
        Update menu state and control element visibility based on active tab.
        
        Visibility Rules:
        - Tab buttons ("tabs" key): Always shown
        - Other elements: Only shown if their tab == active_tab
        
        This is called each frame during draw to update element visibility.
        """
        # Control visibility of children based on active tab
        # Tab buttons are always visible
        if "tabs" in self.buttons:
            for button in self.buttons["tabs"].values():
                button.shown = True
        
        # Show only elements for the active tab
        for tab in self.tabs:
            is_active = (tab == self.active_tab)
            
            if tab in self.buttons:
                for button in self.buttons[tab].values():
                    button.shown = is_active
            if tab in self.toggles:
                for toggle in self.toggles[tab].values():
                    toggle.shown = is_active
            if tab in self.sliders:
                for slider in self.sliders[tab].values():
                    slider.shown = is_active
            if tab in self.images:
                for image in self.images[tab].values():
                    image.shown = is_active
            if tab in self.text_displays:
                for text_display in self.text_displays[tab].values():
                    text_display.shown = is_active

    ## --- RENDERING --- ##

    def draw(self, surface: pygame.Surface, time: int | None= None):
        """
        Draw menu background and all visible children.
        
        Process:
        1. Update menu state (tab visibility)
        2. Redraw background (backdrop image or solid color)
        3. Draw menu surface at absolute position
        4. Draw all visible children (they handle their own positioning)
        5. Draw guiding lines if in dev mode
        
        Special Handling:
        - Toggle elements receive time parameter for animation
        - Children use their own get_absolute_rect() for positioning
        """
        if not self.shown:
            return
        
        self.update()

        # Update menu state
        if time is not None:
            self.update_menu(time)
        
        # Use absolute rect for drawing (combines rect with location)
        abs_rect = self.get_absolute_rect()
        
        # Redraw background
        if self.backdrop:
            self.menu_surface.fill((0, 0, 0, 0))  # Clear
            self.menu_surface.blit(pygame.transform.scale(self.backdrop, self.rect.size), (0, 0))
        else:
            self.menu_surface.fill(self.bckg_color)
        
        # Draw menu surface at absolute position
        surface.blit(self.menu_surface, abs_rect.topleft)
        
        # Draw children (they handle their own absolute positioning)
        for child in self.children:
            if child.shown:
                # Pass time to toggles if needed
                if isinstance(child, Toggle) and time is not None:
                    child.draw(surface, time)
                else:
                    child.draw(surface) # type: ignore
        
        # Draw guiding lines in dev mode
        if self.game_manager.dev_mode and self.is_active:
            pygame.draw.rect(surface, self.guiding_line_color, abs_rect, 2)
    
    ## --- COORDINATE TRANSFORM --- ##
    
    def get_absolute_rect(self) -> pygame.Rect:
        """
        Override to use location tuple instead of rect.x/rect.y for positioning.
        
        Critical Difference:
        - Normal UIElement: Uses rect.x and rect.y
        - Menu: Uses self.location (init_location or final_location)
        
        This allows menu to have separate open/closed positions without
        modifying rect, which is used for size only.
        """
        if self._absolute_rect is None:
            # Menu uses location for positioning, not rect.x/rect.y
            if self.location:
                x, y = self.location
            else:
                x, y = self.rect.x, self.rect.y
            
            if self.parent:
                parent_rect = self.parent.get_absolute_rect()
                self._absolute_rect = pygame.Rect(
                    parent_rect.x + x,
                    parent_rect.y + y,
                    self.rect.width,
                    self.rect.height
                )
            else:
                self._absolute_rect = pygame.Rect(x, y, self.rect.width, self.rect.height)
        return self._absolute_rect

    ## --- SERIALIZATION --- ##

    def get_layout(self) -> dict:
        """
        Serialize menu and all child elements to config dict.
        
        Includes complete nested serialization of all buttons, toggles, sliders,
        images, and text_displays organized by tab.
        """
        layout = self._get_common_layout()
        layout.update({
            "_type": "Menu",
            "bckg_color": [self.bckg_color[0], self.bckg_color[1], self.bckg_color[2]] if self.bckg_color else None,
            "init_location": [self.init_location[0], self.init_location[1]] if self.init_location else None,
            "final_location": [self.final_location[0], self.final_location[1]] if self.final_location else None,
            "anim_length": self.anim_length,
            "active_tab": self.active_tab,
            "tabs": self.tabs,
            "z_index": self.z_index,
            "exclusive_with": self.exclusive_with,
            "modal": self.modal,
            "close_on_state_change": self.close_on_state_change,
            "buttons": {tab: {name: button.get_layout() for name, button in buttons.items()} for tab, buttons in self.buttons.items()},
            "toggles": {tab: {name: toggle.get_layout() for name, toggle in toggles.items()} for tab, toggles in self.toggles.items()},
            "sliders": {tab: {name: slider.get_layout() for name, slider in sliders.items()} for tab, sliders in self.sliders.items()},
            "images": {tab: {name: image.get_layout() for name, image in images.items()} for tab, images in self.images.items()},
            "text_displays": {tab: {name: text_display.get_layout() for name, text_display in text_displays.items()} for tab, text_displays in self.text_displays.items()}
        })
        return layout
    
    def read_layout(self, layout_props: dict) -> None:
        """
        Load menu properties and propagate to all child elements.
        
        Reads menu-specific properties (locations, colors, z_index, etc.) and
        then recursively reads layout for all child elements in all tabs.
        
        Note: Only updates existing elements - doesn't create new ones.
        """
        # Read common properties first
        self._read_common_layout(layout_props)
        
        bckg_color_data = layout_props.get("bckg_color", [self.bckg_color[0], self.bckg_color[1], self.bckg_color[2]]) if self.bckg_color else None
        if bckg_color_data:
            self.bckg_color = (bckg_color_data[0], bckg_color_data[1], bckg_color_data[2])

        init_location_data = layout_props.get("init_location", [self.init_location[0], self.init_location[1]]) if self.init_location else None
        if init_location_data:
            self.init_location = (init_location_data[0], init_location_data[1])

        final_location_data = layout_props.get("final_location", [self.final_location[0], self.final_location[1]]) if self.final_location else None
        if final_location_data:
            self.final_location = (final_location_data[0], final_location_data[1])

        self.anim_length = layout_props.get("anim_length", self.anim_length)
        
        # Read multi-menu properties
        self.z_index = layout_props.get("z_index", self.z_index)
        self.exclusive_with = layout_props.get("exclusive_with", self.exclusive_with)
        self.modal = layout_props.get("modal", self.modal)
        self.close_on_state_change = layout_props.get("close_on_state_change", self.close_on_state_change)

        # Read buttons
        buttons_layout = layout_props.get("buttons", {})
        for tab, buttons in buttons_layout.items():
            for name, button_layout in buttons.items():
                if tab in self.buttons and name in self.buttons[tab]:
                    self.buttons[tab][name].read_layout(button_layout)

        # Read toggles
        toggles_layout = layout_props.get("toggles", {})
        for tab, toggles in toggles_layout.items():
            for name, toggle_layout in toggles.items():
                if tab in self.toggles and name in self.toggles[tab]:
                    self.toggles[tab][name].read_layout(toggle_layout)

        # Read sliders
        sliders_layout = layout_props.get("sliders", {})
        for tab, sliders in sliders_layout.items():
            for name, slider_layout in sliders.items():
                if tab in self.sliders and name in self.sliders[tab]:
                    self.sliders[tab][name].read_layout(slider_layout)
        
        # Read images
        images_layout = layout_props.get("images", {})
        for tab, images in images_layout.items():
            for name, image_layout in images.items():
                if tab in self.images and name in self.images[tab]:
                    self.images[tab][name].read_layout(image_layout)
        
        # Read text displays
        text_displays_layout = layout_props.get("text_displays", {})
        for tab, text_displays in text_displays_layout.items():
            for name, text_display_layout in text_displays.items():
                if tab in self.text_displays and name in self.text_displays[tab]:
                    self.text_displays[tab][name].read_layout(text_display_layout)

    ## --- DEV MODE --- ##

    def dev_mode_drag(self, x: int, y: int) -> None:
        """
        Override to update both rect and location properties when dragging.
        
        Since Menu uses location for positioning (not rect.x/rect.y), we need to
        update all three location properties to maintain proper positioning:
        - location: Current position
        - init_location: Closed position
        - final_location: Open position
        """
        super().dev_mode_drag(x, y)
        # Update the current location as well
        if self.location:
            self.location = (self.location[0] + x, self.location[1] + y)
        # Update init and final locations to maintain offsets
        if self.init_location:
            self.init_location = (self.init_location[0] + x, self.init_location[1] + y)
        if self.final_location:
            self.final_location = (self.final_location[0] + x, self.final_location[1] + y)

    def print_info(self) -> None:
        """Print menu properties and all child element info for debugging."""
        self.print_common_info()
        print(f"Background Color: {self.bckg_color}")
        print(f"Initial Location: {self.init_location}")
        print(f"Final Location: {self.final_location}")
        print(f"Animation Length: {self.anim_length}")
        print(f"Active Tab: {self.active_tab}")
        print(f"Shown (Open): {self.shown}")
        print(f"Buttons:")
        for tab, buttons in self.buttons.items():
            print(f"  Tab: {tab}")
            for name, button in buttons.items():
                print(f"    Button Name: {name}")
                button.print_info()
        print(f"Toggles:")
        for tab, toggles in self.toggles.items():
            print(f"  Tab: {tab}")
            for name, toggle in toggles.items():
                print(f"    Toggle Name: {name}")
                toggle.print_info()
        print(f"Sliders:")
        for tab, sliders in self.sliders.items():
            print(f"  Tab: {tab}")
            for name, slider in sliders.items():
                print(f"    Slider Name: {name}")
                slider.print_info()