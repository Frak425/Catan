from pygame import *
import pygame
from helperFunctions import *

class Toggle:
    def __init__(self, screen: Surface, location: tuple[int], unchecked_box: Surface=None, checkmark: Surface=None, size: tuple[int]=(25, 25), checked=False) -> None:
        #TODO: Create assets for box and checkmark
        self.screen = screen
        self.location = location
        self.size = size
        self.rect = [self.location[0], self.location[1], self.size[0], self.size[1]]
        self.checked = checked
        if unchecked_box and checkmark:
            self.checkmark = checkmark
            self.unchecked_box = unchecked_box
            self.checked_box = self.create_checked()
        else:
            self.unchecked_box = Surface(self.size)
            self.unchecked_box.fill((255, 50, 50))
            self.checked_box = Surface(self.size)
            self.checked_box.fill((50, 255, 50))

    def create_checked(self) -> Surface:
        self.temp_box = self.unchecked_box.copy()
        self.temp_box.blit(self.checkmark, (0, 0))
        return self.temp_box

    def handle_click(self) -> None:
        self.checked = not self.checked

    def draw(self) -> None:
        if self.checked:
            self.screen.blit(self.checked_box, self.location)
        else:
            self.screen.blit(self.unchecked_box, self.location)