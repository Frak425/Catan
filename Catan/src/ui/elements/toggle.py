import pygame
import pytweening as tween

from typing import TYPE_CHECKING
from src.ui.ui_element import UIElement

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

class Toggle(UIElement):
    """
    Animated on/off toggle switch with smooth easing transition.
    
    Features:
    - Stadium-shaped track (circles + rectangle)
    - Circular handle that slides between positions
    - Smooth animation with easeInOutCubic easing (pytweening)
    - Click anywhere on toggle to flip state
    - Configurable colors, size, and animation duration
    
    Visual Structure:
    - Track: Two circles (radius = height/2) connected by rectangle (width = center_width)
    - Handle: Circle (radius = height/2 - toggle_gap) that slides on track
    - Total width: center_width + height
    
    Animation:
    - Click triggers animation with start/end time tracking
    - Each frame updates handle position via pytweening.easeInOutCubic
    - State (on/off) only flips when animation completes
    - Progress calculated as (current_time - start_time) / duration
    
    Positions:
    - Off: Handle at (height/2, height/2) - left side
    - On: Handle at (center_width + height/2, height/2) - right side
    - Animating: Interpolated between positions
    """
    def __init__(self, layout_props: dict, time: int, game_manager: GameManager, on: bool = False, callback=None, shown: bool = True) -> None:
        """
        Initialize toggle with initial state and create surfaces.
        
        Args:
            layout_props: Configuration from layout.json
            time: Initial time in milliseconds (for animation tracking)
            game_manager: Central game state manager
            on: Initial state (False = off/left, True = on/right)
            callback: Function called when toggle is clicked
            shown: Initial visibility
        
        Properties:
        - height: Track height (determines radius)
        - center_width: Length of rectangle connecting circles
        - color: Track color (r, g, b)
        - handle_color: Handle circle color (r, g, b)
        - toggle_gap: Gap between track edge and handle (pixels)
        - time_to_flip: Animation duration in seconds (default: 0.25s)
        - guiding_lines: Debug lines showing center axes
        
        Surfaces:
        - surface: Track background (stadium shape)
        - toggle_circle: Handle circle (slides on track)
        """
        # Initialize element-specific defaults
        self.guiding_lines = False
        self.height = 50
        self.radius = self.height / 2
        self.center_width = 100
        self.color = (0, 100, 0)
        self.handle_color = (100, 0, 0)
        self.toggle_gap = 7
        self.handle_radius = self.height / 2 - self.toggle_gap
        self.time_to_flip = 0.25  # seconds
        
        # Call parent constructor
        super().__init__(layout_props, game_manager, callback, shown)
        
        # read layout and override default values
        self.read_layout(layout_props)
        
        #Animation properties
        self.start_time = time
        
        self.on = on
        self.animating = False
        if not self.on:
            self.toggle_center_location = (self.height // 2, self.height // 2) 
        else:
            self.toggle_center_location = (self.center_width + self.height // 2, self.height // 2)

        #Create the toggle's background surface
        self.surface = pygame.Surface((self.center_width + self.height, self.height), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))  # Transparent background
        #draw endpoints and center rectangle
        pygame.draw.circle(self.surface, self.color, (self.radius, self.height // 2), self.radius)
        pygame.draw.circle(self.surface, self.color, (self.center_width + self.radius, self.height // 2), self.radius)
        pygame.draw.rect(self.surface, self.color, (self.height / 2, 0, self.center_width, self.height))
        
        if self.guiding_lines:
            pygame.draw.line(self.surface, (100, 100, 200), (0, self.height / 2), (self.height + self. center_width, self.height / 2), 1)
            pygame.draw.line(self.surface, (100, 100, 200), ((self.height + self.center_width) / 2, 0), ((self.height + self.center_width) / 2, self.height), 1)

        #Create the toggle circle
        self.toggle_circle = pygame.Surface((self.height - self.toggle_gap * 2, self.height - self.toggle_gap * 2), pygame.SRCALPHA)
        self.toggle_circle.fill((0, 0, 0, 0))  # Transparent background
        pygame.draw.circle(self.toggle_circle, self.handle_color, self.toggle_circle.get_rect().center, self.handle_radius)
    
    ## --- EVENT HANDLING --- ##
    
    def _handle_own_event(self, event: pygame.event.Event) -> bool:
        """
        Handle toggle click to start animation and trigger callback.
        
        Click anywhere on toggle starts animation. Callback fires immediately,
        but state (on/off) only changes when animation completes.
        """
        if not self.shown:
            return False
        
        abs_rect = self.get_absolute_rect()
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle click to toggle
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if abs_rect.collidepoint(event.pos):
                # Get current time from game_manager
                current_time = pygame.time.get_ticks()
                self.set_animating(current_time)
                if self.callback:
                    self.trigger()
                return True
        
        return False
    
    ## --- ANIMATION --- ##
    
    def set_animating(self, time: int):
        """Start animation with timestamp (only if not already animating)."""
        if not self.animating:
            self.animating = True
            self.time = time
            self.start_time = time
            self.end_time = time + int(self.time_to_flip * 1000)
    
    def update(self, new_time: int):
        """
        Update handle position during animation using easing function.
        
        Algorithm:
        1. Check if animation complete (flip state and stop)
        2. Calculate progress: (current - start) / (end - start)
        3. Apply easeInOutCubic easing for smooth acceleration/deceleration
        4. Interpolate handle position based on eased progress
        
        Easing: pytweening.easeInOutCubic
        - Slow start (ease in)
        - Slow end (ease out)
        - Fast in middle
        
        Direction:
        - Off->On: Move right (height/2 to center_width + height/2)
        - On->Off: Move left (center_width + height/2 to height/2)
        """
        if self.animating:
            if new_time >= self.end_time:
                    self.animating = False
                    self.on = not self.on
                    return
            progress = (new_time - self.start_time) / (self.end_time - self.start_time)
            progress = tween.easeInOutCubic(progress)
            if not self.on:
                self.toggle_center_location = (self.height // 2 + int((self.center_width) * progress), self.height // 2)
            else:
                self.toggle_center_location = (self.center_width + self.height // 2 - int((self.center_width) * progress), self.height // 2)

    ## --- RENDERING --- ##

    def draw(self, surface: pygame.Surface, time: int | None = None):
        """
        Draw toggle track and handle, updating animation if active.
        
        Process:
        1. If animating: Update handle position and redraw track
        2. Blit handle circle at current toggle_center_location
        3. Blit composite to screen at absolute position
        
        Note: Track is redrawn each frame during animation (could be optimized
              to only redraw handle, but current approach is simpler).
        
        Args:
            surface: Target surface for drawing
            time: Current time in milliseconds (optional, for animation update)
        """
        if not self.shown:
            return
        
        # Get absolute position for drawing
        abs_rect = self.get_absolute_rect()
        
        # Draw the toggle on the background and then the background to the surface 
        if self.animating:
            if time is not None:
                self.update(time)
            # Redraw the toggle background
            self.surface.fill((0, 0, 0, 0))  # Transparent background
            pygame.draw.circle(self.surface, self.color, (self.radius, self.height // 2), self.radius)
            pygame.draw.circle(self.surface, self.color, (self.center_width + self.height - self.radius, self.height // 2), self.radius)
            pygame.draw.rect(self.surface, self.color, (self.height / 2, 0, self.center_width, self.height))
        if self.guiding_lines:
            pygame.draw.line(self.surface, (100, 100, 200), (0, self.height / 2), (self.height + self. center_width, self.height / 2), 1)
            pygame.draw.line(self.surface, (100, 100, 200), ((self.height + self.center_width) / 2, 0), ((self.height + self.center_width) / 2, self.height), 1)
        self.surface.blit(self.toggle_circle, (self.toggle_center_location[0] - self.toggle_circle.get_size()[0] / 2, self.toggle_center_location[1] - self.toggle_circle.get_size()[1] / 2))
        surface.blit(self.surface, abs_rect.topleft)

        if self.is_active:
            self.draw_guiding_lines(surface)

    ## --- SERIALIZATION --- ##

    def read_layout(self, layout_props: dict):
        """
        Load toggle properties from config dict and recalculate dependent values.
        
        Dependent properties (calculated from height and toggle_gap):
        - radius: height / 2
        - handle_radius: height / 2 - toggle_gap
        """
        # Schema reference: See [layout.json](./config/layout.json#L442-L465)
        self._read_common_layout(layout_props)
        
        self.guiding_lines = layout_props.get("guiding_lines", self.guiding_lines)
        self.height = layout_props.get("height", self.height)
        self.center_width = layout_props.get("center_width", self.center_width)
        color_data = layout_props.get("color", [self.color[0], self.color[1], self.color[2]])
        self.color = (color_data[0], color_data[1], color_data[2])
        toggle_color_data = layout_props.get("handle_color", [self.handle_color[0], self.handle_color[1], self.handle_color[2]])
        self.handle_color = (toggle_color_data[0], toggle_color_data[1], toggle_color_data[2]) 
        self.toggle_gap = layout_props.get("toggle_gap", self.toggle_gap)
        self.time_to_flip = layout_props.get("time_to_flip", self.time_to_flip)

        # Recalculate dependent properties
        self.radius = self.height / 2
        self.handle_radius = self.height / 2 - self.toggle_gap
        
    def get_layout(self) -> dict:
        """Serialize toggle properties including current state (on/off)."""
        layout = self._get_common_layout()
        layout.update({
            "_type": "Toggle",
            "on": self.on,
            "guiding_lines": self.guiding_lines,
            "height": self.height,
            "center_width": self.center_width,
            "color": [self.color[0], self.color[1], self.color[2]],
            "handle_color": [self.handle_color[0], self.handle_color[1], self.handle_color[2]],
            "toggle_gap": self.toggle_gap,
            "time_to_flip": self.time_to_flip
        })
        return layout
    
    def print_info(self) -> None:
        """Print all toggle properties and current state for debugging."""
        self.print_common_info()
        print(f"On: {self.on}")
        print(f"Guiding Lines: {self.guiding_lines}")
        print(f"Height: {self.height}")
        print(f"Center Width: {self.center_width}")
        print(f"Color: {self.color}")
        print(f"Handle Color: {self.handle_color}")
        print(f"Toggle Gap: {self.toggle_gap}")
        print(f"Time to Flip: {self.time_to_flip}")
        print(f"Rect: {self.rect}")