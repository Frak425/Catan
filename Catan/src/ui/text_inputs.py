import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.managers.game_manager import GameManager  

class TextInput:
    def __init__(self, layout_props: dict, font: pygame.font.Font, game_manager: "GameManager") -> None:
        self.game_manager = game_manager

        #initialize defaults so read_layout() can fall back reliably
        self.name = ""
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.background_color = (255, 255, 255)
        self.text_color = (0, 0, 0)
        self.padding = 5
        self.text = ""
        self.font = font

        # read layout and override default values
        self.read_layout(layout_props)

        # Render the text surface
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect()

        # Create the background surface
        self.background_surface = pygame.Surface((self.text_rect.width + 2 * self.padding, self.text_rect.height + 2 * self.padding))
        self.background_surface.fill(self.background_color)

        self.background_rect = self.background_surface.get_rect()

        # read layout and override default values
        self.read_layout(layout_props)

    def update_text(self, new_text: str) -> None:
        self.text = new_text
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect()

    def draw(self, screen: pygame.Surface) -> None:
        # Center the text on the background
        self.text_rect.center = self.background_rect.center

        # Blit the background and text to the screen
        self.background_surface.fill(self.background_color)
        self.background_surface.blit(self.text_surface, self.text_rect)
        screen.blit(self.background_surface, self.background_rect)

    def read_layout(self, layout_props: dict) -> None:
        
        # Schema reference: See [layout.json](./config/layout.json#L240-L260)
        
        self.name = layout_props.get("name", self.name)
        rect_data = layout_props.get("rect", [self.rect.x, self.rect.y, self.rect.width, self.rect.height])
        self.rect = pygame.Rect(rect_data[0], rect_data[1], rect_data[2], rect_data[3])
        color_data = layout_props.get("color", [self.background_color[0], self.background_color[1], self.background_color[2]])
        self.background_color = (color_data[0], color_data[1], color_data[2])
        self.text = layout_props.get("text", self.text)
        text_color_data = layout_props.get("text_color", [self.text_color[0], self.text_color[1], self.text_color[2]])
        self.text_color = (text_color_data[0], text_color_data[1], text_color_data[2])
        self.padding = layout_props.get("padding", self.padding)
    
    def get_layout(self) -> dict:
        return {
            "name": self.name,
            "rect": [self.rect.x, self.rect.y, self.rect.width, self.rect.height],
            "color": [self.background_color[0], self.background_color[1], self.background_color[2]],
            "text": self.text,
            "text_color": [self.text_color[0], self.text_color[1], self.text_color[2]],
            "padding": self.padding
        }
    
    def read_settings(self, settings: dict) -> None:
        pass

    def get_settings(self) -> dict:
        return {}