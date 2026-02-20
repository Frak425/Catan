import pygame

from typing import TYPE_CHECKING, Callable, Optional
from src.ui.ui_element import UIElement

if TYPE_CHECKING:
    from src.managers.game.game_manager import GameManager



class Button(UIElement):
    """
    Interactive button element with text, visual states, and click handling.
    
    Features:
    - Text rendering with alignment (left/center/right)
    - Visual states: normal, hover, disabled, active
    - Optional background image
    - Configurable colors, padding, and border radius
    - Callback execution on click
    
    Visual States:
    - Normal: Default color
    - Hover: 20% lighter when mouse over
    - Disabled: 50% darker, no interaction
    - Active: Shows guiding lines (dev mode selection)
    """

    text_color: tuple[int, int, int]

    def __init__(self, layout_props: dict, font: pygame.font.Font, game_manager: "GameManager", background_image: pygame.Surface | None = None, callback: Optional[Callable] = None, shown: bool = True) -> None:
        """
        Initialize button with text, colors, and visual properties.
        
        Args:
            layout_props: Configuration from layout.json
            font: Pygame font for text rendering
            game_manager: Central game state manager
            background_image: Optional background (overrides color fill)
            callback: Function called on click
            shown: Initial visibility
        
            NOTE: Update as needed when adding new properties.
        Properties:
        - text: Button label
        - color: Background color (r, g, b)
        - text_color: Text color (r, g, b)
        - text_align: "left", "center", or "right"
        - padding: Pixels between text and button edge
        - disabled: If True, button is non-interactive and darkened
        - border_radius: Corner rounding (not yet implemented in draw)
        """
        # Initialize element-specific defaults
        self.text = ""
        self.color = (0, 0, 0)
        self.padding = 5
        self.text_color = (0, 0, 0)
        self.text_align = "center"
        self.font = font
        self.disabled = False

        self.border_radius = -1
        self.border_top_right_radius = -1
        self.border_top_left_radius = -1
        self.border_bottom_right_radius = -1
        self.border_bottom_left_radius = -1
        
        # Call parent constructor
        super().__init__(layout_props, game_manager, callback, shown)
        
        self.game_font = font
        self.hovering = False
        self.selected = False
        self.background_image = background_image

        self.text_surface = self.game_font.render(self.text, False, self.text_color)
        self.text_rect = self.text_surface.get_rect()
        
        if self.background_image:
            self.surface = self.background_image
        else:
            self.surface = pygame.Surface((self.text_rect.width + 2 * self.padding, self.text_rect.height + 2 * self.padding))
            self.surface.fill(self.color)

        self.set_text_align(self.text_align)

        # read layout after setting defaults
        self.read_layout(layout_props)

    ## --- TEXT MANAGEMENT --- ##

    def update_text(self, new_text: str) -> None:
        """Update button text and regenerate text surface."""
        self.text = new_text
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect()
        self.set_text_align(self.text_align)

    def update_text_color(self, new_color: tuple[int, int, int]) -> None:
        """Update text color and regenerate text surface."""
        self.text_color = new_color
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect()
        self.set_text_align(self.text_align)

    def set_text_align(self, text_align: str) -> None:
        """Position text within button based on alignment (left/center/right)."""
        if text_align == "center":
            self.text_rect.center = self.surface.get_rect().center
        elif text_align == "left":
            self.text_rect.midleft = (self.padding, self.surface.get_rect().centery)
        elif text_align == "right":
            self.text_rect.midright = (self.surface.get_rect().width - self.padding, self.surface.get_rect().centery)

    ## --- EVENT HANDLING --- ##

    def _handle_own_event(self, event: pygame.event.Event) -> bool:
        """
        Handle button-specific events (clicks, hover).
        
        Tracks hover state for visual feedback and triggers callback on click.
        Respects disabled state. Returns True if click consumed.
        """
        if self.disabled or not self.shown:
            return False
        
        abs_rect = self.get_absolute_rect()
        mouse_pos = pygame.mouse.get_pos()
        
        # Update hover state
        is_hovering = abs_rect.collidepoint(mouse_pos)
        if is_hovering != self.hovering:
            self.hovering = is_hovering
        
        # Handle click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if abs_rect.collidepoint(event.pos):
                self.trigger()
                return True
        
        return False

    ## --- RENDERING --- ##

    #TODO: absract all draw functions into parent class, leaving room for custom functionality
    def draw(self, surface: pygame.Surface, time: int) -> None:
        """
        Draw button with text and visual state effects.
        
        Visual Modifications:
        - Disabled: Colors darkened to 50%
        - Hover: Background lightened to 120%
        - Active: Shows guiding lines (dev mode)
        
        Uses absolute coordinates for positioning (accounts for parent offset).
        """
        if not self.shown:
            return
        
        self.update()
        # Get absolute position for drawing
        abs_rect = self.get_absolute_rect()
        
        # Apply visual state modifications
        draw_color = self.color
        draw_text_color = self.text_color
        
        if self.disabled:
            # Darken disabled buttons
            draw_color = tuple(int(c * 0.5) for c in self.color)
            draw_text_color = tuple(int(c * 0.5) for c in self.text_color)
        elif self.hovering:
            # Lighten on hover
            draw_color = tuple(min(255, int(c * 1.2)) for c in self.color)
        
        # Draw using absolute rect
        pygame.draw.rect(surface, draw_color, abs_rect, 0, self.border_radius, self.border_top_left_radius, self.border_top_right_radius, self.border_bottom_left_radius, self.border_bottom_right_radius)
        text = self.game_font.render(self.text, False, draw_text_color)
        
        # Calculate text position based on absolute rect
        text_rect = text.get_rect()
        if self.text_align == "center":
            text_rect.center = abs_rect.center
        elif self.text_align == "left":
            text_rect.midleft = (abs_rect.left + self.padding, abs_rect.centery)
        elif self.text_align == "right":
            text_rect.midright = (abs_rect.right - self.padding, abs_rect.centery)
        
        surface.blit(text, text_rect)

        if self.is_active:
            self.draw_guiding_lines(surface)

    def get_text_rect(self, text_surface: pygame.Surface) -> pygame.Rect:
        """Calculate text position based on alignment. Returns rect in relative coordinates."""
        text_rect = text_surface.get_rect()
        if self.text_align == "center":
            text_rect.center = self.rect.center
        elif self.text_align == "left":
            text_rect.midleft = (self.rect.left + 5, self.rect.centery)
        elif self.text_align == "right":
            text_rect.midright = (self.rect.right - 5, self.rect.centery)
        return text_rect

    ## --- SERIALIZATION --- ##

    def read_layout(self, layout: dict) -> None:
        """
        Load button properties from config dict.
        
        Properties: color, text, text_color, padding, text_align
        See layout.json for schema reference.
        """
        # Schema reference: See [layout.json](./config/layout.json#L23-L41)
        self._read_common_layout(layout)
        
        color_data = layout.get("color", [self.color[0], self.color[1], self.color[2]])
        self.color = (color_data[0], color_data[1], color_data[2])
        self.text = layout.get("text", self.text)
        text_color_data = layout.get("text_color", [self.text_color[0], self.text_color[1], self.text_color[2]])
        self.text_color = (text_color_data[0], text_color_data[1], text_color_data[2])
        self.padding = layout.get("padding", self.padding)
        self.text_align = layout.get("text_align", self.text_align)
        self.disabled = layout.get("disabled", self.disabled)
        self.border_radius = layout.get("border_radius", self.border_radius)
        self.border_top_right_radius = layout.get("border_top_right_radius", self.border_top_right_radius)
        self.border_top_left_radius = layout.get("border_top_left_radius", self.border_top_left_radius)
        self.border_bottom_right_radius = layout.get("border_bottom_right_radius", self.border_bottom_right_radius)
        self.border_bottom_left_radius = layout.get("border_bottom_left_radius", self.border_bottom_left_radius)

    def get_layout(self) -> dict:
        """
        Serialize button properties to config dict.
        
        Includes reverse callback lookup to save callback name (if registered).
        Note: Nested loop for callback lookup - could be optimized with reverse registry.
        """
        layout = self._get_common_layout()
        layout.update({
            "_type": "Button",
            "color": [self.color[0], self.color[1], self.color[2]],
            "text_align": self.text_align,
            "text": self.text,
            "shown": self.shown,
            "padding": self.padding,
            "disabled": self.disabled,
            "text_color": [self.text_color[0], self.text_color[1], self.text_color[2]],
            "border_radius": self.border_radius,
            "border_top_right_radius": self.border_top_right_radius,
            "border_top_left_radius": self.border_top_left_radius,
            "border_bottom_right_radius": self.border_bottom_right_radius,
            "border_bottom_left_radius": self.border_bottom_left_radius
        })
        
        # Save callback name if it exists - do reverse lookup in callback registry
        if hasattr(self, 'callback') and self.callback:
            callback_name = None
            for name, func in self.game_manager.input_manager.ui_factory.callback_registry.items():
                if func == self.callback:
                    callback_name = name
                    break
            
                if callback_name:
                    layout["callback"] = callback_name
                    if func == self.callback:
                        callback_name = name
                        break
            
            if callback_name:
                layout["callback"] = callback_name
        
        return layout
    
    def print_info(self) -> None:
        """Print all button properties for debugging (used by dev mode print_info command)."""

        self.print_common_info()
        print(f"Button: {self.name}")
        print(f"Text: {self.text}")
        print(f"Color: {self.color}")
        print(f"Text Color: {self.text_color}")
        print(f"Padding: {self.padding}")
        print(f"Text Align: {self.text_align}")
        print(f"Rect: {self.rect}")
        print(f"border_radius: {self.border_radius}")
        print(f"border_top_right_radius: {self.border_top_right_radius}")
        print(f"border_top_left_radius: {self.border_top_left_radius}")
        print(f"border_bottom_right_radius: {self.border_bottom_right_radius}")
        print(f"border_bottom_left_radius: {self.border_bottom_left_radius}")
        print(f"Shown: {self.shown}")
        print(f"")