import pygame
from typing import Dict
from src.managers import *
from src.ui.button import Button
from src.ui.toggle import Toggle
from src.ui.slider import Slider

#import pytweening as tween

class Menu:
    def __init__(self, screen: pygame.Surface, game_font: pygame.font.Font , type: str, buttons: Dict[str, Dict[str, Button]], toggles: Dict[str, Dict[str, Toggle]], sliders: Dict[str, Dict[str, Slider]], menu_size: tuple[int, int], init_location: tuple | None= None, final_location: tuple | None= None, backdrop: pygame.Surface | None = None, bckg_color: tuple[int, int, int] | None = None, anim_length: int | None = None, start_time: float | None = None, time: int = 0) -> None:
        self.menu_size = menu_size #(length, width)
        self.type = type #"animated" or "static"
        self.backdrop = backdrop #defaults to backdrop if both are provided
        self.bckg_color = bckg_color #(r,g,b)
        self.screen = screen
        self.game_font = game_font
        # IN PROGRESS: adding tabs to the settings menu to further organize the settings
        self.tabs = ["input", "accessibility", "gameplay", "audio", "graphics"] #[input, accessibility, gameplay, audio, graphics]
        #self.selected_tab = self.tabs[0]
        self.active_tab = "input" #change as needed, should probably start on gameplay but should be whatever is first in the list
        self.buttons = buttons
        self.toggles = toggles
        self.sliders = sliders

        self.init_location = init_location #(x, y)
        self.final_location = final_location #(x,y)
        self.location = self.init_location
        self.open = False


        self.anim_length = anim_length #in seconds
        self.start_time = start_time
        self.elapsed_time = 0
        self.anim_reversed = False

        self.menu_surface = pygame.Surface((self.menu_size), pygame.SRCALPHA)

        if self.backdrop:
            self.menu_surface.blit(pygame.transform.scale(self.backdrop, self.menu_size), (0, 0))
        else:
            assert self.bckg_color is not None
            self.menu_surface.fill(self.bckg_color)

        self.update_menu(time)

        pygame.draw.rect(self.screen, (100, 200, 200), [100, 100, 50, 50])
    
    def open_menu(self):
        self.location = self.final_location

    def close_menu(self):
        self.location = self.init_location

    def update_menu(self, time: int):
        # When refreshing the menu...
        # Refresh the background and cover everything previously
        assert self.bckg_color is not None
        self.menu_surface.fill((self.bckg_color))

        # Blit tabs on the menu surface
        for button_name, button in self.buttons["tabs"].items():
            button.draw(self.menu_surface)

        # Blit the active tab's buttons on the menu surface
        for button_name, button in self.buttons[self.active_tab].items():
            button.draw(self.menu_surface)

        # Blit toggles on the menu surface
        for toggle_name, toggle in self.toggles[self.active_tab].items():
            toggle.draw(self.menu_surface, time)

        for slider_name, slider in self.sliders[self.active_tab].items():
            slider.draw(self.menu_surface)

    def draw(self, time):
        self.update_menu(time)
        assert self.location is not None
        self.screen.blit(self.menu_surface, self.location)