import pygame
import random

from classes.button import Button

class Drag_n_drop(Button):
    def __init__(self, layer: str, color: tuple[int], text: str, rect: list[int], var_name: str, screen, font) -> None:
        super().__init__(layer, color, text, rect, var_name, screen, font)