import pygame

#TODO: Add click and drag / click functionality
class Slider:
    def __init__(self, wrapper_rect: pygame.Rect, bar_rect: pygame.Rect, min_value: int, max_value: int, initial_value: int, bar_color: tuple[int], slider_color: tuple[int], slider_radius: int) -> None:
        self.bar_rect = bar_rect
        self.wrapper_rect = wrapper_rect
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.bar_color = bar_color
        self.slider_color = slider_color
        self.slider_radius = slider_radius
        self.slider_position = self.calculate_slider_position(self.value)

        # Create the bar surface
        self.bar_surface = pygame.Surface((self.bar_rect.width, self.bar_rect.height), pygame.SRCALPHA)
        self.bar_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.bar_surface, self.bar_color, (self.bar_rect.height / 2, 0, self.bar_rect.width - self.bar_rect.height, self.bar_rect.height))  # Draw the bar
        pygame.draw.circle(self.bar_surface, self.slider_color, (self.bar_rect.height / 2, self.bar_rect.height / 2), self.bar_rect.height / 2)  # Draw the slider circle
        pygame.draw.circle(self.bar_surface, self.slider_color, (self.bar_rect.width - self.bar_rect.height, self.bar_rect.height / 2), self.bar_rect.height / 2)  # Draw the slider circle

        # Create the slider surface
        self.slider_surface = pygame.Surface((self.bar_rect.height, self.bar_rect.height), pygame.SRCALPHA)
        self.slider_surface.fill((0, 0, 0, 0))
        pygame.draw.circle(self.slider_surface, self.slider_color, (self.bar_rect.height // 2, self.bar_rect.height // 2), slider_radius)

    def calculate_slider_position(self, value: int) -> int:
        # Ensure the value is within the defined range
        if value < self.min_value:
            value = self.min_value
        elif value > self.max_value:
            value = self.max_value
        # Calculate the position based on the value
        return int(self.bar_rect.x + (value - self.min_value) / (self.max_value - self.min_value) * (self.bar_rect.width - self.bar_rect.height) + self.bar_rect.height / 2)

    def set_value(self, value: int):
        # Update the value and recalculate the slider position
        self.value = value
        self.slider_position = self.calculate_slider_position(value)

    def update_location(self, mouse_x: int):
        # Update the slider position based on mouse input
        #TODO: change offset constant (+ self.bar_rect.height // 2)
        if self.wrapper_rect.collidepoint(mouse_x, self.bar_rect.y + self.bar_rect.height // 2):
            # Calculate the new value based on mouse position
            new_value = int(self.min_value + (mouse_x - self.bar_rect.x) / (self.bar_rect.width - self.bar_rect.height) * (self.max_value - self.min_value))
            self.slider_position = self.calculate_slider_position(new_value)

    def draw(self, surface: pygame.Surface):
        # Redraw the bar and slider surfaces
        self.bar_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.bar_surface, self.bar_color, (self.bar_rect.height / 2, 0, self.bar_rect.width - self.bar_rect.height, self.bar_rect.height))  # Draw the bar
        pygame.draw.circle(self.bar_surface, self.slider_color, (self.bar_rect.height / 2, self.bar_rect.height / 2), self.bar_rect.height / 2)  # Draw the slider circle
        pygame.draw.circle(self.bar_surface, self.slider_color, (self.bar_rect.width - self.bar_rect.height, self.bar_rect.height / 2), self.bar_rect.height / 2)  # Draw the slider circle

        self.slider_surface.fill((0, 0, 0, 0))
        pygame.draw.circle(self.slider_surface, self.slider_color, (self.bar_rect.height // 2, self.bar_rect.height // 2), self.slider_radius)

        # Draw the slider on the bar surface
        surface.blit(self.bar_surface, self.bar_rect.topleft)

        # Draw the bar and slider on the main surface
        surface.blit(self.bar_surface, self.bar_rect.topleft)
