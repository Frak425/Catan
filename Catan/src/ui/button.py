import pygame
from pygame import *

class Button:
    def __init__(self, color: tuple[int], text: str, rect: Rect, button_name: str, surface: pygame.Surface, font, location: tuple[int]) -> None:
        self.color = color
        self.text = text
        self.rect = rect #includes location and size data
        self.name = button_name
        self.surface = surface
        self.game_font = font
        self.location = location
        self.shown = True

    def draw(self, surface=None) -> None:
        if not self.shown:
            return
        if surface:
            pygame.draw.rect(surface, self.color, self.rect) #change this to include backgrounds
            text = self.game_font.render(self.text, False, (0, 0, 0))
            surface.blit(text, (self.rect[0], self.rect[1]))
        else:
            pygame.draw.rect(self.surface, self.color, self.rect) #change this to include backgrounds
            text = self.game_font.render(self.text, False, (0, 0, 0))
            self.surface.blit(text, (self.rect[0], self.rect[1]))

    def hide(self) -> None:
        self.shown = False

    def show(self) -> None:
        self.shown = True