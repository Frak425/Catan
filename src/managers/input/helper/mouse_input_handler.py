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
    """
    Handles all mouse input events including clicks, drags, and motion.
    
    Responsibilities:
    - Process pygame mouse events (MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP)
    - Manage active/clicked UI element state
    - Handle dragging for sliders and scrollable areas
    - Support dev mode drag-to-reposition for all UI elements
    - Coordinate menu z-index priority (lower z-index = higher priority)
    - Dispatch click callbacks to appropriate UI elements
    
    Architecture:
    - Three-phase event handling: button_down → motion → button_up
    - Element priority: Open menus (by z-index) → game state UI
    - Click detection: dragging = False and distance < 5 pixels
    - Drag detection: clicked = True and distance > 5 pixels
    
    Dev Mode Features:
    - All UI elements become draggable for repositioning
    - TextDisplay and Menu backgrounds become selectable
    - Active elements stay selected until explicitly deselected
    """
    active: Button | Slider | Toggle | Button | Image | TextDisplay | Menu | None = None  # Currently active/clicked element
    prev_active: Button | Slider | Toggle | Button | Image | TextDisplay | Menu | None = None  # Previously active element
    # Manager references (set after initialization)
    game_manager: 'GameManager'
    graphics_manager: 'GraphicsManager'
    helper_manager: 'HelperManager'
    menu: Menu

    def __init__(self):
        """
        Initialize mouse input tracking state.
        
        State Variables:
        - dragging: True when mouse moves >5px while clicked
        - clicked: True between button_down and button_up
        - start_x/y: Mouse position when button was pressed
        - click_end_x/y: Mouse position when button was released
        - prev_dx/dy: Previous delta for smooth drag calculations
        
        UI Element Collections:
        - buttons, toggles, sliders: Organized by state/tab
        - scrollable_areas: Organized by state/tab
        - Populated by set_ui_elements() after creation
        """
        # Mouse state tracking
        self.dragging = False  # True when clicked and moved >5px
        self.clicked = False  # True between MOUSEBUTTONDOWN and MOUSEBUTTONUP
        self.start_x = 0  # X position when button pressed
        self.start_y = 0  # Y position when button pressed
        self.click_end_x = 0  # X position when button released
        self.click_end_y = 0  # Y position when button released
        self.prev_dx = 0  # Previous delta X for smooth dragging
        self.prev_dy = 0  # Previous delta Y for smooth dragging
        
        # UI element references (populated by set_ui_elements)
        self.buttons: Dict = {}
        self.toggles: Dict = {}
        self.sliders: Dict = {}
        self.scrollable_areas: Dict = {}
        
    ## --- DEPENDENCY INJECTION --- ##
    
    def set_managers(self, game_manager, graphics_manager, helper_manager):
        """
        Set manager dependencies required for mouse input handling.
        
        Args:
            game_manager: Central game state (dev_mode, game_state, input_manager access)
            graphics_manager: Graphics timing for toggle animations
            helper_manager: Collision detection utilities (check_clickable_from_dict)
        
        Note: Must be called before handle_mouse_input() to avoid AttributeError.
        """
        self.game_manager = game_manager
        self.graphics_manager = graphics_manager
        self.helper_manager = helper_manager

    def set_ui_elements(self, buttons, toggles, sliders, images, text_display, scrollable_areas, menus):
        """
        Set UI element collections for hit detection and interaction.
        
        Args:
            buttons: Dict[state][name] -> Button instances
            toggles: Dict[state][name] -> Toggle instances
            sliders: Dict[state][name] -> Slider instances
            images: Dict[state][name] -> Image instances
            text_display: Dict[state][name] -> TextDisplay instances
            scrollable_areas: Dict[state][name] -> ScrollableArea instances
            menus: Dict[name] -> Menu instances
        
        Structure:
        - States: "home", "setup", "game", "menu"
        - Menu tabs: "tabs", "input", "accessibility", "graphics", "audio", "gameplay"
        
        Note: Must be called after UIFactory creates all elements.
        """
        self.buttons = buttons
        self.toggles = toggles
        self.sliders = sliders
        self.images = images
        self.text_display = text_display
        self.scrollable_areas = scrollable_areas
        self.menus = menus
    
    ## --- COLLISION DETECTION HELPERS --- ##
    
    def _check_slider_handle_collision(self, slider: Slider, x: int, y: int, offset_x: int = 0, offset_y: int = 0) -> bool:
        """
        Check if mouse position collides with slider handle (not just slider track).
        
        Args:
            slider: The slider to check
            x: Mouse X coordinate
            y: Mouse Y coordinate
            offset_x: X offset (for menu-relative coordinates)
            offset_y: Y offset (for menu-relative coordinates)
        
        Returns:
            bool: True if mouse is over the handle, False otherwise
        
        Note: This prevents clicking the track from activating the slider.
              User must click the handle specifically to drag.
        """
        if slider.direction == "horizontal":
            handle_rect = pygame.Rect(
                slider.rect.x + slider.slider_position + offset_x,
                slider.rect.y + offset_y,
                slider.handle_surface.get_width(),
                slider.handle_surface.get_height()
            )
        else:  # vertical
            handle_rect = pygame.Rect(
                slider.rect.x + offset_x,
                slider.rect.y + slider.slider_position + offset_y,
                slider.handle_surface.get_width(),
                slider.handle_surface.get_height()
            )
        return handle_rect.collidepoint(x, y)
    
    def _check_scrollable_handle_collision(self, scrollable: ScrollableArea, x: int, y: int, offset_x: int = 0, offset_y: int = 0) -> bool:
        """
        Check if mouse position collides with scrollable area's slider handle.
        
        Args:
            scrollable: The scrollable area to check
            x: Mouse X coordinate
            y: Mouse Y coordinate
            offset_x: X offset (for menu-relative coordinates)
            offset_y: Y offset (for menu-relative coordinates)
        
        Returns:
            bool: True if mouse is over the scrollbar handle, False otherwise
        
        Note: ScrollableArea has internal slider - must check relative to container rect.
        """
        slider = scrollable.slider
        if slider.direction == "horizontal":
            handle_rect = pygame.Rect(
                scrollable.rect.x + slider.rect.x + slider.slider_position + offset_x,
                scrollable.rect.y + slider.rect.y + offset_y,
                slider.handle_surface.get_width(),
                slider.handle_surface.get_height()
            )
        else:  # vertical
            handle_rect = pygame.Rect(
                scrollable.rect.x + slider.rect.x + offset_x,
                scrollable.rect.y + slider.rect.y + slider.slider_position + offset_y,
                slider.handle_surface.get_width(),
                slider.handle_surface.get_height()
            )
        return handle_rect.collidepoint(x, y)

    ## --- MOUSE EVENT DISPATCHING --- ##
  
    def handle_mouse_input(self, x: int, y: int, event_type: int) -> None:
        """
        Main entry point for handling all mouse events.
        
        Args:
            x: Mouse X coordinate (screen space)
            y: Mouse Y coordinate (screen space)
            event_type: pygame event type (MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP)
        
        Event Flow:
        1. MOUSEBUTTONDOWN: Detect clicked element, set active, record start position
        2. MOUSEMOTION: Track dragging, update slider/scrollable positions or dev mode repositioning
        3. MOUSEBUTTONUP: Execute callbacks, reset state, handle click completion
        """
        if event_type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_button_down(x, y)
        elif event_type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(x, y)
        elif event_type == pygame.MOUSEBUTTONUP:
            self._handle_mouse_button_up(x, y)

    def _handle_mouse_button_down(self, x: int, y: int) -> None:
        """
        Handle mouse button down events - detect which UI element was clicked.
        
        Args:
            x: Mouse X coordinate at click
            y: Mouse Y coordinate at click
        
        Process:
        1. Deactivate previously active element
        2. Record click start position and set clicked=True
        3. Check open menus by z-index priority (lower = higher priority)
        4. For each menu (top to bottom), check all element types
        5. If menu element found, stop checking (don't check lower menus or game state)
        6. If no menu element, check game state UI elements
        7. Set self.active to highest priority clicked element
        8. Activate the new active element
        
        Priority Order (highest to lowest):
        - Open menu elements (by menu z-index, lower = higher)
        - Game state UI elements (home/setup/game)
        
        Element Priority within Same Context:
        - ScrollableArea > Image > TextDisplay > Slider > Toggle > Button > Menu background
        
        Note: In dev mode, TextDisplay and Menu backgrounds become clickable.
        """
        # Deactivate previously active element
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
        #image_clicked = None
        scrollable_area_clicked = None
        menu_clicked = None
        
        assert input_manager is not None, "input_manager not defined"
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
            
            # If slider was clicked, verify it was specifically on the handle (not track)
            if temp_slider and not self._check_slider_handle_collision(temp_slider, x, y, menu_offset_x, menu_offset_y):
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
            
            #temp_image = self.helper_manager.check_clickable_from_dict(
            #    self.images["menu"][menu.active_tab], 
            #    (x, y),
            #    menu_offset_x,
            #    menu_offset_y
            #)
            temp_scrollable_area = self.helper_manager.check_clickable_from_dict(
                self.scrollable_areas["menu"][menu.active_tab],
                (x, y),
                menu_offset_x,
                menu_offset_y
            )
            
            # If scrollable area was clicked, verify click was on scrollbar handle
            if temp_scrollable_area and not self._check_scrollable_handle_collision(temp_scrollable_area, x, y, menu_offset_x, menu_offset_y):
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
            if temp_button or temp_toggle or temp_slider or temp_text_display or temp_scrollable_area or temp_menu: #or temp_image
                button_clicked = temp_button
                toggle_clicked = temp_toggle
                slider_clicked = temp_slider
                text_display_clicked = temp_text_display
                #image_clicked = temp_image
                scrollable_area_clicked = temp_scrollable_area
                menu_clicked = temp_menu
                break  # Stop checking lower priority menus
    
        # If no menu elements were clicked, check game state UI
        if not (button_clicked or toggle_clicked or slider_clicked or text_display_clicked or scrollable_area_clicked or menu_clicked): #or image_clicked
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
            
            # If slider was clicked, verify it was specifically on the handle (not track)
            if slider_clicked and not self._check_slider_handle_collision(slider_clicked, x, y):
                slider_clicked = None
            
            # TextDisplay is display-only, but selectable in dev mode
            text_display_clicked = None
            if self.game_manager.dev_mode:
                text_display_clicked = self.helper_manager.check_clickable_from_dict(
                    self.text_display[state], (x, y)
                )
            
            #image_clicked = self.helper_manager.check_clickable_from_dict(
            #    self.images[state], (x, y)
            #)
            scrollable_area_clicked = self.helper_manager.check_clickable_from_dict(
                self.scrollable_areas[state], (x, y)
            )
            
            # If scrollable area was clicked, verify click was on scrollbar handle
            if scrollable_area_clicked and not self._check_scrollable_handle_collision(scrollable_area_clicked, x, y):
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

        #if image_clicked:
        #    self.active = image_clicked

        if scrollable_area_clicked:
            self.active = scrollable_area_clicked

        if self.prev_active and self.prev_active != self.active:
            self.prev_active.is_active = False
        if self.active:
            self.active.is_active = True

    def _handle_mouse_motion(self, x: int, y: int) -> None:
        """
        Handle mouse motion events - detect dragging and update element positions.
        
        Args:
            x: Current mouse X coordinate
            y: Current mouse Y coordinate
        
        Process:
        1. Calculate distance from click start position
        2. If clicked and moved >5px, set dragging=True
        3. In normal mode: Update slider/scrollable positions if active
        4. In dev mode: Move any active element by drag delta
        5. Track previous delta for smooth incremental movement
        
        Drag Distance Threshold:
        - >5 pixels: Considered a drag (prevents accidental drag on click)
        - <=5 pixels: Still considered a click
        """
        # Calculate distance from start to current position
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
        """
        Handle mouse button up events - complete click/drag and execute callbacks.
        
        Args:
            x: Mouse X coordinate at release
            y: Mouse Y coordinate at release
        
        Process:
        1. Record release position
        2. Reset dragging and clicked flags
        3. In normal mode: Execute click handler if active element exists
        4. Special handling for Slider: Call callback after drag completes
        5. Deactivate and clear sliders and scrollable areas (not persistent)
        
        Note: In dev mode, elements stay active for keyboard commands.
              In normal mode, sliders/scrollable areas auto-deactivate.
        """
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

    ## --- CLICK CALLBACK EXECUTION --- ##
    
    def handle_click(self) -> None:
        """
        Process a click event on the active UI element and execute its callback.
        
        Process:
        1. Verify click ended inside the element's rect (click completion)
        2. Check if element is in an open menu (needs offset coordinates)
        3. If not in menu, check game state UI (no offset)
        4. If click is valid, retrieve and execute element's callback
        5. For Toggles, trigger animation at current time
        
        Click Validation:
        - Must end inside element's rect (prevents drag-away cancellation)
        - Must account for menu offsets if element is in menu
        - Uses _is_descendant_of() to check menu hierarchy
        
        Note: Only called in normal mode (dev mode skips callbacks on release).
        """
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
    
    def _is_descendant_of(self, element, ancestor) -> bool:
        """
        Check if element is a descendant of ancestor in the UI hierarchy.
        
        Args:
            element: The UI element to check
            ancestor: The potential ancestor element (e.g., Menu)
        
        Returns:
            bool: True if element is a descendant of ancestor, False otherwise
        
        Algorithm:
        - Walk up the parent chain from element
        - If ancestor is found, return True
        - If reach root (parent=None), return False
        
        Use Case: Determine if element is inside a menu for offset calculations.
        """
        current = element.parent
        while current:
            if current == ancestor:
                return True
            current = current.parent
        return False
