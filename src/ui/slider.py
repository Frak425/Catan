import pygame
from pygame import Surface
from src.managers.game_manager import GameManager

class Slider:
    def __init__(self, game_manager: GameManager, location: tuple[int], button_size: tuple[int]=(25,25), slider_size: tuple[int]=(200, 10), min_max_vals: tuple[int]=(0, 100), bar_asset: Surface=None, knob_asset: Surface=None):
        self.game_manager = game_manager
        self.location = location
        self.button_size = button_size
        self.slider_size = slider_size
        self.min_max_vals = min_max_vals
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

        self.bar_rect = pygame.Rect(self.location[0], self.location[1], self.length, self.width)
        self.knob_x = self.location[0] + (self.value - self.min_value) / (self.max_value - self.min_value) * self.length
        self.knob_rect = pygame.Rect(self.knob_x, self.location[1] - (self.knob_size[1] - self.width) // 2,
                                     self.knob_size[0], self.knob_size[1])

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Clamp knob movement within slider bounds
            mouse_x = event.pos[0]
            self.knob_x = max(self.location[0], min(mouse_x, self.location[0] + self.slider_size[0]))
            self.knob_rect.x = self.knob_x

            # Update slider value
            self.value = self.min_max_vals[0] + ((self.knob_x - self.location[0]) / self.slider_size[0]) * (self.min_max_vals[1] - self.min_max_vals[0])

    def draw(self) -> None:
        self.game_manager.screen.blit(self.bar, self.location)
        self.game_manager.screen.blit(self.knob, (self.knob_rect.x, self.knob_rect.y))