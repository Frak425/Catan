import pygame
from src.managers import *
from src.ui.button import Button

import pytweening as tween

class Menu:
    def __init__(self, screen: pygame.Surface, game_font: pygame.Font , type: str,  menu_size: tuple[int], init_location: tuple = None, final_location: tuple = None, backdrop: pygame.Surface = None, bckg_color: tuple[int] = None, anim_length: int = None, start_time: float = None) -> None:
        self.menu_size = menu_size #(length, width)
        self.type = type #"animated" or "static"
        self.backdrop = backdrop #defaults to backdrop if both are provided
        self.bckg_color = bckg_color #(r,g,b)
        self.screen = screen
        self.game_font = game_font
        # IN PROGRESS: adding tabs to the settings menu to further organize the settings
        self.tabs = [] #[input, accessibility, gameplay, audio, graphics]
        #self.selected_tab = self.tabs[0]

        self.buttons = self.create_buttons()

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
            self.menu_surface.fill(self.bckg_color)

        for button in self.buttons:
            button.draw_button(self.menu_surface)

        pygame.draw.rect(self.screen, (100, 200, 200), [100, 100, 50, 50])

    def create_buttons(self) -> list[Button]:
        settings_buttons = {}
        for tab in self.tabs:
            if tab == "input":
                """
                Input (keyboard and controller):
                -Controller vibration (toggle)
                -Deadzone adjustment (slider)
                -Invert Y and X axes (toggles)
                -Key remapping (list TBD: something similar to minecraft w/ keyboard and controller inputs listed?)
                -Sensitivities (sliders TBD)
                """
                input_buttons = [] #TODO: fill with buttons
                settings_buttons[tab] = input_buttons

            elif tab == "accessibility":
                """
                Accessibility:
                -Colorblind mode: deuteranopia, protanopia, and tritanopia (multi-choice select box)
                -Font Size: small, medium, large (multi-choice select box)
                -High contrast mode (toggle)
                -TTS: Hesitant to implement because limited usage and maximal time to produce
                """
                accessibility_buttons = [] #TODO: fill with buttons
                settings_buttons[tab] = accessibility_buttons

            elif tab == "graphics":
                """
                Graphics:
                -AA (toggle)
                -Brightness (slider)
                -Windowed/fullscreen (toggle)
                -Particle effects (toggle)
                -Resolution (multi-choice select box)
                -Shadows (toggle)
                -Texture quality (multi-choice select box)
                -V-sync (toggle)
                """
                graphics_buttons = [] #TODO: fill with buttons
                settings_buttons[tab] = graphics_buttons

            elif tab == "audio":
                """
                Audio:
                -Master (slider)
                -Music (slider)
                -SFX (toggle)
                """
                audio_buttons = [] #TODO: fill with buttons
                settings_buttons[tab] = audio_buttons

            elif tab == "gameplay":
                """
                Gameplay:
                -HUD (ask ChatGPT)
                -Language (multi-choice select box)
                """
                gameplay_buttons = [] #TODO: fill with buttons
                settings_buttons[tab] = gameplay_buttons
                
            else:
                print("Error: incorrect tab name")
     
        return settings_buttons

    #TODO: Find a way to deal with buttons' functions. How do they interact with the game as a whole?
    def clicked(self, coordinates: tuple[int]) -> None:
        for button in self.buttons:
            #check to close menu
            if button.check_clicked(coordinates) and button.var_name == "X":
                self.close_menu()

    def update_offset(self, time: float):
        dt = time - self.start_time
        if not reverse:
            elapsed_time += dt
            if elapsed_time >= self.anim_length:  # Switch direction at the end
                elapsed_time = self.anim_length
                reverse = True
        else:
            elapsed_time -= dt
            if elapsed_time <= 0:  # Switch direction at the start
                elapsed_time = 0
                reverse = False

        t = elapsed_time / self.anim_length  # Normalize time to [0, 1]
        eased_t = tween.easeInOutQuad(t)  # Use an easing function

        self.init_location[0] + (self.final_location[0] - self.init_location[0]) * eased_t,
        self.init_location[1] + (self.final_location[1] - self.init_location[1]) * eased_t,
    
    def open_menu(self):
        self.open = True
        self.location = self.final_location

    def close_menu(self):
        self.open = False
        self.location = self.init_location

    def draw(self, time):
        if self.type == "animated":
            self.update_offset(time)
        self.screen.blit(self.menu_surface, self.location)