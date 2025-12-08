import pygame
import random
import math

from src.managers.game_manager import GameManager
from src.managers.audio_manager import AudioManager
from src.managers.graphics_manager import GraphicsManager
from src.managers.helper_manager import HelperManager
from src.managers.input.input_manager import InputManager
from src.managers.player_manager import PlayerManager

#initialize game
pygame.init()
#set resolution
screen_info = pygame.display.Info()
screen_w = screen_info.current_w
screen_h = screen_info.current_h
screen = pygame.display.set_mode((1366, 768))

#set caption and icon
pygame.display.set_caption("Catan")
"""icon = pygame.image.load('')
pygame.display.set_icon(icon)"""

clock = pygame.time.Clock()

#managers act in a circular way, every one except game_manager calls every other one
#dependencies are installed after initialization
game_manager = GameManager()
game_manager.init(screen)
audio_manager = AudioManager()
#TODO: create list of player in game manager
player_manager = PlayerManager()
graphics_manager = GraphicsManager()
input_manager = InputManager()
helper_manager = HelperManager()

#set dependencies


input_manager.set_game_manager(game_manager)
input_manager.set_graphics_manager(graphics_manager)
input_manager.set_helper_manager(helper_manager)
input_manager.set_player_manager(player_manager)
input_manager.set_audio_manager(audio_manager)

graphics_manager.set_game_manager(game_manager)
graphics_manager.set_input_manager(input_manager)
graphics_manager.set_helper_manager(helper_manager)
graphics_manager.set_player_manager(player_manager)
graphics_manager.set_audio_manager(audio_manager)

game_manager.set_graphics_manager(graphics_manager)
game_manager.set_audio_manager(audio_manager)
game_manager.set_helper_manager(helper_manager)
game_manager.set_input_manager(input_manager)
game_manager.set_player_manager(player_manager)

audio_manager.set_game_manager(game_manager)
audio_manager.set_input_manager(input_manager)
audio_manager.set_helper_manager(helper_manager)
audio_manager.set_player_manager(player_manager)
audio_manager.set_graphics_manager(graphics_manager)

player_manager.set_game_manager(game_manager)
player_manager.set_input_manager(input_manager)
player_manager.set_helper_manager(helper_manager)
player_manager.set_audio_manager(audio_manager)
player_manager.set_graphics_manager(graphics_manager)

#init all managers
input_manager.init()
graphics_manager.init(pygame.time.get_ticks())
audio_manager.init()
player_manager.init([])
helper_manager.init()


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

        #on a keyboard press
        elif event.type == pygame.KEYDOWN:
            key = event.key
            input_manager.handle_keyboard(key)

    graphics_manager.draw_screen()
    graphics_manager.time = pygame.time.get_ticks()

    pygame.display.update()

pygame.quit()