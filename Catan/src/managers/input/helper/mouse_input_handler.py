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
        
    def set_managers(self, game_manager, graphics_manager, helper_manager):
        """Set manager references."""
        self.game_manager = game_manager
        self.graphics_manager = graphics_manager
        self.helper_manager = helper_manager

    def set_ui_elements(self, buttons, toggles, sliders, images, text_display, menu):
        """Set UI element references."""
        self.buttons = buttons
        self.toggles = toggles
        self.sliders = sliders
        self.images = images
        self.text_display = text_display
        self.menu = menu

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

        # If the menu is open, we check the menu buttons first
        if self.graphics_manager.menu_open:
            # Use menu's current location as offset
            menu_offset_x = self.menu.location[0]
            menu_offset_y = self.menu.location[1]
            
            button_clicked: Button | None = self.helper_manager.check_clickable_from_dict(
                self.buttons["menu"][self.menu.active_tab], 
                (x, y), 
                menu_offset_x, 
                menu_offset_y
            )
            toggle_clicked: Toggle | None = self.helper_manager.check_clickable_from_dict(
                self.toggles["menu"][self.menu.active_tab], 
                (x, y), 
                menu_offset_x, 
                menu_offset_y
            )
            slider_clicked: Slider | None = self.helper_manager.check_clickable_from_dict(
                self.sliders["menu"][self.menu.active_tab], 
                (x, y), 
                menu_offset_x, 
                menu_offset_y
            )
            # TextDisplay is display-only, but selectable in dev mode
            text_display_clicked: TextDisplay | None = None
            if self.game_manager.dev_mode:
                text_display_clicked = self.helper_manager.check_clickable_from_dict(
                    self.text_display["menu"][self.menu.active_tab], 
                    (x, y),
                    menu_offset_x,
                    menu_offset_y
                )
            image_clicked: Image | None = self.helper_manager.check_clickable_from_dict(
                
                self.images["menu"][self.menu.active_tab], 
                (x, y),
                menu_offset_x,
                menu_offset_y
            )
            
            # If not, check the tabs of the menu
            if not button_clicked:
                button_clicked = self.helper_manager.check_clickable_from_dict(
                    self.buttons["menu"]["tabs"], 
                    (x, y), 
                    menu_offset_x, 
                    menu_offset_y
                )
            
            # In dev mode, check if the menu background itself was clicked
            menu_clicked: Menu | None = None
            if self.game_manager.dev_mode:
                menu_rect = pygame.Rect(
                    self.menu.rect.x + menu_offset_x,
                    self.menu.rect.y + menu_offset_y,
                    self.menu.rect.width,
                    self.menu.rect.height
                )
                if menu_rect.collidepoint(x, y):
                    menu_clicked = self.menu

        else:
            # If the menu is not open, we check the buttons for the current game state
            button_clicked: Button | None = self.helper_manager.check_clickable_from_dict(
                self.buttons[state], (x, y)
            )
            toggle_clicked: Toggle | None = self.helper_manager.check_clickable_from_dict(
                self.toggles[state], (x, y)
            )
            slider_clicked: Slider | None = self.helper_manager.check_clickable_from_dict(
                self.sliders[state], (x, y)
            )
            # TextDisplay is display-only, but selectable in dev mode
            text_display_clicked: TextDisplay | None = None
            if self.game_manager.dev_mode:
                text_display_clicked = self.helper_manager.check_clickable_from_dict(
                    self.text_display[state], (x, y)
                )
            image_clicked: Image | None = self.helper_manager.check_clickable_from_dict(
                self.images[state], (x, y)
            )

            menu_clicked: Menu | None = None

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
                if self.graphics_manager.menu_open:
                    self.handle_drag(
                        x - self.menu.location[0], 
                        y - self.menu.location[1]
                    )
                else:
                    self.handle_drag(x, y)
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

        # In normal mode, sliders become inactive after release
        # In dev mode, keep them active for command execution
        if isinstance(self.active, Slider) and not self.game_manager.dev_mode:
            self.active.is_active = False
            # Trigger slider callback after drag completes, regardless of mouse position
            if self.active.callback:
                self.active.callback()
            self.active = None

    def handle_click(self) -> None:
        """Process a click event on the active UI element."""
        x = self.click_end_x
        y = self.click_end_y

        # If the click ended inside the clickable object, call its handler
        assert self.active is not None
        handler = None
        
        if self.graphics_manager.menu_open:
            if pygame.rect.Rect.collidepoint(
                pygame.Rect(
                    self.active.rect.x + self.menu.location[0], 
                    self.active.rect.y + self.menu.location[1], 
                    self.active.rect.w, 
                    self.active.rect.h
                ), 
                (x, y)
            ):
                handler = getattr(self.active, 'callback', None)
            if isinstance(self.active, Toggle):
                self.active.set_animating(self.graphics_manager.time)
        else:
            if pygame.rect.Rect.collidepoint(self.active.rect, (x, y)):
                handler = getattr(self.active, 'callback', None)

            if isinstance(self.active, Toggle):
                self.active.set_animating(self.graphics_manager.time)

        if handler:
            handler()

    def handle_drag(self, x: int, y: int) -> None:
        """Handle dragging of slider elements."""
        if self.active and isinstance(self.active, Slider):
            self.active.update_location(x, y)
