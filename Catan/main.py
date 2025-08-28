import pygame
import random
import math

from src.managers.game_manager import GameManager
from src.managers.audio_manager import AudioManager
from src.managers.graphics_manager import GraphicsManager
from src.managers.helper_manager import HelperManager
from src.managers.input_manager import InputManager
from src.managers.player_manager import PlayerManager

from src.scenes.board import Board
from src.scenes.game_over import GameOver
from src.scenes.game_setup import GameSetup
from src.scenes.title_screen import TitleScreen


#initialize game
pygame.init()
#set resolution
screen_info = pygame.display.Info()
screen_w = screen_info.current_w
screen_h = screen_info.current_h
screen = pygame.display.set_mode((screen_w, screen_h), flags=pygame.FULLSCREEN)

#set caption and icon
pygame.display.set_caption("Catan")
"""icon = pygame.image.load('')
pygame.display.set_icon(icon)"""

clock = pygame.time.Clock()

#managers act in a circular way, every one except game_manager calls every other one
#dependencies are installed after initialization
game_manager = GameManager(screen)
graphics_manager = GraphicsManager(clock.get_time())
input_manager = InputManager()
helper_manager = HelperManager()

graphics_manager.set_game_manager(game_manager)
graphics_manager.set_input_manager(input_manager)
graphics_manager.set_helper_manager(helper_manager)

input_manager.set_game_manager(game_manager)
input_manager.create_buttons()
input_manager.set_graphics_manager(graphics_manager)
input_manager.set_helper_manager(helper_manager)

#create scenes
title_screen = TitleScreen(game_manager)
game_setup = GameSetup(game_manager)
#board = Board(game_manager)
game_over = GameOver(game_manager)
#list_scenes = [title_screen, game_setup, board, game_over]

#game loop
while game_manager.running:

    clock.tick(game_manager.framerates[game_manager.framerate_index])
    screen.fill((30, 80, 150))

    #handles events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_manager.running = False
        #on a mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            input_manager.handle_input(x, y, pygame.MOUSEBUTTONDOWN)

        elif event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            input_manager.handle_input(x, y, pygame.MOUSEMOTION)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            x, y = event.pos
            input_manager.handle_input(x, y, pygame.MOUSEBUTTONUP)

    graphics_manager.draw_screen()
    graphics_manager.time = pygame.time.get_ticks()

    pygame.display.update()