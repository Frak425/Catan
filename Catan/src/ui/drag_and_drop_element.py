import pygame
import random

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager
from src.ui.button import Button

class Drag_n_drop(Button):
    def __init__(self, layer: str, color: tuple[int], text: str, rect: list[int], var_name: str, screen, font, game_manager: "GameManager") -> None:
        super().__init__(layer, color, text, rect, var_name, screen, font, game_manager)