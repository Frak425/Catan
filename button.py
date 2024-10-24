import pygame
import math
import random

class Button:
    def __init__(self, layer: str, color: tuple[int], text: str, rect: list[int], var_name: str, screen, font) -> None:
        self.layer = layer # main menu -> game setup -> board -> game over -> main menu
        self.color = color
        self.text = text
        self.rect = rect
        self.var_name = var_name
        self.screen = screen
        self.game_font = font
            
    def draw_button(self) -> None:
        pygame.draw.rect(self.screen, self.color, self.rect)
        text = self.game_font.render(self.text, False, (0, 0, 0))
        self.screen.blit(text, (self.rect[0], self.rect[1]))

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