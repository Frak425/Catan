import pygame
import random
import math

from src.managers.game_manager import GameManager
from src.managers.audio_manager import AudioManager
from src.managers.graphics_manager import GraphicsManager
from src.managers.helper_manager import HelperManager
from src.managers.input_manager import InputManager
from src.managers.player_manager import PlayerManager

#from src.scenes.board import Board
from src.scenes.game_over import GameOver
from src.scenes.game_setup import GameSetup
from src.scenes.title_screen import TitleScreen


#initialize game
pygame.init()
#set resolution
screen_info = pygame.display.Info()
screen_w = screen_info.current_w
screen_h = screen_info.current_h
screen = pygame.display.set_mode((screen_w, screen_h))

#set caption and icon
pygame.display.set_caption("Catan")
"""icon = pygame.image.load('')
pygame.display.set_icon(icon)"""

clock = pygame.time.Clock()

#managers act in a circular way, every one except game_manager calls every other one
#dependencies are installed after initialization
game_manager = GameManager(screen)
graphics_manager = GraphicsManager()
input_manager = InputManager()
helper_manager = HelperManager()

graphics_manager.set_game_manager(game_manager)
graphics_manager.set_input_manager(input_manager)
graphics_manager.set_helper_manager(helper_manager)

input_manager.set_game_manager(game_manager)
input_manager.set_graphics_manager(graphics_manager)
input_manager.set_helper_manager(helper_manager)

#create scenes
title_screen = TitleScreen(game_manager)
game_setup = GameSetup(game_manager)
#board = Board(game_manager)
game_over = GameOver(game_manager)
#list_scenes = [title_screen, game_setup, board, game_over]

#game loop
running = True
while running:

    clock.tick(game_manager.framerates[game_manager.framerate_index])
    screen.fill((30, 80, 150))

    #handles events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #on a mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            #click in main menu
            if (game_manager.game_state == "main_menu"):
                input_manager.handle_main_menu(x, y)
            
            #click in menu, comes before others because menu clicks are mutually exclusive to the other layers
            elif (game_manager.menu.open):
                input_manager.handle_menu(x, y)
                    
            #click in setup
            elif (game_manager.game_state == "game_setup"):
                input_manager.handle_setup(x, y)

            #click in game
            elif (game_manager.game_state == "game_ongoing"):
                input_manager.handle_game(x, y)

            
    graphics_manager.draw_screen()
    graphics_manager.draw_menu()

    pygame.display.update()