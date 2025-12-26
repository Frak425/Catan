import pygame
import pytweening as tween

from typing import TYPE_CHECKING
from src.ui.ui_element import UIElement

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

class Toggle(UIElement):
    def __init__(self, layout_props: dict, time: int, game_manager: GameManager, on: bool = False, callback=None, shown: bool = True) -> None:
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
    
    def set_animating(self, time: int):
        if not self.animating:
            self.animating = True
            self.time = time
            self.start_time = time
            self.end_time = time + int(self.time_to_flip * 1000)
    
    def update(self, new_time: int):
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

    def draw(self, surface: pygame.Surface, time: int):
        # Draw the toggle on the background and then the background to the surface 
        if self.animating:
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
        surface.blit(self.surface, self.rect.topleft)

        if self.is_active:
            self.draw_guiding_lines(surface)

    def read_layout(self, layout_props: dict):
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
        layout = self._get_common_layout()
        layout.update({
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
        self.print_common_info()
        print(f"Toggle: {self.name}")
        print(f"On: {self.on}")
        print(f"Guiding Lines: {self.guiding_lines}")
        print(f"Height: {self.height}")
        print(f"Center Width: {self.center_width}")
        print(f"Color: {self.color}")
        print(f"Handle Color: {self.handle_color}")
        print(f"Toggle Gap: {self.toggle_gap}")
        print(f"Time to Flip: {self.time_to_flip}")
        print(f"Rect: {self.rect}")