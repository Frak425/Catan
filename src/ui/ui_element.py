import pygame
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Optional, List

from src.managers.animation.animation import SpriteAnimation
from src.managers.animation.driver import AnimationDriver

if TYPE_CHECKING:
    from src.managers.game.game_manager import GameManager


class UIElement(ABC):
    """
    Abstract base class for all UI elements with hierarchical positioning and common functionality.
    
    Responsibilities:
    - Manage parent-child relationships for nested UI (e.g., buttons inside menus)
    - Provide coordinate system conversion (relative → absolute screen coordinates)
    - Cache absolute positions for performance (invalidated on position changes)
    - Handle common properties (rect, name, shown state, active state)
    - Provide dev mode functionality (drag-to-reposition, guiding lines)
    - Define interface for serialization (read_layout/get_layout)
    
    Coordinate Systems:
    - Relative Coordinates (self.rect): Position relative to parent element
      Example: Button at (10, 20) inside Menu at (100, 150) → Button's rect = (10, 20)
    - Absolute Coordinates (get_absolute_rect()): Position in screen space
      Example: Same button → Absolute rect = (110, 170)
    
    Hierarchy System:
    - Elements can have parent (self.parent) and children (self.children)
    - Absolute positions calculated by walking up parent chain
    - Position changes invalidate cached absolute rects recursively
    - Children drawn relative to parent's absolute position
    
    Caching Strategy:
    - _absolute_rect: Cached screen coordinates (None when invalid)
    - _invalidate_absolute_rect(): Recursively invalidates cache on position change
    - get_absolute_rect(): Recalculates and caches on first access after invalidation
    
    Abstract Methods (must be implemented by subclasses):
    - draw(): Render element to surface
    - read_layout(): Parse layout properties from config dict
    - get_layout(): Serialize layout properties to config dict
    - print_info(): Debug output with all element properties
    
    Common Subclasses:
    - Button, Slider, Toggle, Image, TextDisplay (interactive elements)
    - Menu, ScrollableArea (container elements with children)
    """
    
    ## --- INITIALIZATION --- ##
    
    def __init__(self, layout_props: dict, game_manager: 'GameManager', callback: Optional[Callable] = None, shown: bool = True):
        """
        Initialize UIElement with common properties.
        
        Args:
            layout_props: Dictionary of layout properties from config (processed by read_layout)
            game_manager: Central game state manager (provides dev_mode flag)
            callback: Optional function called on interaction (e.g., button click)
            shown: Initial visibility state (False = hidden, not drawn)
        
        Common Properties Initialized:
        - name: Element identifier (empty string by default)
        - rect: Relative position/size (0,0,0,0 by default)
        - guiding_line_color: Dev mode outline color (default: blue)
        - is_active: Selection state for mouse/keyboard input
        - parent/children: Hierarchy relationships (None/[] by default)
        - _absolute_rect: Cached screen coordinates (None = needs calculation)
        
        Note: Subclasses should set their own defaults before calling read_layout().
              This allows defaults to be overridden by config properties.
        """
        self.game_manager = game_manager
        self.callback = callback
        self.shown = shown
        
        # Initialize common defaults
        self.name = ""
        self.rect = pygame.Rect(0, 0, 0, 0)  # Position relative to parent
        self.offset = (0, 0)
        self.guiding_line_color = (100, 100, 200)
        self.is_active = False
        self.active = True
        
        # Hierarchical relationship management
        self.parent: Optional['UIElement'] = None
        self.children: List['UIElement'] = []
        self._absolute_rect: Optional[pygame.Rect] = None  # Cached screen coordinates
        
        # Animation management
        self.animation: Optional[SpriteAnimation] = None
        self.drivers: List[tuple[str, AnimationDriver]] = []

        # Subclasses can add their own defaults before calling read_layout
    
    ## --- CALLBACK EXECUTION --- ##
    
    def trigger(self):
        """
        Execute the callback function if one is assigned.
        
        Use Cases:
        - Button clicks: Execute action when button pressed
        - Slider changes: Update setting when value changes
        - Toggle switches: Apply state change when toggled
        
        Note: Called by input handlers after validating interaction.
              Checks for callback existence before calling (no-op if None).
        """
        if self.callback:
            self.callback()
    
    ## --- HIERARCHY MANAGEMENT --- ##
    
    def add_child(self, child: 'UIElement') -> None:
        """
        Add a child element and establish parent-child relationship.
        
        Args:
            child: UIElement to add as child
        
        Process:
        1. Set child.parent = self
        2. Append child to self.children list
        3. Invalidate child's absolute rect cache (position changed)
        
        Effects:
        - Child's position becomes relative to this element
        - Child will be drawn at parent's absolute position + child's relative rect
        - Child will be clipped to parent's bounds (if parent implements clipping)
        
        Use Cases:
        - Buttons inside menus
        - Elements inside scrollable areas
        - UI groups with coordinated movement
        """
        child.parent = self
        self.children.append(child)
        child._invalidate_absolute_rect()
    
    def remove_child(self, child: 'UIElement') -> None:
        """
        Remove a child element and break parent-child relationship.
        
        Args:
            child: UIElement to remove from children
        
        Process:
        1. Set child.parent = None (orphan the child)
        2. Remove child from self.children list
        3. Invalidate child's absolute rect cache (position context changed)
        
        Note: Only removes if child is in self.children list.
              Child continues to exist but is no longer attached to hierarchy.
        """
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            child._invalidate_absolute_rect()
    
    ## --- ANIMATION AND DRIVER MANAGEMENT --- ##

    def set_animation(self, animation: SpriteAnimation) -> None:
        """
        Assign an animation to the UI element.
        
        Args:
            animation: Animation object to assign
        
        Note: Placeholder method for future animation handling.
              Subclasses can override to implement specific animations.
        """
        self.animation = animation
        if self.animation and not self.animation.animating:
            self.animation.start(self._get_time())

    def add_driver(self, driver: AnimationDriver | dict) -> None:
        """
        Assign a driver to the UI element.
        
        Args:
            driver: Driver object to assign
        
        Note: Placeholder method for future driver handling.
              Subclasses can override to implement specific drivers.
        """
        # Support both AnimationDriver and dict-based driver definitions.
        if isinstance(driver, AnimationDriver):
            self.drivers.append(("", driver))
            return

        # Dict format: {"property_name": "rect.x", "driver": AnimationDriver}
        if isinstance(driver, dict) and "driver" in driver and "property_name" in driver:
            if isinstance(driver["driver"], AnimationDriver):
                self.drivers.append((driver["property_name"], driver["driver"]))
            return

        # Dict format: {"rect.x": AnimationDriver, ...}
        if isinstance(driver, dict):
            for prop, driver_obj in driver.items():
                if isinstance(driver_obj, AnimationDriver):
                    self.drivers.append((prop, driver_obj))
            return

    ## --- COORDINATE SYSTEM --- ##
    
    def _invalidate_absolute_rect(self) -> None:
        """
        Mark absolute rect as needing recalculation and propagate to children.
        
        Process:
        1. Set self._absolute_rect = None (cache miss on next access)
        2. Recursively invalidate all children (their positions also changed)
        
        Called When:
        - Element position changes (dev_mode_drag, property modification)
        - Parent relationship changes (add_child, remove_child)
        - Parent position changes (recursive propagation)
        
        Performance Note:
        - Invalidation is fast (just setting None)
        - Recalculation deferred until get_absolute_rect() called
        - Avoids redundant calculations when multiple changes occur
        """
        self._absolute_rect = None
        for child in self.children:
            child._invalidate_absolute_rect()
    
    def get_absolute_rect(self) -> pygame.Rect:
        """
        Get rect in screen coordinates by walking up parent chain.
        
        Returns:
            pygame.Rect: Screen-space rectangle (absolute coordinates)
        
        Algorithm:
        1. If cached (_absolute_rect is not None), return cache
        2. If has parent:
           a. Get parent's absolute rect (may recursively calculate)
           b. Add self.rect offset to parent's position
           c. Create new Rect with absolute position, keep same size
        3. If no parent (root element):
           - Copy self.rect (already in screen coordinates)
        4. Cache result in _absolute_rect
        5. Return cached rect
        
        Example:
        - Menu at screen (100, 150)
        - Button at relative (10, 20) inside menu
        - Button's absolute rect = (110, 170)
        
        Performance:
        - O(1) for cached values
        - O(depth) for cache miss (walks parent chain)
        - Cache invalidated on position changes
        """
        if self._absolute_rect is None:
            if self.parent:
                parent_rect = self.parent.get_absolute_rect()
                self._absolute_rect = pygame.Rect(
                    parent_rect.x + self.rect.x,
                    parent_rect.y + self.rect.y,
                    self.rect.width,
                    self.rect.height
                )
            else:
                self._absolute_rect = self.rect.copy()
        return self._absolute_rect
    
    def get_clip_rect(self) -> Optional[pygame.Rect]:
        """
        Get the clipping region for this element in screen coordinates.
        
        Returns:
            pygame.Rect or None: Clipping bounds in screen space, or None for no clipping
        
        Clipping Hierarchy:
        - Walks up parent chain to find clipping boundary
        - Child elements inherit parent's clip region
        - Used by containers (Menu, ScrollableArea) to hide overflow
        
        Default Behavior:
        - Returns parent's clip rect (recursive delegation)
        - Root elements return None (no clipping)
        
        Override in Subclasses:
        - Menu: Return own rect to clip children to menu bounds
        - ScrollableArea: Return viewport rect to hide scrolled content
        
        Use Case:
        - Button inside menu stays within menu boundaries
        - Scrolled content hidden outside viewport
        """
        if self.parent:
            return self.parent.get_clip_rect()
        return None
    
    ## --- EVENT HANDLING --- ##
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame event and propagate to children using top-to-bottom ordering.
        
        Args:
            event: pygame event (MOUSEBUTTONDOWN, KEYDOWN, etc.)
        
        Returns:
            bool: True if event was consumed (stop propagation), False otherwise
        
        Process:
        1. If element hidden (shown=False), return False (skip processing)
        2. Iterate children in reverse order (top-to-bottom, last drawn = first handled)
        3. If any child consumes event, return True (stop propagation)
        4. If no child consumed, call _handle_own_event()
        5. Return result from own handler
        
        Event Propagation:
        - Children process before parents (inner elements first)
        - Reverse order matches draw order (top element gets priority)
        - First consumer stops propagation (prevents multiple triggers)
        
        Note: Most elements delegate to InputManager instead of using this.
              This provides alternative event handling path for custom elements.
        """
        if not self.shown or not self.active:
            return False
        
        # Let children handle first (reverse order for top-to-bottom)
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
        
        # Handle own event logic
        return self._handle_own_event(event)
    
    def _handle_own_event(self, event: pygame.event.Event) -> bool:
        """
        Handle element-specific event logic. Override in subclasses.
        
        Args:
            event: pygame event to process
        
        Returns:
            bool: True if consumed, False if ignored
        
        Default Implementation:
        - Returns False (no-op, doesn't consume events)
        
        Override Examples:
        - Button: Check for click in bounds, trigger callback, return True
        - Slider: Check for drag, update value, return True
        - TextInput: Check for typing, append character, return True
        
        Note: Most elements don't override this - they use InputManager delegation.
        """
        return False
    
    ## --- ABSTRACT INTERFACE (MUST IMPLEMENT IN SUBCLASSES) --- ##
    
    @abstractmethod
    def draw(self, surface: pygame.Surface, time: int) -> None:
        """
        Draw the UI element to the surface. Must be implemented by subclasses.
        
        Args:
            surface: pygame.Surface to draw on (usually screen or parent container)
        
        Implementation Requirements:
        1. Check self.shown (return early if False)
        2. Get absolute rect via get_absolute_rect()
        3. Draw element at absolute position
        4. Handle clipping if needed (get_clip_rect())
        5. Draw children recursively if applicable
        6. Call draw_guiding_lines() in dev mode
        
        Coordinate System:
        - Use absolute coordinates for drawing (get_absolute_rect())
        - Children use relative coordinates (self.rect)
        
        Common Pattern:
        ```python
        if not self.shown:
            return
        abs_rect = self.get_absolute_rect()
        pygame.draw.rect(surface, self.color, abs_rect)
        for child in self.children:
            child.draw(surface)
        self.draw_guiding_lines(surface)
        ```
        """
        pass
    
    @abstractmethod
    def read_layout(self, layout_props: dict) -> None:
        """
        Read layout properties from config dict. Must be implemented by subclasses.
        
        Args:
            layout_props: Dictionary from layout.json with element properties
        
        Implementation Requirements:
        1. Call self._read_common_layout(layout_props) to parse base properties
        2. Parse element-specific properties with get() and defaults
        3. Convert lists to tuples where needed (colors, positions)
        4. Validate and clamp values if necessary
        
        Common Properties (handled by _read_common_layout):
        - name: Element identifier string
        - rect: [x, y, width, height] array
        - guiding_line_color: [r, g, b] array
        - children: Array of child element names (deferred loading)
        
        Example Implementation:
        ```python
        def read_layout(self, layout_props: dict) -> None:
            self._read_common_layout(layout_props)
            self.color = tuple(layout_props.get('color', list(self.color)))
            self.text = layout_props.get('text', self.text)
        ```
        """
        pass
    
    @abstractmethod
    def get_layout(self) -> dict:
        """
        Get layout properties as dict for serialization. Must be implemented by subclasses.
        
        Returns:
            dict: Layout properties matching read_layout format
        
        Implementation Requirements:
        1. Call self._get_common_layout() to get base properties
        2. Add element-specific properties to returned dict
        3. Convert tuples to lists for JSON compatibility
        4. Match structure expected by read_layout()
        
        Common Properties (handled by _get_common_layout):
        - name: Element identifier
        - rect: Position and size array
        - guiding_line_color: RGB array
        - children: Array of child names (if has children)
        
        Example Implementation:
        ```python
        def get_layout(self) -> dict:
            layout = self._get_common_layout()
            layout['color'] = list(self.color)
            layout['text'] = self.text
            return layout
        ```
        """
        pass
    
    @abstractmethod
    def print_info(self) -> None:
        """
        Print all variable info about the UI element for debugging.
        
        Implementation Requirements:
        1. Call self.print_common_info() to print base properties
        2. Print element-specific properties with labels
        3. Format output for readability
        
        Common Properties (handled by print_common_info):
        - Name, Rect, Shown state, Guiding line color
        
        Example Implementation:
        ```python
        def print_info(self) -> None:
            self.print_common_info()
            print(f"Color: {self.color}")
            print(f"Text: {self.text}")
            print(f"Callback: {self.callback}")
        ```
        
        Use Case:
        - Dev mode 'print_info' command
        - Debugging element state
        - Verifying config loaded correctly
        """
        pass

    def _get_time(self) -> int:
        """Get current time in milliseconds for animations/drivers."""
        graphics_manager = getattr(self.game_manager, "graphics_manager", None)
        if graphics_manager and hasattr(graphics_manager, "time"):
            return graphics_manager.time
        return pygame.time.get_ticks()

    def _apply_driver_value(self, property_path: str, value: float) -> None:
        """Apply driver output to a property path (supports dot notation)."""
        if not property_path:
            return

        target = self
        parts = property_path.split(".")
        for part in parts[:-1]:
            if not hasattr(target, part):
                return
            target = getattr(target, part)

        if not hasattr(target, parts[-1]):
            return

        setattr(target, parts[-1], value)
        if property_path.startswith("rect."):
            self._invalidate_absolute_rect()

    def update(self):
        """Update any drivers and animations for this element."""
        current_time = self._get_time()
        if self.drivers:
            for prop, driver in self.drivers:
                driver.update(current_time)
                self._apply_driver_value(prop, driver.value)

        if self.animation:
            if not self.animation.animating:
                self.animation.start(current_time)
            self.animation.update(current_time)

    ## --- OPTIONAL OVERRIDES (DEFAULT IMPLEMENTATIONS PROVIDED) --- ##

    def print_common_info(self) -> None:
        """
        Print common properties shared by all UI elements.
        
        Output:
        - Name: Element identifier
        - Rect: Position and size (x, y, w, h)
        - Shown: Visibility state
        - Guiding Line Color: Dev mode outline color
        
        Note: Called by subclass print_info() before printing specific properties.
        """
        print(f"Name: {self.name}")
        print(f"Rect: {self.rect}")
        print(f"Shown: {self.shown}")
        print(f"Active: {self.active}")
        print(f"Guiding Line Color: {self.guiding_line_color}")

    def read_settings(self, settings: dict) -> None:
        """
        Read runtime settings from config. Override in subclasses if needed.
        
        Args:
            settings: Dictionary from settings_state.json
        
        Default Implementation:
        - No-op (base class has no settings)
        
        Override Examples:
        - Slider: Read current value from settings
        - Toggle: Read on/off state from settings
        - Menu: Read open/closed state from settings
        
        Difference from read_layout:
        - read_layout: Static properties (position, size, colors)
        - read_settings: Dynamic state (values, positions, shown state)
        """
        pass
    
    def get_settings(self) -> dict:
        """
        Get runtime settings as dict for serialization. Override in subclasses if needed.
        
        Returns:
            dict: Settings properties matching read_settings format
        
        Default Implementation:
        - Returns empty dict (base class has no settings)
        
        Override Examples:
        - Slider: Return current value
        - Toggle: Return on/off state
        - Menu: Return open/closed state
        
        Use Case:
        - Save settings_state.json with current UI state
        - Restore UI to previous state on next launch
        """
        return {}
    
    ## --- VISIBILITY CONTROL --- ##
    
    def hide(self) -> None:
        """
        Hide the UI element (will not be drawn or receive events).
        
        Effect:
        - Sets shown = False
        - Element skipped in draw() calls
        - Element skipped in event handling
        - Children still exist but not drawn (inherit parent's shown state)
        
        Note: Does not affect position or other properties, only visibility.
        """
        self.shown = False
    
    def show(self) -> None:
        """
        Show the UI element (will be drawn and receive events).
        
        Effect:
        - Sets shown = True
        - Element drawn in next frame
        - Element receives events normally
        - Children drawn if they are also shown
        
        Note: Does not affect position or other properties, only visibility.
        """
        self.shown = True

    def deactivate(self) -> None:
        """Deactivate element interaction while keeping it visible."""
        self.active = False

    def activate(self) -> None:
        """Activate element interaction."""
        self.active = True
    
    ## --- ANIMATION HANDLING --- ##

    def update_animation(self, delta_time: float) -> None:
        """
        Update any animations for the UI element. Override in subclasses if needed.
        
        Args:
            delta_time: Time elapsed since last update (in seconds)
        
        Default Implementation:
        - No-op (base class has no animations)
        
        Override Examples:
        - Button: Animate special effects on hover/click
        - Slider: Animate thumb movement
        - Toggle: Animate switch transition
        
        Use Case:
        - Called each frame by InputManager or GameManager
        - Allows smooth visual updates independent of input events
        """
        pass


    def update_drivers(self, delta_time: float) -> None:
        """
        Update any driver-based properties for the UI element. Override in subclasses if needed.
        
        Args:
            delta_time: Time elapsed since last update (in seconds)
        
        Default Implementation:
        - No-op (base class has no drivers)
        
        Override Examples:
        - Slider: Update value based on external data source
        - TextDisplay: Update text content from game state
        - Image: Change image based on game events
        
        Use Case:
        - Called each frame by InputManager or GameManager
        - Allows dynamic updates driven by game logic or external inputs

        A driver is of the form:
        {
            "property_name": "text",
            "driver": DriverObject
        }

        """
        pass

    ## --- DEV MODE FUNCTIONALITY --- ##
    
    def dev_mode_drag(self, x: int, y: int) -> None:
        """
        Move the UI element by the given offset in dev mode.
        
        Args:
            x: Horizontal offset in pixels (can be negative)
            y: Vertical offset in pixels (can be negative)
        
        Process:
        1. Add offset to self.rect.x and self.rect.y
        2. Invalidate absolute rect cache (position changed)
        3. Children move with parent (relative positions unchanged)
        
        Usage:
        - Mouse drag: Called continuously with delta from MouseInputHandler
        - Arrow keys: Called with ±1 offsets from KeyboardInputHandler
        
        Note: Only available when game_manager.dev_mode = True.
              Changes are saved when 'S' key pressed in dev mode.
        """
        self.rect.x += x
        self.rect.y += y
        self._invalidate_absolute_rect()
    
    def draw_guiding_lines(self, surface: pygame.Surface) -> None:
        """
        Draw rectangular outline around element for dev mode positioning.
        
        Args:
            surface: pygame.Surface to draw on (usually screen)
        
        Visual:
        - Draws 4 lines forming rectangle around element bounds
        - Color: self.guiding_line_color (default: blue)
        - Width: 1 pixel
        - Uses absolute coordinates (screen space)
        
        Behavior:
        - Only drawn when game_manager.dev_mode = True
        - Helps visualize element boundaries during layout
        - Shows clickable areas and alignment
        
        Note: Call at end of draw() method to render on top of element.
        """
        if self.game_manager.dev_mode:
            abs_rect = self.get_absolute_rect()
            pygame.draw.line(surface, self.guiding_line_color, 
                           (abs_rect.x, abs_rect.y), 
                           (abs_rect.x + abs_rect.width, abs_rect.y), 1)
            pygame.draw.line(surface, self.guiding_line_color, 
                           (abs_rect.x, abs_rect.y), 
                           (abs_rect.x, abs_rect.y + abs_rect.height), 1)
            pygame.draw.line(surface, self.guiding_line_color, 
                           (abs_rect.x + abs_rect.width, abs_rect.y), 
                           (abs_rect.x + abs_rect.width, abs_rect.y + abs_rect.height), 1)
            pygame.draw.line(surface, self.guiding_line_color, 
                           (abs_rect.x, abs_rect.y + abs_rect.height), 
                           (abs_rect.x + abs_rect.width, abs_rect.y + abs_rect.height), 1)

    def draw_inactive_overlay(self, surface: pygame.Surface, abs_rect: Optional[pygame.Rect] = None) -> None:
        """Draw translucent gray overlay to indicate deactivated state."""
        if self.active:
            return

        target_rect = abs_rect if abs_rect is not None else self.get_absolute_rect()
        if target_rect.width <= 0 or target_rect.height <= 0:
            return

        overlay = pygame.Surface((target_rect.width, target_rect.height), pygame.SRCALPHA)
        overlay.fill((120, 120, 120, 120))
        surface.blit(overlay, target_rect.topleft)
    
    ## --- SERIALIZATION HELPERS --- ##
    
    def _read_common_layout(self, layout_props: dict) -> None:
        """
        Helper to read common layout properties. Call from subclass read_layout().
        
        Args:
            layout_props: Dictionary from layout.json
        
        Properties Parsed:
        - name: Element identifier (default: keep existing)
        - rect: [x, y, width, height] array (default: current rect)
        - guiding_line_color: [r, g, b] array (default: current color)
        - children: Array of child element names (stored for deferred loading)
        
        Deferred Loading:
        - Children stored in _pending_children_names (not immediately added)
        - Actual child relationships restored by restore_child_relationships()
        - Required because children may not exist yet during parsing
        
        Usage Pattern:
        ```python
        def read_layout(self, layout_props: dict) -> None:
            self._read_common_layout(layout_props)  # First
            self.my_property = layout_props.get('my_property', default)  # Then
        ```
        """
        self.name = layout_props.get("name", self.name)
        rect_data = layout_props.get("rect", [self.rect.x, self.rect.y, self.rect.width, self.rect.height])
        self.rect = pygame.Rect(rect_data[0], rect_data[1], rect_data[2], rect_data[3])
        guiding_line_color_data = layout_props.get("guiding_line_color", 
                                                    [self.guiding_line_color[0], 
                                                     self.guiding_line_color[1], 
                                                     self.guiding_line_color[2]])
        self.guiding_line_color = (guiding_line_color_data[0], 
                                   guiding_line_color_data[1], 
                                   guiding_line_color_data[2])
        self.active = layout_props.get("active", self.active)
        
        # Store pending children names for deferred loading
        # (children must be created before they can be added)
        if "children" in layout_props:
            self._pending_children_names = layout_props["children"]
    
    def restore_child_relationships(self, element_registry: dict) -> None:
        """
        Restore child relationships after all elements are loaded.
        
        Args:
            element_registry: Dict mapping element names to UIElement instances
        
        Process:
        1. Check if _pending_children_names exists (set by _read_common_layout)
        2. For each child name, lookup element in registry
        3. Add child via add_child() (avoids duplicates)
        4. Delete _pending_children_names attribute (cleanup)
        
        Two-Phase Loading:
        Phase 1 (read_layout): Create all elements, store child names
        Phase 2 (restore_child_relationships): Link elements by name
        
        Why Deferred?
        - Child elements may not exist during parent's read_layout()
        - Load order in config is arbitrary
        - Registry must be complete before linking
        
        Note: Called by hierarchy loading utilities (save_ui_hierarchy/restore_ui_hierarchy).
        """
        if hasattr(self, '_pending_children_names'):
            for child_name in self._pending_children_names:
                if child_name in element_registry:
                    child = element_registry[child_name]
                    # Only add if not already a child (avoid duplicates)
                    if child not in self.children:
                        self.add_child(child)
            # Clear pending list after processing
            delattr(self, '_pending_children_names')
    
    def _get_common_layout(self) -> dict:
        """
        Helper to get common layout properties. Call from subclass get_layout().
        
        Returns:
            dict: Layout properties with common fields
        
        Properties Serialized:
        - name: Element identifier
        - rect: [x, y, width, height] array
        - guiding_line_color: [r, g, b] array
        - children: Array of child names (only if has named children)
        
        Children Serialization:
        - Only includes children with non-empty names
        - Stores names (not full objects) for reference
        - Children reconstructed during restore_child_relationships()
        
        Usage Pattern:
        ```python
        def get_layout(self) -> dict:
            layout = self._get_common_layout()  # Start with base
            layout['my_property'] = self.my_property  # Add specific
            return layout
        ```
        """
        layout = {
            "name": self.name,
            "rect": [self.rect.x, self.rect.y, self.rect.width, self.rect.height],
            "guiding_line_color": [self.guiding_line_color[0], 
                                  self.guiding_line_color[1], 
                                  self.guiding_line_color[2]],
            "active": self.active,
            "shown": self.shown
        }
        
        # Serialize children by name (if they have names)
        if self.children:
            children_names = [child.name for child in self.children if child.name]
            if children_names:
                layout["children"] = children_names
        
        return layout
