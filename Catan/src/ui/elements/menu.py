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
    def __init__(self, layout_props: dict, game_manager: 'GameManager', buttons: Dict[str, Dict[str, Button]], toggles: Dict[str, Dict[str, Toggle]], sliders: Dict[str, Dict[str, Slider]], images: Dict[str, Dict[str, Image]], text_displays: Dict[str, Dict[str, TextDisplay]], time: int = 0) -> None:
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
    
    def _add_children_to_hierarchy(self):
        """Add all buttons, toggles, sliders, images, and text displays to the hierarchy."""
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
    
    def open_menu(self):
        self.location = self.final_location
        self.shown = True  # Make menu visible
        self._invalidate_absolute_rect()  # Recalculate positions

    def close_menu(self):
        self.location = self.init_location
        self.shown = False  # Hide menu
        self._invalidate_absolute_rect()  # Recalculate positions

    def update_menu(self, time: int):
        """Update menu state and control which children are visible based on active tab."""
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

    def draw(self, surface: pygame.Surface, time: int | None= None):
        if not self.shown:
            return
        
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
                    child.draw(surface)
        
        # Draw guiding lines in dev mode
        if self.game_manager.dev_mode and self.is_active:
            pygame.draw.rect(surface, self.guiding_line_color, abs_rect, 2)
    
    def get_absolute_rect(self) -> pygame.Rect:
        """Override to use location instead of rect position."""
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

    def get_layout(self) -> dict:
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

    def dev_mode_drag(self, x: int, y: int) -> None:
        """Override to move both rect and location when dragging in dev mode."""
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