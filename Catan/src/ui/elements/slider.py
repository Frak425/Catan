import pygame

from typing import TYPE_CHECKING, Callable, Optional
from src.ui.ui_element import UIElement

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

class Slider(UIElement):
    def __init__(self, layout_props: dict, initial_value: int | float, game_manager: "GameManager",  bar_image: pygame.Surface | None = None, handle_image: pygame.Surface | None = None, callback: Optional[Callable] = None, shown: bool = True) -> None:
        # Initialize element-specific defaults
        self.min_value = 0
        self.max_value = 100
        self.color = (0, 100, 0)
        self.handle_color = (100, 0, 0)
        self.handle_radius = 10
        self.direction = "horizontal"  # or "vertical"
        self.handle_shape = "circle"  # or "rectangle" or "stadium"
        self.handle_length = 0  # used if handle_shape is rectangle
        
        # Call parent constructor
        super().__init__(layout_props, game_manager, callback, shown)

        # read layout and override default values
        self.read_layout(layout_props)

        self.value = initial_value
        self.bar_image = bar_image

        self.slider_position = self.calculate_slider_position(self.value)

        #store the coordinates of where the mouse clicked on the slider to compare to the slider. e.g you have to click on the circle
        self.click_x = 0
        self.click_y = 0

        #create the drawing surface, cleared every frame
        self.draw_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.draw_surface.fill((0, 0, 0, 0))  # Transparent background

        self.create_surfaces(self.direction, self.handle_shape)

    def create_surfaces(self, direction: str, handle_shape: str):
        self.bar_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.bar_surface.fill((0, 0, 0, 0))
        if direction == "horizontal":
            pygame.draw.rect(self.bar_surface, self.color, (self.rect.height / 2, 0, self.rect.width - self.rect.height, self.rect.height))  # Draw the bar
            pygame.draw.circle(self.bar_surface, self.color, (self.rect.height / 2, self.rect.height / 2), self.rect.height / 2)  # Draw the slider circle
            pygame.draw.circle(self.bar_surface, self.color, (self.rect.width - self.rect.height / 2, self.rect.height / 2), self.rect.height / 2)  # Draw the slider circle
            # Create the handle surface
            
            if handle_shape == "stadium":
                self.handle_surface = pygame.Surface((self.rect.height, self.rect.height), pygame.SRCALPHA)
                self.handle_surface.fill((0, 0, 0, 0))
                pygame.draw.rect(self.handle_surface, self.handle_color, (self.handle_radius, 0, self.rect.height - 2 * self.handle_radius, self.rect.height))
                pygame.draw.circle(self.handle_surface, self.handle_color, (self.handle_radius, self.rect.height / 2), self.handle_radius)
                pygame.draw.circle(self.handle_surface, self.handle_color, (self.rect.height - self.handle_radius, self.rect.height / 2), self.handle_radius)
        else:
            pygame.draw.rect(self.bar_surface, self.color, (0, self.rect.width / 2, self.rect.width, self.rect.height - self.rect.width))  # Draw the bar
            pygame.draw.circle(self.bar_surface, self.color, (self.rect.width / 2, self.rect.width / 2), self.rect.width / 2)  # Draw the slider circle
            pygame.draw.circle(self.bar_surface, self.color, (self.rect.width / 2, self.rect.height - self.rect.width / 2), self.rect.width / 2)  # Draw the slider circle

            if handle_shape == "stadium":
                self.handle_surface = pygame.Surface((self.rect.width, self.rect.width), pygame.SRCALPHA)
                self.handle_surface.fill((0, 0, 0, 0))
                pygame.draw.rect(self.handle_surface, self.handle_color, (0, self.handle_radius, self.rect.width, self.rect.width - 2 * self.handle_radius))
                pygame.draw.circle(self.handle_surface, self.handle_color, (self.rect.width / 2, self.handle_radius), self.handle_radius)
                pygame.draw.circle(self.handle_surface, self.handle_color, (self.rect.width / 2, self.rect.width - self.handle_radius), self.handle_radius)


        if handle_shape == "circle":
                # For vertical slider, use width as the dimension
                if direction == "vertical":
                    self.handle_surface = pygame.Surface((self.rect.width, self.rect.width), pygame.SRCALPHA)
                    self.handle_surface.fill((0, 0, 0, 0))
                    pygame.draw.circle(self.handle_surface, self.handle_color, (self.rect.width / 2, self.rect.width / 2), self.handle_radius)
                else:
                    self.handle_surface = pygame.Surface((self.rect.height, self.rect.height), pygame.SRCALPHA)
                    self.handle_surface.fill((0, 0, 0, 0))
                    pygame.draw.circle(self.handle_surface, self.handle_color, (self.rect.height / 2, self.rect.height / 2), self.handle_radius)
        elif handle_shape == "rectangle":
            self.handle_surface = pygame.Surface((self.handle_length, self.rect.height), pygame.SRCALPHA)
            self.handle_surface.fill((0, 0, 0, 0))
            pygame.draw.rect(self.handle_surface, self.handle_color, (0, 0, self.handle_length, self.rect.height))

    def calculate_slider_position(self, value: float | int) -> int:
        # Ensure the value is within the defined range
        if value < self.min_value:
            value = self.min_value
        elif value > self.max_value:
            value = self.max_value
        # Calculate the position based on the value
        denom = (self.max_value - self.min_value)
        if denom == 0:
            return 0
        if self.direction == "horizontal":
            relative_position = (value - self.min_value) / denom
            slider_position = relative_position * (self.rect.width - self.rect.height)
            return int(slider_position)
        else:
            relative_position = (value - self.min_value) / denom
            slider_position = relative_position * (self.rect.height - self.rect.width)
            return int(slider_position)

    def calculate_value(self) -> float:
        # Calculate the value based on the slider position
        denom_pixels = (self.rect.width - self.rect.height) if self.direction == "horizontal" else (self.rect.height - self.rect.width)
        if denom_pixels == 0:
            return float(self.min_value)
        relative_position = self.slider_position / denom_pixels
        value = self.min_value + relative_position * (self.max_value - self.min_value)
        # Ensure the value is within the defined range
        if value < self.min_value:
            value = self.min_value
        elif value > self.max_value:
            value = self.max_value
        return value

    def set_value(self, value: int):
        # Update the value and recalculate the slider position
        self.value = value
        self.slider_position = self.calculate_slider_position(value)

    def update_location(self, mouse_x: int, mouse_y):
        # Calculate the new slider position based on mouse x-coordinate
        if self.direction == "horizontal":
            self.slider_position = mouse_x - self.click_x - self.rect.x - self.handle_surface.get_width() / 2
            # Ensure the slider position is within the bar's bounds
            if self.slider_position < 0:
                self.slider_position = 0
            elif self.slider_position > self.rect.width - self.rect.height:
                self.slider_position = self.rect.width - self.rect.height

        else:
            self.slider_position = mouse_y - self.click_y - self.rect.y - self.handle_surface.get_height() / 2
            # Ensure the slider position is within the bar's bounds
            if self.slider_position < 0:
                self.slider_position = 0
            elif self.slider_position > self.rect.height - self.rect.width:
                self.slider_position = self.rect.height - self.rect.width

        self.value = self.calculate_value()
        if self.callback:
            self.callback()  # Call the callback function if provided

    def draw(self, surface: pygame.Surface):
        # Redraw the bar and slider surfaces
        self.draw_surface.fill((0, 0, 0, 0))  # Clear the drawing surface
        self.draw_surface.blit(self.bar_surface, (0, 0))  # Draw the bar surface
        # Position handle based on direction
        if self.direction == "horizontal":
            handle_pos = (self.slider_position, 0)
            self.draw_surface.blit(self.handle_surface, handle_pos)
        else:
            handle_pos = (0, self.slider_position)
            self.draw_surface.blit(self.handle_surface, handle_pos)

        # Draw the bar and slider on the main surface
        surface.blit(self.draw_surface, self.rect.topleft)

        if self.is_active:
            self.draw_guiding_lines(surface)

    def read_layout(self, layout_props: dict):
        # Schema ref: See [layout.json](./config/layout.json#L188-215)
        self._read_common_layout(layout_props)
        
        self.min_value: int = layout_props.get("min_value", self.min_value)
        self.max_value: int = layout_props.get("max_value", self.max_value)
        color_data = layout_props.get("color", [self.color[0], self.color[1], self.color[2]])
        self.color: tuple[int, int, int] = (color_data[0], color_data[1], color_data[2])
        handle_color_data = layout_props.get("handle_color", [self.handle_color[0], self.handle_color[1], self.handle_color[2]])
        self.handle_color: tuple[int, int, int] = (handle_color_data[0], handle_color_data[1], handle_color_data[2])
        self.handle_radius: int = layout_props.get("handle_radius", self.handle_radius)
        self.direction: str = layout_props.get("direction", self.direction)
        self.handle_shape: str = layout_props.get("handle_shape", self.handle_shape)
        self.handle_length: int = layout_props.get("handle_length", self.handle_length)

    def get_layout(self) -> dict:
        layout = self._get_common_layout()
        layout.update({
            "min_value": self.min_value,
            "max_value": self.max_value,
            "color": [self.color[0], self.color[1], self.color[2]],
            "handle_color": [self.handle_color[0], self.handle_color[1], self.handle_color[2]],
            "handle_radius": self.handle_radius,
            "direction": self.direction,
            "handle_shape": self.handle_shape,
            "handle_length": self.handle_length
        })
        return layout
    
    def print_info(self) -> None:
        self.print_common_info()
        print(f"Min Value: {self.min_value}")
        print(f"Max Value: {self.max_value}")
        print(f"Color: {self.color}")
        print(f"Handle Color: {self.handle_color}")
        print(f"Handle Radius: {self.handle_radius}")
        print(f"Direction: {self.direction}")
        print(f"Handle Shape: {self.handle_shape}")
        print(f"Handle Length: {self.handle_length}")