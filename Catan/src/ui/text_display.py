import pygame
from pygame import *
import math

class TextDisplay:
    def __init__(self, font: pygame.font.Font, text: str, background_image: pygame.Surface = None, background_color: tuple[int] = (255, 255, 255), text_color: tuple[int] = (0, 0, 0), padding: int = 5) -> None:
        self.font = font
        self.text = text
        self.background_image = background_image
        self.background_color = background_color
        self.text_color = text_color
        self.padding = padding

        # Render the text surface
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect()

        # Create the background surface
        if self.background_image:
            self.background_surface = self.background_image
            self.background_rect = self.background_surface.get_rect()
        else:
            self.background_surface = pygame.Surface((self.text_rect.width + 2 * self.padding, self.text_rect.height + 2 * self.padding))
            self.background_surface.fill(self.background_color)
            self.background_rect = self.background_surface.get_rect()

    def update_text(self, new_text: str) -> None:
        self.text = new_text
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect()

    def draw(self, screen: pygame.Surface) -> None:
        # Center the text on the background
        self.text_rect.center = self.background_rect.center

        # Blit the background and text to the screen
        screen.blit(self.background_surface, self.background_rect)
        screen.blit(self.text_surface, self.text_rect)