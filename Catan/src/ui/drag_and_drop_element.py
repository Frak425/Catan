import pygame
import random

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager
from src.ui.button import Button

class Drag_n_drop(Button):
    def __init__(self, layer: str, color: tuple[int, int, int], text: str, rect: list[int], var_name: str, screen, font, game_manager: "GameManager") -> None:
        super().__init__(color, text, pygame.Rect(rect), var_name, screen, font, (rect[0], rect[1]), game_manager)
        self.layer = layer
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0