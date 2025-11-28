import pygame

from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

class Slider:
    def __init__(self, layout_props: dict, initial_value: int | float, game_manager: "GameManager",  bar_image: pygame.Surface | None, callback: Optional[Callable] = None) -> None:
        self.game_manager = game_manager

        #initialize defaults so read_layout() can fall back reliably
        self.name = ""
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.wrapper_rect = pygame.Rect(0, 0, 0, 0)
        self.min_value = 0
        self.max_value = 100
        self.bar_color = (0, 100, 0)
        self.handle_color = (100, 0, 0)
        self.handle_radius = 10
        self.direction = "horizontal"  # or "vertical"
        self.handle_shape = "circle"  # or "rectangle" or "stadium"
        self.handle_length = 0  # used if handle_shape is rectangle
        self.guiding_line_color = (100, 100, 200)
        self.is_active = False

        # read layout and override default values
        self.read_layout(layout_props)

        self.value = initial_value
        self.bar_image = bar_image

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

    def calculate_value(self) -> int:
        # Calculate the value based on the slider position
        denom_pixels = (self.rect.width - self.rect.height) if self.direction == "horizontal" else (self.rect.height - self.rect.width)
        if denom_pixels == 0:
            return int(self.min_value)
        relative_position = self.slider_position / denom_pixels
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

    def trigger(self):
        if self.callback:
            self.callback()

    def draw(self, surface: pygame.Surface):
        # Redraw the bar and slider surfaces
        self.draw_surface.fill((0, 0, 0, 0))  # Clear the drawing surface
        centered_x = (self.wrapper_rect.width - self.rect.width) / 2
        centered_y = (self.wrapper_rect.height - self.rect.height) / 2
        self.draw_surface.blit(self.bar_surface, (centered_x, centered_y))  # Draw the bar surface centered in the wrapper
        self.draw_surface.blit(self.handle_surface, (centered_x + self.slider_position, centered_y))  # Draw the slider surface at the correct position

        # Draw the bar and slider on the main surface
        surface.blit(self.draw_surface, self.wrapper_rect.topleft)

        if self.is_active:
            self.draw_guiding_lines(surface)

    def read_layout(self, layout_props: dict):

        # Schema ref: See [layout.json](./config/layout.json#L188-215)

        self.name: str = layout_props.get("name", self.name)
        rect_data = layout_props.get("rect", [self.rect.x, self.rect.y, self.rect.width, self.rect.height])
        self.rect: pygame.Rect = pygame.Rect(rect_data[0], rect_data[1], rect_data[2], rect_data[3])
        wrapper_rect_data = layout_props.get("wrapper_rect", [self.wrapper_rect.x, self.wrapper_rect.y, self.wrapper_rect.width, self.wrapper_rect.height])
        self.wrapper_rect = pygame.Rect(wrapper_rect_data[0], wrapper_rect_data[1], wrapper_rect_data[2], wrapper_rect_data[3])
        self.min_value: int = layout_props.get("min_value", self.min_value)
        self.max_value: int = layout_props.get("max_value", self.max_value)
        bar_color_data = layout_props.get("bar_color", [self.bar_color[0], self.bar_color[1], self.bar_color[2]])
        self.bar_color: tuple[int, int, int] = (bar_color_data[0], bar_color_data[1], bar_color_data[2])
        handle_color_data = layout_props.get("handle_color", [self.handle_color[0], self.handle_color[1], self.handle_color[2]])
        self.handle_color: tuple[int, int, int] = (handle_color_data[0], handle_color_data[1], handle_color_data[2])
        self.handle_radius: int = layout_props.get("handle_radius", self.handle_radius)
        self.direction: str = layout_props.get("direction", self.direction)
        self.handle_shape: str = layout_props.get("handle_shape", self.handle_shape)
        self.handle_length: int = layout_props.get("handle_length", self.handle_length)

    def get_layout(self) -> dict:
        return {
            "name": self.name,
            "rect": [self.rect.x, self.rect.y, self.rect.width, self.rect.height],
            "wrapper_rect": [self.wrapper_rect.x, self.wrapper_rect.y, self.wrapper_rect.width, self.wrapper_rect.height],
            "min_value": self.min_value,
            "max_value": self.max_value,
            "bar_color": [self.bar_color[0], self.bar_color[1], self.bar_color[2]],
            "handle_color": [self.handle_color[0], self.handle_color[1], self.handle_color[2]],
            "handle_radius": self.handle_radius,
            "direction": self.direction,
            "handle_shape": self.handle_shape,
            "handle_length": self.handle_length,
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
    