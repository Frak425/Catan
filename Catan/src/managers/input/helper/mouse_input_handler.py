import pygame
import math
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from game_manager import GameManager
    from graphics_manager import GraphicsManager
    from helper_manager import HelperManager

from src.ui.elements.text_display import TextDisplay
from src.ui.elements.button import Button
from src.ui.elements.slider import Slider
from src.ui.elements.toggle import Toggle
from src.ui.elements.image import Image
from src.ui.elements.menu import Menu
from src.ui.elements.scrollable_area import ScrollableArea


class MouseInputHandler:
    """Handles all mouse input events including clicks, drags, and motion."""
    active: Button | Slider | Toggle | Button | Image | TextDisplay | Menu | None = None  # the currently active clickable object
    prev_active: Button | Slider | Toggle | Button | Image | TextDisplay | Menu | None = None  # previously active clickable object
    # Manager references (set after initialization)
    game_manager: 'GameManager'
    graphics_manager: 'GraphicsManager'
    helper_manager: 'HelperManager'
    menu: Menu

    def __init__(self):
        self.dragging = False  # true between MBD and MBU with distance > 5 pixels
        self.clicked = False  # true between MBD and MBU
        self.start_x = 0
        self.start_y = 0
        self.click_end_x = 0
        self.click_end_y = 0
        self.prev_dx = 0
        self.prev_dy = 0
        
        self.buttons: Dict = {}
        self.toggles: Dict = {}
        self.sliders: Dict = {}
        self.scrollable_areas: Dict = {}
        
    def set_managers(self, game_manager, graphics_manager, helper_manager):
        """Set manager references."""
        self.game_manager = game_manager
        self.graphics_manager = graphics_manager
        self.helper_manager = helper_manager

    def set_ui_elements(self, buttons, toggles, sliders, images, text_display, scrollable_areas, menus):
        """Set UI element references."""
        self.buttons = buttons
        self.toggles = toggles
        self.sliders = sliders
        self.images = images
        self.text_display = text_display
        self.scrollable_areas = scrollable_areas
        self.menus = menus

    def handle_mouse_input(self, x: int, y: int, event_type: int) -> None:
        """Main entry point for handling mouse events."""
        if event_type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_button_down(x, y)
        elif event_type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(x, y)
        elif event_type == pygame.MOUSEBUTTONUP:
            self._handle_mouse_button_up(x, y)

    def _handle_mouse_button_down(self, x: int, y: int) -> None:
        """Handle mouse button down events."""
        if self.active:
            self.prev_active = self.active
            self.active.is_active = False
        
        self.start_x = x
        self.start_y = y
        self.clicked = True
        state = self.game_manager.game_state

        # Check if any menus are open - prioritize by z-index (lower = on top)
        from src.managers.input.input_manager import InputManager
        input_manager = self.game_manager.input_manager if hasattr(self.game_manager, 'input_manager') else None
        
        button_clicked = None
        toggle_clicked = None
        slider_clicked = None
        text_display_clicked = None
        image_clicked = None
        scrollable_area_clicked = None
        menu_clicked = None
        
        if input_manager:
            open_menus = input_manager.get_open_menus()
            # Sort by z_index (lower = higher priority)
            open_menus_sorted = sorted(open_menus, key=lambda m: m.z_index)
            
            # Check menus from top to bottom (lowest z_index first)
            for menu in open_menus_sorted:
                menu_offset_x = menu.location[0]
                menu_offset_y = menu.location[1]
                
                # Check this menu's elements
                temp_button = self.helper_manager.check_clickable_from_dict(
                    self.buttons["menu"][menu.active_tab], 
                    (x, y), 
                    menu_offset_x, 
                    menu_offset_y
                )
                temp_toggle = self.helper_manager.check_clickable_from_dict(
                    self.toggles["menu"][menu.active_tab], 
                    (x, y), 
                    menu_offset_x, 
                    menu_offset_y
                )
                temp_slider = self.helper_manager.check_clickable_from_dict(
                    self.sliders["menu"][menu.active_tab], 
                    (x, y), 
                    menu_offset_x, 
                    menu_offset_y
                )
                
                # If slider was clicked, check if it was specifically on the handle
                if temp_slider:
                    if temp_slider.direction == "horizontal":
                        handle_rect = pygame.Rect(
                            temp_slider.rect.x + temp_slider.slider_position + menu_offset_x,
                            temp_slider.rect.y + menu_offset_y,
                            temp_slider.handle_surface.get_width(),
                            temp_slider.handle_surface.get_height()
                        )
                    else:  # vertical
                        handle_rect = pygame.Rect(
                            temp_slider.rect.x + menu_offset_x,
                            temp_slider.rect.y + temp_slider.slider_position + menu_offset_y,
                            temp_slider.handle_surface.get_width(),
                            temp_slider.handle_surface.get_height()
                        )
                    if not handle_rect.collidepoint(x, y):
                        temp_slider = None
                
                # TextDisplay is display-only, but selectable in dev mode
                temp_text_display = None
                if self.game_manager.dev_mode:
                    temp_text_display = self.helper_manager.check_clickable_from_dict(
                        self.text_display["menu"][menu.active_tab], 
                        (x, y),
                        menu_offset_x,
                        menu_offset_y
                    )
                
                temp_image = self.helper_manager.check_clickable_from_dict(
                    self.images["menu"][menu.active_tab], 
                    (x, y),
                    menu_offset_x,
                    menu_offset_y
                )
                temp_scrollable_area = self.helper_manager.check_clickable_from_dict(
                    self.scrollable_areas["menu"][menu.active_tab],
                    (x, y),
                    menu_offset_x,
                    menu_offset_y
                )
                
                # If scrollable area was clicked, check if it was specifically on the slider handle
                if temp_scrollable_area:
                    slider = temp_scrollable_area.slider
                    if slider.direction == "horizontal":
                        handle_rect = pygame.Rect(
                            temp_scrollable_area.rect.x + slider.rect.x + slider.slider_position + menu_offset_x,
                            temp_scrollable_area.rect.y + slider.rect.y + menu_offset_y,
                            slider.handle_surface.get_width(),
                            slider.handle_surface.get_height()
                        )
                    else:  # vertical
                        handle_rect = pygame.Rect(
                            temp_scrollable_area.rect.x + slider.rect.x + menu_offset_x,
                            temp_scrollable_area.rect.y + slider.rect.y + slider.slider_position + menu_offset_y,
                            slider.handle_surface.get_width(),
                            slider.handle_surface.get_height()
                        )
                    if not handle_rect.collidepoint(x, y):
                        temp_scrollable_area = None
                
                # Check tab buttons
                if not temp_button:
                    temp_button = self.helper_manager.check_clickable_from_dict(
                        self.buttons["menu"]["tabs"], 
                        (x, y), 
                        menu_offset_x, 
                        menu_offset_y
                    )
                
                # In dev mode, check if the menu background itself was clicked
                temp_menu = None
                if self.game_manager.dev_mode:
                    menu_rect = pygame.Rect(
                        menu.rect.x + menu_offset_x,
                        menu.rect.y + menu_offset_y,
                        menu.rect.width,
                        menu.rect.height
                    )
                    if menu_rect.collidepoint(x, y):
                        temp_menu = menu
                
                # If we found any element in this menu, use it and stop checking lower menus
                if temp_button or temp_toggle or temp_slider or temp_text_display or temp_image or temp_scrollable_area or temp_menu:
                    button_clicked = temp_button
                    toggle_clicked = temp_toggle
                    slider_clicked = temp_slider
                    text_display_clicked = temp_text_display
                    image_clicked = temp_image
                    scrollable_area_clicked = temp_scrollable_area
                    menu_clicked = temp_menu
                    break  # Stop checking lower priority menus
        
        # If no menu elements were clicked, check game state UI
        if not (button_clicked or toggle_clicked or slider_clicked or text_display_clicked or image_clicked or scrollable_area_clicked or menu_clicked):
            # Check the buttons for the current game state
            button_clicked = self.helper_manager.check_clickable_from_dict(
                self.buttons[state], (x, y)
            )
            toggle_clicked = self.helper_manager.check_clickable_from_dict(
                self.toggles[state], (x, y)
            )
            slider_clicked = self.helper_manager.check_clickable_from_dict(
                self.sliders[state], (x, y)
            )
            
            # If slider was clicked, check if it was specifically on the handle
            if slider_clicked:
                if slider_clicked.direction == "horizontal":
                    handle_rect = pygame.Rect(
                        slider_clicked.rect.x + slider_clicked.slider_position,
                        slider_clicked.rect.y,
                        slider_clicked.handle_surface.get_width(),
                        slider_clicked.handle_surface.get_height()
                    )
                else:  # vertical
                    handle_rect = pygame.Rect(
                        slider_clicked.rect.x,
                        slider_clicked.rect.y + slider_clicked.slider_position,
                        slider_clicked.handle_surface.get_width(),
                        slider_clicked.handle_surface.get_height()
                    )
                if not handle_rect.collidepoint(x, y):
                    slider_clicked = None
            
            # TextDisplay is display-only, but selectable in dev mode
            text_display_clicked = None
            if self.game_manager.dev_mode:
                text_display_clicked = self.helper_manager.check_clickable_from_dict(
                    self.text_display[state], (x, y)
                )
            
            image_clicked = self.helper_manager.check_clickable_from_dict(
                self.images[state], (x, y)
            )
            scrollable_area_clicked = self.helper_manager.check_clickable_from_dict(
                self.scrollable_areas[state], (x, y)
            )
            
            # If scrollable area was clicked, check if it was specifically on the slider handle
            if scrollable_area_clicked:
                slider = scrollable_area_clicked.slider
                if slider.direction == "horizontal":
                    handle_rect = pygame.Rect(
                        scrollable_area_clicked.rect.x + slider.rect.x + slider.slider_position,
                        scrollable_area_clicked.rect.y + slider.rect.y,
                        slider.handle_surface.get_width(),
                        slider.handle_surface.get_height()
                    )
                else:  # vertical
                    handle_rect = pygame.Rect(
                        scrollable_area_clicked.rect.x + slider.rect.x,
                        scrollable_area_clicked.rect.y + slider.rect.y + slider.slider_position,
                        slider.handle_surface.get_width(),
                        slider.handle_surface.get_height()
                    )
                if not handle_rect.collidepoint(x, y):
                    scrollable_area_clicked = None

        # Set the active clickable object, check menu first because it has lowest priority
        if menu_clicked:
            self.active = menu_clicked

        if button_clicked:
            self.active = button_clicked

        if toggle_clicked:
            self.active = toggle_clicked

        if slider_clicked:
            self.active = slider_clicked

        if text_display_clicked:
            self.active = text_display_clicked

        if image_clicked:
            self.active = image_clicked

        if scrollable_area_clicked:
            self.active = scrollable_area_clicked

        if self.prev_active and self.prev_active != self.active:
            self.prev_active.is_active = False
        if self.active:
            self.active.is_active = True

    def _handle_mouse_motion(self, x: int, y: int) -> None:
        """Handle mouse motion events."""
        # Find distance from start to current position
        dx = x - self.start_x
        dy = y - self.start_y
        drag_distance = math.sqrt(abs(dx)**2 + abs(dy)**2)
        
        if self.clicked and drag_distance > 5:
            self.dragging = True

        if not self.game_manager.dev_mode:
            # Handle drag updates
            if self.dragging and isinstance(self.active, Slider):
                self.active.update_location(x, y)
            elif self.dragging and isinstance(self.active, ScrollableArea):
                # Handle scrollable area's internal slider dragging
                # Pass absolute coordinates - ScrollableArea will adjust them
                self.active.update_scroll(x, y)
        else:
            # In dev mode, we can move any ui element around
            if self.active:
                if self.dragging:
                    self.active.dev_mode_drag(dx - self.prev_dx, dy - self.prev_dy)
                if not self.active.is_active:
                    self.active.is_active = True

        self.prev_dx = dx
        self.prev_dy = dy

    def _handle_mouse_button_up(self, x: int, y: int) -> None:
        """Handle mouse button up events."""
        self.click_end_x = x
        self.click_end_y = y
        self.dragging = False
        self.clicked = False

        if self.active and not self.game_manager.dev_mode:
            self.handle_click()

        # In normal mode, sliders and scrollable areas become inactive after release
        # In dev mode, keep them active for command execution
        if not self.game_manager.dev_mode:
            if isinstance(self.active, Slider):
                self.active.is_active = False
                # Trigger slider callback after drag completes, regardless of mouse position
                if self.active.callback:
                    self.active.callback()
                self.active = None
            elif isinstance(self.active, ScrollableArea):
                self.active.is_active = False
                self.active = None

    def handle_click(self) -> None:
        """Process a click event on the active UI element."""
        x = self.click_end_x
        y = self.click_end_y

        # If the click ended inside the clickable object, call its handler
        assert self.active is not None
        handler = None
        
        # Check if active element is in a menu
        from src.ui.elements.menu import Menu
        clicked_in_menu = False
        
        if isinstance(self.active, Menu):
            # Menu itself was clicked (dev mode)
            clicked_in_menu = True
        else:
            # Check if element is a child of any open menu
            input_manager = self.game_manager.input_manager if hasattr(self.game_manager, 'input_manager') else None
            if input_manager:
                for menu in input_manager.get_open_menus():
                    if self.active.parent == menu or self._is_descendant_of(self.active, menu):
                        menu_offset_x = menu.location[0]
                        menu_offset_y = menu.location[1]
                        if pygame.rect.Rect.collidepoint(
                            pygame.Rect(
                                self.active.rect.x + menu_offset_x, 
                                self.active.rect.y + menu_offset_y, 
                                self.active.rect.w, 
                                self.active.rect.h
                            ), 
                            (x, y)
                        ):
                            handler = getattr(self.active, 'callback', None)
                            clicked_in_menu = True
                            break
        
        # If not in menu, check game state UI
        if not clicked_in_menu:
            if pygame.rect.Rect.collidepoint(self.active.rect, (x, y)):
                handler = getattr(self.active, 'callback', None)

        if isinstance(self.active, Toggle):
            self.active.set_animating(self.graphics_manager.time)

        if handler:
            handler()
    
    def _is_descendant_of(self, element, ancestor):
        """Check if element is a descendant of ancestor in the hierarchy."""
        current = element.parent
        while current:
            if current == ancestor:
                return True
            current = current.parent
        return False

    def handle_drag(self, x: int, y: int) -> None:
        """Handle dragging of slider elements."""
        if self.active and isinstance(self.active, Slider):
            self.active.update_location(x, y)

        if self.active and isinstance(self.active, ScrollableArea):
            self.active.update_scroll(x, y)
