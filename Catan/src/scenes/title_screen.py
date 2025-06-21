import pygame
from src.ui.button import Button
from src.managers.game_manager import GameManager

class TitleScreen:
    def __init__(self, game_manager: GameManager):
        self.game_manager = game_manager
        self.buttons = self.create_buttons()

    def create_buttons(self) -> list[Button]:
        play_b_w = 200
        play_b_h = 75
        #play_button = Button("main_menu", (0, 100, 0), "PLAY", pygame.Rect(self.game_manager.screen_size[0] / 2 - play_b_w / 2, self.game_manager.screen_size[1] / 2 - play_b_h / 1.75, play_b_w, play_b_h), "play", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        #quit_button = Button("main_menu", (100, 0, 0), "QUIT", pygame.Rect(self.game_manager.screen_size[0] / 2 - play_b_w / 2, self.game_manager.screen_size[1] / 2 + play_b_h / 1.75, play_b_w, play_b_h), "quit", self.game_manager.screen, self.game_manager.game_font, (0, 0))
        #title_screen_buttons = [play_button, quit_button]
        #return title_screen_buttons


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    button.handle_click(event)

    def draw(self):
        """Draws the contents of the title screen"""
        pass

