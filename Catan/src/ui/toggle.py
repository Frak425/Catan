import pygame
import pytweening as tween

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

class Toggle:
    def __init__(self, layout_props: dict, time: int, game_manager: GameManager, on: bool = False, callback=None) -> None:
        self.game_manager = game_manager

        # Initialize defaults so read_layout() can fall back reliably
        self.name = ""
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.guiding_lines = False
        self.height = 50
        self.radius = self.height / 2
        self.center_width = 100
        self.fill_color = (0, 100, 0)
        self.toggle_color = (100, 0, 0)
        self.toggle_gap = 7
        self.toggle_radius = self.height / 2 - self.toggle_gap
        self.toggle_gap = 7
        self.time_to_flip = 0.25  # seconds
        self.guiding_line_color = (100, 100, 200)
        self.callback = callback
        self.is_active = False
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
        pygame.draw.circle(self.surface, self.fill_color, (self.radius, self.height // 2), self.radius)
        pygame.draw.circle(self.surface, self.fill_color, (self.center_width + self.radius, self.height // 2), self.radius)
        pygame.draw.rect(self.surface, self.fill_color, (self.height / 2, 0, self.center_width, self.height))
        
        if self.guiding_lines:
            pygame.draw.line(self.surface, (100, 100, 200), (0, self.height / 2), (self.height + self. center_width, self.height / 2), 1)
            pygame.draw.line(self.surface, (100, 100, 200), ((self.height + self.center_width) / 2, 0), ((self.height + self.center_width) / 2, self.height), 1)

        #Create the toggle circle
        self.toggle_circle = pygame.Surface((self.height - self.toggle_gap * 2, self.height - self.toggle_gap * 2), pygame.SRCALPHA)
        self.toggle_circle.fill((0, 0, 0, 0))  # Transparent background
        pygame.draw.circle(self.toggle_circle, self.toggle_color, self.toggle_circle.get_rect().center, self.toggle_radius)
    
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
    
    def trigger(self):
        if self.callback:
            self.callback()

    def draw(self, surface: pygame.Surface, time: int):
        # Draw the toggle on the background and then the background to the surface 
        if self.animating:
            self.update(time)
            # Redraw the toggle background
            self.surface.fill((0, 0, 0, 0))  # Transparent background
            pygame.draw.circle(self.surface, self.fill_color, (self.radius, self.height // 2), self.radius)
            pygame.draw.circle(self.surface, self.fill_color, (self.center_width + self.height - self.radius, self.height // 2), self.radius)
            pygame.draw.rect(self.surface, self.fill_color, (self.height / 2, 0, self.center_width, self.height))
        if self.guiding_lines:
            pygame.draw.line(self.surface, (100, 100, 200), (0, self.height / 2), (self.height + self. center_width, self.height / 2), 1)
            pygame.draw.line(self.surface, (100, 100, 200), ((self.height + self.center_width) / 2, 0), ((self.height + self.center_width) / 2, self.height), 1)
        self.surface.blit(self.toggle_circle, (self.toggle_center_location[0] - self.toggle_circle.get_size()[0] / 2, self.toggle_center_location[1] - self.toggle_circle.get_size()[1] / 2))
        surface.blit(self.surface, self.rect.topleft)

        if self.is_active:
            self.draw_guiding_lines(surface)

    def read_layout(self, layout_props: dict):
        # Schema reference: See [layout.json](./config/layout.json#L442-L465)
        
        self.name = layout_props.get("name", self.name)
        rect_data = layout_props.get("rect", [self.rect.x, self.rect.y, self.rect.width, self.rect.height])
        self.rect = pygame.Rect(rect_data[0], rect_data[1], rect_data[2], rect_data[3])
        self.guiding_lines = layout_props.get("guiding_lines", self.guiding_lines)
        self.height = layout_props.get("height", self.height)
        self.center_width = layout_props.get("center_width", self.center_width)
        fill_color_data = layout_props.get("fill_color", [self.fill_color[0], self.fill_color[1], self.fill_color[2]])
        self.fill_color = (fill_color_data[0], fill_color_data[1], fill_color_data[2])
        toggle_color_data = layout_props.get("toggle_color", [self.toggle_color[0], self.toggle_color[1], self.toggle_color[2]])
        self.toggle_color = (toggle_color_data[0], toggle_color_data[1], toggle_color_data[2]) 
        self.toggle_gap = layout_props.get("toggle_gap", self.toggle_gap)
        self.time_to_flip = layout_props.get("time_to_flip", self.time_to_flip)

        # Recalculate dependent properties
        self.radius = self.height / 2
        self.toggle_radius = self.height / 2 - self.toggle_gap
        
    def get_layout(self) -> dict:
        return {
            "name": self.name,
            "rect": [self.rect.x, self.rect.y, self.rect.width, self.rect.height],
            "guiding_lines": self.guiding_lines,
            "height": self.height,
            "center_width": self.center_width,
            "fill_color": [self.fill_color[0], self.fill_color[1], self.fill_color[2]],
            "toggle_color": [self.toggle_color[0], self.toggle_color[1], self.toggle_color[2]],
            "toggle_gap": self.toggle_gap,
            "time_to_flip": self.time_to_flip,
            "guiding_line_color": [self.guiding_line_color[0], self.guiding_line_color[1], self.guiding_line_color[2]]
        }
    
    #TODO: implement settings read/write
    def read_settings(self, settings: dict) -> None:
        pass

    def get_settings(self) -> dict:
        return {}
    
    def dev_mode_drag(self, x: int, y: int) -> None:
        self.rect.x += x
        self.rect.y += y

    def draw_guiding_lines(self, surface: pygame.Surface) -> None:
        if self.game_manager.dev_mode:
            pygame.draw.line(surface, self.guiding_line_color, (self.rect.x, self.rect.y), (self.rect.x + self.rect.width, self.rect.y), 1)
            pygame.draw.line(surface, self.guiding_line_color, (self.rect.x, self.rect.y), (self.rect.x, self.rect.y + self.rect.height), 1)
            pygame.draw.line(surface, self.guiding_line_color, (self.rect.x + self.rect.width, self.rect.y), (self.rect.x + self.rect.width, self.rect.y + self.rect.height), 1)
            pygame.draw.line(surface, self.guiding_line_color, (self.rect.x, self.rect.y + self.rect.height), (self.rect.x + self.rect.width, self.rect.y + self.rect.height), 1)
    