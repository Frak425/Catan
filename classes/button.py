import pygame
import math
import random

class Button:
    def __init__(self, layer: str, color: tuple[int], text: str, rect: list[int], button_name: str, surface: pygame.Surface, font, location: tuple[int]) -> None:
        self.layer = layer # main menu -> game setup -> board -> game over -> main menu
        self.color = color
        self.text = text
        self.rect = rect #includes location and size data
        self.button_name = button_name
        self.surface = surface
        self.game_font = font
        self.location = location
            
    def draw_button(self, surface=None) -> None:
        if surface:
            pygame.draw.rect(surface, self.color, self.rect) #change this to include backgrounds
            text = self.game_font.render(self.text, False, (0, 0, 0))
            surface.blit(text, (self.rect[0], self.rect[1]))
        else:
            pygame.draw.rect(self.surface, self.color, self.rect) #change this to include backgrounds
            text = self.game_font.render(self.text, False, (0, 0, 0))
            self.surface.blit(text, (self.rect[0], self.rect[1]))

    def check_clicked(self, coords: tuple[int]) -> bool:
        return self.check_point_in_rect(self.rect, coords)
    
    def check_point_in_rect(self, rect: list[int], point: tuple[int]) -> bool:
        x, y, w, h = rect
        px, py = point
        if (px > x and px < (x + w)) and \
        (py > y and py < (y + h)):
            return True
        else:
            return False