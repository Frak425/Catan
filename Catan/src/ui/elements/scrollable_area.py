import pygame
from src.ui.elements.slider import Slider
from src.ui.ui_element import UIElement

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

class ScrollableArea(UIElement):
    def __init__(self, layout_props: dict, game_manager: GameManager, content_surface: pygame.Surface) -> None:
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

    def add_element(self, element: UIElement) -> None:
        """Add a UI element to the scrollable content."""
        self.add_child(element)  # Use parent method for hierarchy
        self.content_elements.append(element)
        self._recalculate_content_height()

    def remove_element(self, element: UIElement) -> None:
        """Remove a UI element from the scrollable content."""
        if element in self.content_elements:
            self.remove_child(element)  # Use parent method for hierarchy
            self.content_elements.remove(element)
            self._recalculate_content_height()

    def _recalculate_content_height(self) -> None:
        """Calculate total content height based on child elements."""
        if self.content_elements:
            max_bottom = max(elem.rect.y + elem.rect.height for elem in self.content_elements)
            self.content_height = max_bottom
        elif self.content_surface:
            self.content_height = self.content_surface.get_height()
        else:
            self.content_height = 0
        
        self.max_scroll = max(0, self.content_height - self.viewable_content_height)

    def _get_content_rect(self) -> pygame.Rect:
        """Get the rect for the content area (where child elements live)."""
        return pygame.Rect(
            self.rect.x + self.exterior_padding,
            self.rect.y + self.exterior_padding,
            self.viewable_content_width,
            self.viewable_content_height
        )
    
    def get_absolute_content_rect(self) -> pygame.Rect:
        """Get the visible content area in screen coordinates."""
        abs_rect = super().get_absolute_rect()  # Get actual screen position
        return pygame.Rect(
            abs_rect.x + self.exterior_padding,
            abs_rect.y + self.exterior_padding,
            self.viewable_content_width,
            self.viewable_content_height
        )
    
    def get_clip_rect(self) -> pygame.Rect:
        """Content area should clip its children."""
        return self.get_absolute_content_rect()
    
    def get_absolute_rect(self) -> pygame.Rect:
        """Override to account for scroll offset for children positioning."""
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

    def _handle_own_event(self, event: pygame.event.Event) -> bool:
        """Handle scrolling events (mousewheel, slider interaction)."""
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

    def draw(self, surface: pygame.Surface):
        if not self.shown:
            return
        
        # Get actual screen position (not offset by scroll)
        actual_rect = super().get_absolute_rect()
        
        # Draw background
        surface.blit(self.background_surface, (actual_rect.x, actual_rect.y))

        # Get content area for clipping
        content_abs_rect = self.get_absolute_content_rect()
        
        # Create a subsurface for clipping content
        try:
            content_area = surface.subsurface(content_abs_rect)
            
            # Draw content surface if present
            if self.content_surface:
                content_area.blit(
                    self.content_surface, 
                    (0, -self.content_scroll)
                )
            
            # Draw child elements with clipping
            # Children use get_absolute_rect which includes scroll offset
            for element in self.content_elements:
                if element.shown:
                    # Check if element is visible in viewport
                    elem_abs_rect = element.get_absolute_rect()
                    if (elem_abs_rect.y + elem_abs_rect.height > content_abs_rect.y and 
                        elem_abs_rect.y < content_abs_rect.y + content_abs_rect.height):
                        element.draw(content_area)
        except ValueError:
            # Clip rect is outside surface bounds
            pass
        
        # Draw slider on top (outside content area)
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

    def create_surfaces(self):
        self.create_background_surface()
        self.create_slider()

    def create_background_surface(self):
        self.background_surface = pygame.Surface((self.rect.width, self.rect.height))
        if self.background_image:
            self.background_surface.blit(self.background_image, (0, 0))
        else:
            self.background_surface.fill(self.background_color)

    def create_slider(self):
        self.slider = Slider(
            self.slider_layout_props,
            0,  # initial_value
            self.game_manager,
            bar_image=self.slider_image,
            handle_image=self.slider_handle_image,
            callback=self.set_content_scroll
        )

    def calculate_dependent_properties(self):
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

    #called by slider to update content scroll, the area of the content surface to draw
    def set_content_scroll(self) -> None:
        #takes slider value (0 to 1) and sets content surface scroll accordingly
        self.content_scroll = self.slider.value * self.max_scroll
        self._invalidate_absolute_rect()  # Children positions changed

    #called on mouse drag
    def update_scroll(self, x: int, y: int) -> None:
        # Adjust coordinates to be relative to the scrollable area
        relative_x = x - self.rect.x
        relative_y = y - self.rect.y
        self.slider.update_location(relative_x, relative_y)

    def read_layout(self, layout_props: dict) -> None:
        self._read_common_layout(layout_props)

        self.slider_layout_props: dict = layout_props.get("slider_layout_props", {})

        self.exterior_padding = layout_props.get("exterior_padding", self.exterior_padding)
        self.interior_padding = layout_props.get("interior_padding", self.interior_padding)

        background_color_data = layout_props.get("background_color", [self.background_color[0], self.background_color[1], self.background_color[2], self.background_color[3]])
        self.background_color = (background_color_data[0], background_color_data[1], background_color_data[2], background_color_data[3])
        
        content_background_color_data = layout_props.get("content_background_color", [self.content_background_color[0], self.content_background_color[1], self.content_background_color[2], self.content_background_color[3]])
        self.content_background_color = (content_background_color_data[0], content_background_color_data[1], content_background_color_data[2], content_background_color_data[3])
                
        self.slider_side = layout_props.get("slider_side", self.slider_side)

        self.content_width_percentage = layout_props.get("content_width_percentage", self.content_width_percentage)
        
        # Store pending content elements for deferred loading
        # (elements must be created separately before being added)
        if "content_elements" in layout_props:
            self._pending_content_elements = layout_props["content_elements"]

        #recalculate dependent properties
        self.calculate_dependent_properties()
        self.create_surfaces()
    
    def restore_content_elements(self, element_factory_callback) -> None:
        """Restore content elements from layout after loading.
        
        Args:
            element_factory_callback: Function that creates a UI element from layout dict
                                     Should have signature: (layout_props: dict, game_manager) -> UIElement
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
            "content_width_percentage": self.content_width_percentage
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
        self.print_common_info()
        print(f"  Exterior Padding: {self.exterior_padding}")
        print(f"  Interior Padding: {self.interior_padding}")
        print(f"  Viewable Content Size: {self.viewable_content_width}x{self.viewable_content_height}")
        print(f"  Max Scroll: {self.max_scroll}")
        print(f"  Content Scroll: {self.content_scroll}")
        print(f"  Slider Side: {self.slider_side}")
        print(f"  Slider Info:")
        self.slider.print_info()

        