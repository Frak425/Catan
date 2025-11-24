import pygame

from Catan.src.managers.game_manager import GameManager

class Slider:
    def __init__(self, name: str, wrapper_rect: pygame.Rect, rect: pygame.Rect, min_value: int, max_value: int, initial_value: int, bar_color: tuple[int], slider_color: tuple[int], slider_radius: int, game_manager: GameManager) -> None:
        self.name = name
        self.game_manager = game_manager

        self.rect = rect
        self.wrapper_rect = wrapper_rect
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.bar_color = bar_color
        self.slider_color = slider_color
        self.slider_radius = slider_radius
        self.slider_position = self.calculate_slider_position(self.value)

        #store the coordinates of where the mouse clicked on the slider to compare to the slider. e.g you have to click on the circle
        self.click_x = 0
        self.click_y = 0

        #create the drawing surface, cleared every frame
        self.draw_surface = pygame.Surface((self.wrapper_rect.width, self.wrapper_rect.height), pygame.SRCALPHA)
        self.draw_surface.fill((0, 0, 0, 0))  # Transparent background

        # Create the bar surface
        self.bar_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.bar_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.bar_surface, self.bar_color, (self.rect.height / 2, 0, self.rect.width - self.rect.height, self.rect.height))  # Draw the bar
        pygame.draw.circle(self.bar_surface, self.bar_color, (self.rect.height / 2, self.rect.height / 2), self.rect.height / 2)  # Draw the slider circle
        pygame.draw.circle(self.bar_surface, self.bar_color, (self.rect.width - self.rect.height / 2, self.rect.height / 2), self.rect.height / 2)  # Draw the slider circle

        # Create the slider surface
        self.slider_surface = pygame.Surface((self.rect.height, self.rect.height), pygame.SRCALPHA)
        self.slider_surface.fill((0, 0, 0, 0))
        pygame.draw.circle(self.slider_surface, self.slider_color, (self.rect.height / 2, self.rect.height / 2), slider_radius)

    def calculate_slider_position(self, value: int) -> int:
        # Ensure the value is within the defined range
        if value < self.min_value:
            value = self.min_value
        elif value > self.max_value:
            value = self.max_value
        # Calculate the position based on the value
        relative_position = (value - self.min_value) / (self.max_value - self.min_value)
        slider_position = relative_position * (self.rect.width - self.rect.height)
        return int(slider_position)

    def calculate_value(self) -> int:
        # Calculate the value based on the slider position
        relative_position = self.slider_position / (self.rect.width - self.rect.height)
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
        self.slider_position = mouse_x - self.click_x - self.rect.x - self.slider_surface.get_width() / 2
        # Ensure the slider position is within the bar's bounds
        if self.slider_position < 0:
            self.slider_position = 0
        elif self.slider_position > self.rect.width - self.rect.height:
            self.slider_position = self.rect.width - self.rect.height

        self.value = self.calculate_value()

    def draw(self, surface: pygame.Surface):
        # Redraw the bar and slider surfaces
        self.draw_surface.fill((0, 0, 0, 0))  # Clear the drawing surface
        centered_x = (self.wrapper_rect.width - self.rect.width) / 2
        centered_y = (self.wrapper_rect.height - self.rect.height) / 2
        self.draw_surface.blit(self.bar_surface, (centered_x, centered_y))  # Draw the bar surface centered in the wrapper
        self.draw_surface.blit(self.slider_surface, (centered_x + self.slider_position, centered_y))  # Draw the slider surface at the correct position

        # Draw the bar and slider on the main surface
        surface.blit(self.draw_surface, self.wrapper_rect.topleft)
