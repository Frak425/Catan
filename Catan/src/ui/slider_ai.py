from pygame import *
import pygame

class Slider:
    def __init__(self, screen: Surface, location: tuple[int, int], length: int = 200, width: int = 10, knob_size: tuple[int, int] = (20, 20), min_value: float = 0.0, max_value: float = 1.0, default_value: float = 0.5, bar_asset: Surface = None, knob_asset: Surface = None) -> None:
        """
        A slider UI element with click-and-drag support.
        
        :param screen: Pygame Surface to draw on.
        :param location: Tuple (x, y) for the slider's position.
        :param length: Length of the slider bar.
        :param width: Width of the slider bar.
        :param knob_size: Size (width, height) of the slider knob.
        :param min_value: Minimum value of the slider.
        :param max_value: Maximum value of the slider.
        :param default_value: Default starting value of the slider.
        :param bar_asset: Custom asset for the slider bar (optional).
        :param knob_asset: Custom asset for the knob (optional).
        """
        self.screen = screen
        self.location = location
        self.length = length
        self.width = width
        self.knob_size = knob_size
        self.min_value = min_value
        self.max_value = max_value
        self.value = default_value
        self.dragging = False

        # Create default assets if not provided
        if bar_asset:
            self.bar = bar_asset
        else:
            self.bar = pygame.Surface((self.length, self.width))
            self.bar.fill((150, 150, 150))  # Gray bar

        if knob_asset:
            self.knob = knob_asset
        else:
            self.knob = pygame.Surface(self.knob_size, pygame.SRCALPHA)
            self.knob.fill((255, 0, 0))  # Red knob

        # Define bar and knob rects
        self.bar_rect = pygame.Rect(self.location[0], self.location[1], self.length, self.width)
        self.knob_x = self.location[0] + (self.value - self.min_value) / (self.max_value - self.min_value) * self.length
        self.knob_rect = pygame.Rect(self.knob_x, self.location[1] - (self.knob_size[1] - self.width) // 2,
                                     self.knob_size[0], self.knob_size[1])

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handles mouse events for clicking and dragging."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.knob_rect.collidepoint(event.pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Clamp knob movement within slider bounds
            mouse_x = event.pos[0]
            self.knob_x = max(self.location[0], min(mouse_x, self.location[0] + self.length))
            self.knob_rect.x = self.knob_x

            # Update slider value
            self.value = self.min_value + ((self.knob_x - self.location[0]) / self.length) * (self.max_value - self.min_value)

    def draw(self) -> None:
        """Draws the slider on the screen."""
        self.screen.blit(self.bar, self.location)
        self.screen.blit(self.knob, (self.knob_rect.x, self.knob_rect.y))
