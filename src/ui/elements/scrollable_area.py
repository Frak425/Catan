import pygame
from src.ui.elements.slider import Slider
from src.ui.ui_element import UIElement

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.managers.game.game_manager import GameManager

class ScrollableArea(UIElement):
    """
    Scrollable container for content larger than viewport with vertical slider.
    
    Features:
    - Vertical scrolling with mousewheel and slider
    - Viewport clipping (only visible content drawn)
    - Child element management with scroll offset
    - Configurable slider position (left/right)
    - Content area width percentage control
    
    Architecture:
    - Composite structure: background + content area + slider
    - Three coordinate spaces:
      1. Container rect: Full scrollable area including padding
      2. Content rect: Viewport where content is visible
      3. Scroll offset: Virtual position of content (-content_scroll pixels)
    - Slider controls content_scroll (0 to max_scroll)
    
    Layout:
    - exterior_padding: Space around entire container
    - content area: Left portion (content_width_percentage)
    - interior_padding: Gap between content and slider
    - slider: Right portion (remaining width)
    
    Coordinate Transform:
    - Child elements positioned relative to content area
    - get_absolute_rect() applies scroll offset for children
    - Drawing uses clipped subsurface for viewport
    """
    def __init__(self, layout_props: dict, game_manager: GameManager, content_surface: pygame.Surface) -> None:
        """
        Initialize scrollable area with content surface and slider.
        
        Args:
            layout_props: Configuration from layout.json
            game_manager: Central game state manager
            content_surface: Surface to display (can be larger than viewport)
        
        Properties:
        - exterior_padding: Space around entire area
        - interior_padding: Gap between content and slider
        - content_scroll: Current scroll position in pixels (0 to max_scroll)
        - content_width_percentage: Content area as fraction of usable width
        - slider_side: "right" or "left"
        - content_elements: Child UI elements that scroll with content
        """
        # Call parent constructor to initialize common UIElement attributes
        super().__init__(layout_props, game_manager, callback=None, shown=True)
        
        #TODO: implement theme class for images. Currently images are not passed in so default colors are used
        #set defaults
        self.rect = pygame.Rect(0, 0, 300, 400)
        self.exterior_padding = 5
        self.interior_padding = 5
        self.content_surface = content_surface
        self.content_scroll = 0  # current scroll position in pixels
        self.background_color = (240, 240, 240, 255)
        self.background_image = None 
        self.content_background_color = (255, 255, 255, 255)
        self.content_background_image = None
        self.content_elements: list[UIElement] = [] # chile ui elements
        self.content_width_percentage = .9 # percentage of total width for content area
        self.slider_image = None
        self.slider_handle_image = None
        self.slider_handle_inset = 2
        self.slider_side = "right"  # or "left"

        self.viewable_content_height = self.rect.height - 2 * self.exterior_padding
        # Calculate usable width (after exterior padding and interior padding between content and slider)
        usable_width = self.rect.width - 2 * self.exterior_padding - self.interior_padding
        self.viewable_content_width = int(usable_width * self.content_width_percentage)
        self.max_scroll = max(0, self.content_surface.get_height() - self.viewable_content_height)
        
        self.slider_height = self.viewable_content_height
        self.slider_width = usable_width - self.viewable_content_width
        self.slider_x = self.rect.width - self.exterior_padding - self.slider_width if self.slider_side == "right" else self.exterior_padding
        self.slider_y = self.exterior_padding


        self.slider_layout_props = {
            "name": "slider",
            "rect": [self.slider_x, self.slider_y, self.slider_width, self.slider_height],
            "min_value": 0,
            "max_value": 1,
            "color": [50, 50, 50],  # Dark gray bar
            "handle_color": [255, 255, 0],  # Bright yellow handle
            "handle_radius": int(self.slider_width / 2) - self.slider_handle_inset,
            "direction": "vertical",
            "handle_shape": "circle",
            "handle_length": 0
        }   

        self.read_layout(layout_props)

    ## --- CHILD ELEMENT MANAGEMENT --- ##

    def add_element(self, element: UIElement) -> None:
        """Add UI element to scrollable content and recalculate height."""
        self.add_child(element)  # Use parent method for hierarchy
        self.content_elements.append(element)
        self._recalculate_content_height()

    def remove_element(self, element: UIElement) -> None:
        """Remove UI element from scrollable content and recalculate height."""
        if element in self.content_elements:
            self.remove_child(element)  # Use parent method for hierarchy
            self.content_elements.remove(element)
            self._recalculate_content_height()

    def _recalculate_content_height(self) -> None:
        """
        Calculate total content height and update max scroll.
        
        Uses bottommost child element or content_surface height.
        Updates max_scroll to ensure content can't scroll beyond bottom.
        """
        if self.content_elements:
            max_bottom = max(elem.rect.y + elem.rect.height for elem in self.content_elements)
            self.content_height = max_bottom
        elif self.content_surface:
            self.content_height = self.content_surface.get_height()
        else:
            self.content_height = 0
        
        self.max_scroll = max(0, self.content_height - self.viewable_content_height)

    ## --- COORDINATE TRANSFORMS --- ##

    def _get_content_rect(self) -> pygame.Rect:
        """
        Get content area rect in container-relative coordinates.
        
        Returns rect accounting for exterior_padding but not scroll offset.
        Used for layout calculations, not drawing.
        """
        return pygame.Rect(
            self.rect.x + self.exterior_padding,
            self.rect.y + self.exterior_padding,
            self.viewable_content_width,
            self.viewable_content_height
        )
    
    def get_absolute_content_rect(self) -> pygame.Rect:
        """
        Get visible viewport area in screen coordinates (no scroll offset).
        
        Used for:
        - Drawing subsurface (clipping region)
        - Event collision detection
        - Determining what's visible
        
        Returns fixed screen-space rect regardless of scroll position.
        """
        abs_rect = super().get_absolute_rect()  # Get actual screen position
        return pygame.Rect(
            abs_rect.x + self.exterior_padding,
            abs_rect.y + self.exterior_padding,
            self.viewable_content_width,
            self.viewable_content_height
        )
    
    def get_clip_rect(self) -> pygame.Rect:
        """Return clipping rect for child elements (content viewport)."""
        return self.get_absolute_content_rect()
    
    def get_absolute_rect(self) -> pygame.Rect:
        """
        Override to apply scroll offset for child element positioning.
        
        CRITICAL: This method returns the content rect WITH scroll offset applied.
        Children use this to calculate their screen positions, making them scroll.
        
        Transform:
        - base_y includes -content_scroll offset
        - As content_scroll increases, children move up (negative Y)
        - Viewport (get_absolute_content_rect) stays fixed
        
        Returns rect that moves with scroll, not the visible viewport.
        """
        if self._absolute_rect is None:
            if self.parent:
                parent_rect = self.parent.get_absolute_rect()
                # Base position for the scrollable area itself
                base_x = parent_rect.x + self.rect.x + self.exterior_padding
                base_y = parent_rect.y + self.rect.y + self.exterior_padding - self.content_scroll
            else:
                base_x = self.rect.x + self.exterior_padding
                base_y = self.rect.y + self.exterior_padding - self.content_scroll
            
            self._absolute_rect = pygame.Rect(
                base_x,
                base_y,
                self.viewable_content_width,
                self.viewable_content_height
            )
        return self._absolute_rect

    ## --- EVENT HANDLING --- ##

    def _handle_own_event(self, event: pygame.event.Event) -> bool:
        """
        Handle scrolling events (mousewheel, slider drag).
        
        Event Priority:
        1. Mousewheel over content area: Direct scroll (20px per tick)
        2. Slider interaction: Delegated to slider (updates via callback)
        
        Scroll Update:
        - Updates content_scroll and invalidates absolute rects
        - Keeps scroll clamped to [0, max_scroll]
        - Syncs slider value with scroll position
        
        Returns True if event consumed.
        """
        # Handle mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            abs_content_rect = self.get_absolute_content_rect()
            mouse_pos = pygame.mouse.get_pos()
            if abs_content_rect.collidepoint(mouse_pos):
                # Scroll with mouse wheel
                self.content_scroll = max(0, min(
                    self.content_scroll - event.y * 20,  # 20 pixels per wheel tick
                    self.max_scroll
                ))
                self._invalidate_absolute_rect()  # Children positions changed
                # Update slider to reflect new scroll position
                if self.max_scroll > 0:
                    self.slider.value = self.content_scroll / self.max_scroll
                return True
        
        # Let slider handle its events
        if hasattr(self, 'slider') and self.slider:
            # Transform event coordinates for slider if needed
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                slider_abs_rect = pygame.Rect(
                    super().get_absolute_rect().x + self.slider.rect.x,
                    super().get_absolute_rect().y + self.slider.rect.y,
                    self.slider.rect.width,
                    self.slider.rect.height
                )
                mouse_pos = pygame.mouse.get_pos()
                if slider_abs_rect.collidepoint(mouse_pos):
                    # Let the slider handle this event
                    if hasattr(self.slider, 'handle_event'):
                        return self.slider.handle_event(event)
        
        return False

    ## --- RENDERING --- ##

    def draw(self, surface: pygame.Surface):
        """
        Draw scrollable area with viewport clipping.
        
        Rendering Order:
        1. Background (at actual_rect position, unaffected by scroll)
        2. Content surface and child elements (clipped to viewport, offset by scroll)
        3. Slider (at actual_rect position, on top of everything)
        """
        if not self.shown:
            return
        
        self.update()
        
        # Get actual screen position (not offset by scroll)
        actual_rect = super().get_absolute_rect()
        
        # Draw each component
        self._draw_background(surface, actual_rect)
        self._draw_content(surface, actual_rect)
        self._draw_slider(surface, actual_rect)
    
    def _draw_background(self, surface: pygame.Surface, actual_rect: pygame.Rect) -> None:
        """
        Draw background with clipping for off-screen positioning.
        
        Args:
            surface: Target surface to draw on
            actual_rect: Container's screen position (unscrolled)
        """
        surface_rect = surface.get_rect()
        if actual_rect.colliderect(surface_rect):
            # Clip background to visible area
            clipped_bg_rect = actual_rect.clip(surface_rect)
            if clipped_bg_rect.width > 0 and clipped_bg_rect.height > 0:
                # Calculate which part of the background to draw
                bg_offset_x = clipped_bg_rect.x - actual_rect.x
                bg_offset_y = clipped_bg_rect.y - actual_rect.y
                bg_source_rect = pygame.Rect(bg_offset_x, bg_offset_y, clipped_bg_rect.width, clipped_bg_rect.height)
                
                # Draw the visible portion of the background
                surface.blit(self.background_surface, (clipped_bg_rect.x, clipped_bg_rect.y), bg_source_rect)
    
    def _draw_content(self, surface: pygame.Surface, actual_rect: pygame.Rect) -> None:
        """
        Draw content surface and child elements with viewport clipping.
        
        Args:
            surface: Target surface to draw on
            actual_rect: Container's screen position (unscrolled)
        """
        # Get content area for clipping
        content_abs_rect = self.get_absolute_content_rect()
        
        # Clip content rect to surface bounds to handle off-screen positioning
        surface_rect = surface.get_rect()
        clipped_content_rect = content_abs_rect.clip(surface_rect)
        
        # Only draw content if there's a visible area
        if clipped_content_rect.width > 0 and clipped_content_rect.height > 0:
            try:
                content_area = surface.subsurface(clipped_content_rect)
                
                # Draw content surface if present
                if self.content_surface:
                    self._draw_content_surface(content_area, content_abs_rect, clipped_content_rect)
                
                # Draw child elements with clipping
                self._draw_child_elements(content_area, clipped_content_rect)
                
            except ValueError:
                # Subsurface creation failed - skip drawing content
                pass
    
    def _draw_content_surface(self, content_area: pygame.Surface, content_abs_rect: pygame.Rect, clipped_content_rect: pygame.Rect) -> None:
        """
        Draw the content surface within the clipped content area.
        
        Args:
            content_area: Subsurface to draw within (clipped viewport)
            content_abs_rect: Full content area rect (before clipping)
            clipped_content_rect: Visible portion of content area
        """
        # Calculate offset for drawing within the clipped area
        offset_x = clipped_content_rect.x - content_abs_rect.x
        offset_y = clipped_content_rect.y - content_abs_rect.y
        
        # Calculate source rectangle from content surface
        # When clipped, we need to skip the portion that's off-screen
        content_source_x = offset_x
        content_source_y = offset_y + self.content_scroll  # Add scroll offset to source
        content_source_rect = pygame.Rect(
            content_source_x,
            content_source_y,
            clipped_content_rect.width,
            clipped_content_rect.height
        )
        
        # Ensure source rect is within content surface bounds
        content_surface_rect = self.content_surface.get_rect()
        content_source_rect = content_source_rect.clip(content_surface_rect)
        
        # Draw the visible portion of content surface at (0,0) in subsurface
        if content_source_rect.width > 0 and content_source_rect.height > 0:
            content_area.blit(
                self.content_surface,
                (0, 0),  # Always draw at origin of subsurface
                content_source_rect
            )
    
    def _draw_child_elements(self, content_area: pygame.Surface, clipped_content_rect: pygame.Rect) -> None:
        """
        Draw child UI elements within the clipped content area.
        
        Args:
            content_area: Subsurface to draw within (clipped viewport)
            clipped_content_rect: Visible portion of content area
        """
        # Children use get_absolute_rect which includes scroll offset
        for element in self.content_elements:
            if element.shown:
                # Check if element is visible in viewport
                elem_abs_rect = element.get_absolute_rect()
                if (elem_abs_rect.y + elem_abs_rect.height > clipped_content_rect.y and 
                    elem_abs_rect.y < clipped_content_rect.y + clipped_content_rect.height):
                    element.draw(content_area)
    
    def _draw_slider(self, surface: pygame.Surface, actual_rect: pygame.Rect) -> None:
        """
        Draw slider on top of content area.
        
        Args:
            surface: Target surface to draw on
            actual_rect: Container's screen position (unscrolled)
        """
        if hasattr(self, 'slider') and self.slider:
            slider_abs_x = actual_rect.x + self.slider.rect.x
            slider_abs_y = actual_rect.y + self.slider.rect.y
            # Temporarily adjust slider rect for drawing
            original_slider_pos = (self.slider.rect.x, self.slider.rect.y)
            self.slider.rect.x = slider_abs_x
            self.slider.rect.y = slider_abs_y
            self.slider.draw(surface)
            # Restore slider position
            self.slider.rect.x, self.slider.rect.y = original_slider_pos

    ## --- SURFACE CREATION --- ##

    def create_surfaces(self):
        """Initialize background and slider (called after layout read)."""
        self.create_background_surface()
        self.create_slider()

    def create_background_surface(self):
        """Create background surface from image or solid color."""
        self.background_surface = pygame.Surface((self.rect.width, self.rect.height))
        if self.background_image:
            self.background_surface.blit(self.background_image, (0, 0))
        else:
            self.background_surface.fill(self.background_color)

    def create_slider(self):
        """
        Create vertical slider with callback to update scroll position.
        
        Slider value: 0.0 (top) to 1.0 (bottom)
        Callback: set_content_scroll() converts to pixel offset
        """
        self.slider = Slider(
            self.slider_layout_props,
            0,  # initial_value
            self.game_manager,
            bar_image=self.slider_image,
            handle_image=self.slider_handle_image,
            callback=self.set_content_scroll
        )

    def _invalidate_absolute_rect(self) -> None:
        """Override to update slider position when scrollable area moves."""
        super()._invalidate_absolute_rect()
        
        # Only update slider if we actually have one
        if hasattr(self, 'slider') and self.slider:
            # Recalculate slider dimensions based on current rect
            self.viewable_content_height = self.rect.height - 2 * self.exterior_padding
            usable_width = self.rect.width - 2 * self.exterior_padding - self.interior_padding
            self.viewable_content_width = int(usable_width * self.content_width_percentage)
            
            self.slider_width = usable_width - self.viewable_content_width
            self.slider_height = self.viewable_content_height
            self.slider_x = self.rect.width - self.exterior_padding - self.slider_width if self.slider_side == "right" else self.exterior_padding
            self.slider_y = self.exterior_padding
            
            # Update the actual slider rect directly
            self.slider.rect.x = self.slider_x
            self.slider.rect.y = self.slider_y  
            self.slider.rect.width = self.slider_width
            self.slider.rect.height = self.slider_height
            
            # Update slider's handle radius based on new width
            if hasattr(self.slider, 'handle_radius'):
                self.slider.handle_radius = int(self.slider_width / 2) - self.slider_handle_inset
            
            # Invalidate only the slider's absolute rect
            if hasattr(self.slider, '_invalidate_absolute_rect'):
                self.slider._invalidate_absolute_rect()

    def calculate_dependent_properties(self):
        """
        Recalculate viewport dimensions and slider layout from base properties.
        
        Called when rect, padding, or content_width_percentage changes.
        Updates slider_layout_props with new dimensions.
        """
        self.viewable_content_height = self.rect.height - 2 * self.exterior_padding
        # Calculate usable width (after exterior padding and interior padding between content and slider)
        usable_width = self.rect.width - 2 * self.exterior_padding - self.interior_padding
        self.viewable_content_width = int(usable_width * self.content_width_percentage)
        self.max_scroll = max(0, self.content_surface.get_height() - self.viewable_content_height)

        self.slider_width = usable_width - self.viewable_content_width
        self.slider_x = self.rect.width - self.exterior_padding - self.slider_width if self.slider_side == "right" else self.exterior_padding
        
        self.slider_layout_props.update({
            "rect": [self.slider_x, self.slider_y, self.slider_width, self.slider_height],
            "handle_radius": int(self.slider_width / 2) - self.slider_handle_inset
        })

    ## --- SCROLL CONTROL --- ##

    def set_content_scroll(self) -> None:
        """
        Update content scroll from slider value (callback from slider).
        
        Converts slider.value (0 to 1) to pixel offset (0 to max_scroll).
        Invalidates children absolute rects since they move with scroll.
        """
        self.content_scroll = self.slider.value * self.max_scroll
        self._invalidate_absolute_rect()  # Children positions changed

    def update_scroll(self, x: int, y: int) -> None:
        """
        Update scroll from mouse coordinates (legacy drag handler).
        
        Note: This may be unused - event handling now done via _handle_own_event.
        """
        # Adjust coordinates to be relative to the scrollable area
        relative_x = x - self.rect.x
        relative_y = y - self.rect.y
        self.slider.update_location(relative_x, relative_y)

    ## --- SERIALIZATION --- ##

    def read_layout(self, layout_props: dict) -> None:
        """
        Load scrollable area properties from config dict.
        
        Deferred Loading:
        - content_elements stored in _pending_content_elements
        - Must call restore_content_elements() after loading to create children
        - Necessary because element creation requires factory callback
        """
        self._read_common_layout(layout_props)

        self.slider_layout_props: dict = layout_props.get("slider_layout_props", {})

        self.exterior_padding = layout_props.get("exterior_padding", self.exterior_padding)
        self.interior_padding = layout_props.get("interior_padding", self.interior_padding)

        background_color_data = layout_props.get("background_color", [self.background_color[0], self.background_color[1], self.background_color[2], self.background_color[3]])
        self.background_color = (background_color_data[0], background_color_data[1], background_color_data[2], background_color_data[3])
        
        content_background_color_data = layout_props.get("content_background_color", [self.content_background_color[0], self.content_background_color[1], self.content_background_color[2], self.content_background_color[3]])
        self.content_background_color = (content_background_color_data[0], content_background_color_data[1], content_background_color_data[2], content_background_color_data[3])
                
        self.slider_side = layout_props.get("slider_side", self.slider_side)
        self.slider_handle_inset = layout_props.get("slider_handle_inset", self.slider_handle_inset)
        self.content_width_percentage = layout_props.get("content_width_percentage", self.content_width_percentage)
        
        # Store pending content elements for deferred loading
        # (elements must be created separately before being added)
        if "content_elements" in layout_props:
            self._pending_content_elements = layout_props["content_elements"]

        #recalculate dependent properties
        self.calculate_dependent_properties()
        self.create_surfaces()
    
    def restore_content_elements(self, element_factory_callback) -> None:
        """
        Create and add child elements from pending layout data.
        
        Args:
            element_factory_callback: Factory function with signature:
                (layout_props: dict, game_manager) -> UIElement
        
        Must be called after read_layout() to complete deserialization.
        Factory pattern allows polymorphic element creation without circular imports.
        """
        if hasattr(self, '_pending_content_elements'):
            for element_layout in self._pending_content_elements:
                # Create element using factory
                element = element_factory_callback(element_layout, self.game_manager)
                if element:
                    self.add_element(element)
            # Clear pending list
            delattr(self, '_pending_content_elements')

    def get_layout(self) -> dict:
        """Serialize scrollable area and all child elements to config dict."""
        layout = self._get_common_layout()
        layout.update({
            "_type": "ScrollableArea",
            "slider_layout_props": self.slider.get_layout(),
            "exterior_padding": self.exterior_padding,
            "interior_padding": self.interior_padding,
            "viewable_content_height": self.viewable_content_height,
            "viewable_content_width": self.viewable_content_width,
            "background_color": [self.background_color[0], self.background_color[1], self.background_color[2], self.background_color[3]],
            "content_background_color": [self.content_background_color[0], self.content_background_color[1], self.content_background_color[2], self.content_background_color[3]],
            "slider_side": self.slider_side,
            "slider_handle_inset": self.slider_handle_inset,
            "content_width_percentage": self.content_width_percentage,
            "shown": self.shown
        })
        
        # Serialize content_elements (child UI elements)
        if self.content_elements:
            content_element_layouts = []
            for element in self.content_elements:
                element_layout = element.get_layout()
                # Type should already be in layout from element's get_layout()
                content_element_layouts.append(element_layout)
            layout["content_elements"] = content_element_layouts
        
        return layout
    
    def print_info(self) -> None:
        """Print scrollable area properties and slider info for debugging."""
        self.print_common_info()
        print(f"  Exterior Padding: {self.exterior_padding}")
        print(f"  Interior Padding: {self.interior_padding}")
        print(f"  Viewable Content Size: {self.viewable_content_width}x{self.viewable_content_height}")
        print(f"  Max Scroll: {self.max_scroll}")
        print(f"  Content Scroll: {self.content_scroll}")
        print(f"  Slider Side: {self.slider_side}")
        print(f"  Slider Info:")
        self.slider.print_info()

        