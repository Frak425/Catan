import pygame

from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

class Slider:
    def __init__(self, name: str, wrapper_rect: pygame.Rect, rect: pygame.Rect, min_value: int, max_value: int, initial_value: int | float, bar_color: tuple[int, int, int], handle_color: tuple[int, int, int], handle_radius: int, game_manager: "GameManager",  bar_image: pygame.Surface | None, direction: str = "horizontal", handle_shape: str = "circle", handle_length: int = 0, callback: Optional[Callable] = None) -> None:
        self.name = name
        self.game_manager = game_manager

        self.rect = rect
        self.wrapper_rect = wrapper_rect
        self.direction = direction
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.bar_color = bar_color
        self.bar_image = bar_image
        self.handle_color = handle_color
        self.handle_radius = handle_radius
        self.handle_length = handle_length
        self.handle_shape = handle_shape
        self.slider_position = self.calculate_slider_position(self.value)

        #store the coordinates of where the mouse clicked on the slider to compare to the slider. e.g you have to click on the circle
        self.click_x = 0
        self.click_y = 0

        #create the drawing surface, cleared every frame
        self.draw_surface = pygame.Surface((self.wrapper_rect.width, self.wrapper_rect.height), pygame.SRCALPHA)
        self.draw_surface.fill((0, 0, 0, 0))  # Transparent background

        self.create_surfaces(self.direction, self.handle_shape)
        # optional callback triggered on slider click/interaction
        self.callback = callback

    def create_surfaces(self, direction: str, handle_shape: str):
        self.bar_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.bar_surface.fill((0, 0, 0, 0))
        if direction == "horizontal":
            pygame.draw.rect(self.bar_surface, self.bar_color, (self.rect.height / 2, 0, self.rect.width - self.rect.height, self.rect.height))  # Draw the bar
            pygame.draw.circle(self.bar_surface, self.bar_color, (self.rect.height / 2, self.rect.height / 2), self.rect.height / 2)  # Draw the slider circle
            pygame.draw.circle(self.bar_surface, self.bar_color, (self.rect.width - self.rect.height / 2, self.rect.height / 2), self.rect.height / 2)  # Draw the slider circle
            # Create the handle surface
            
            if handle_shape == "stadium":
                self.handle_surface = pygame.Surface((self.rect.height, self.rect.height), pygame.SRCALPHA)
                self.handle_surface.fill((0, 0, 0, 0))
                pygame.draw.rect(self.handle_surface, self.handle_color, (self.handle_radius, 0, self.rect.height - 2 * self.handle_radius, self.rect.height))
                pygame.draw.circle(self.handle_surface, self.handle_color, (self.handle_radius, self.rect.height / 2), self.handle_radius)
                pygame.draw.circle(self.handle_surface, self.handle_color, (self.rect.height - self.handle_radius, self.rect.height / 2), self.handle_radius)
        else:
            pygame.draw.rect(self.bar_surface, self.bar_color, (0, self.rect.width / 2, self.rect.width, self.rect.height - self.rect.width))  # Draw the bar
            pygame.draw.circle(self.bar_surface, self.bar_color, (self.rect.width / 2, self.rect.width / 2), self.rect.width / 2)  # Draw the slider circle
            pygame.draw.circle(self.bar_surface, self.bar_color, (self.rect.width / 2, self.rect.height - self.rect.width / 2), self.rect.width / 2)  # Draw the slider circle

            if handle_shape == "stadium":
                self.handle_surface = pygame.Surface((self.rect.width, self.rect.width), pygame.SRCALPHA)
                self.handle_surface.fill((0, 0, 0, 0))
                pygame.draw.rect(self.handle_surface, self.handle_color, (0, self.handle_radius, self.rect.width, self.rect.width - 2 * self.handle_radius))
                pygame.draw.circle(self.handle_surface, self.handle_color, (self.rect.width / 2, self.handle_radius), self.handle_radius)
                pygame.draw.circle(self.handle_surface, self.handle_color, (self.rect.width / 2, self.rect.width - self.handle_radius), self.handle_radius)


        if handle_shape == "circle":
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
        if self.direction == "horizontal":
            relative_position = (value - self.min_value) / (self.max_value - self.min_value)
            slider_position = relative_position * (self.rect.width - self.rect.height)
            return int(slider_position)
        else:
            relative_position = (value - self.min_value) / (self.max_value - self.min_value)
            slider_position = relative_position * (self.rect.height - self.rect.width)
            return int(slider_position)

    def calculate_value(self) -> int:
        # Calculate the value based on the slider position
        if self.direction == "horizontal":
            relative_position = self.slider_position / (self.rect.width - self.rect.height)
            value = int(self.min_value + relative_position * (self.max_value - self.min_value))
        else:
            relative_position = self.slider_position / (self.rect.height - self.rect.width)
            value = int(self.min_value + relative_position * (self.max_value - self.min_value))
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

    def draw(self, surface: pygame.Surface):
        # Redraw the bar and slider surfaces
        self.draw_surface.fill((0, 0, 0, 0))  # Clear the drawing surface
        centered_x = (self.wrapper_rect.width - self.rect.width) / 2
        centered_y = (self.wrapper_rect.height - self.rect.height) / 2
        self.draw_surface.blit(self.bar_surface, (centered_x, centered_y))  # Draw the bar surface centered in the wrapper
        self.draw_surface.blit(self.handle_surface, (centered_x + self.slider_position, centered_y))  # Draw the slider surface at the correct position

        # Draw the bar and slider on the main surface
        surface.blit(self.draw_surface, self.wrapper_rect.topleft)
