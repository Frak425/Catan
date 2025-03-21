import pygame
from pygame import Surface

class Slider:
    def __init__(self, screen: Surface, location: tuple[int], button_size: tuple[int]=(25,25), slider_size: tuple[int]=(200, 10)):
        self.screen = screen
        self.location = location
        self.button_size = button_size
        self.slider_size = slider_size
        self.dragging = False

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            pass

    def draw(self) -> None:
        pass