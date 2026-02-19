import pygame
import random
import math
import time

from src.managers.animation.animation_manager import AnimationManager
from src.managers.game.game_manager import GameManager
from src.managers.audio.audio_manager import AudioManager
from src.managers.graphics.graphics_manager import GraphicsManager
from src.managers.helper.helper_manager import HelperManager
from src.managers.input.input_manager import InputManager
from src.managers.player.player_manager import PlayerManager
from src.managers.animation.driver_manager import DriverManager

#initialize game
pygame.init()
#set resolution
screen_info = pygame.display.Info()
screen_w = screen_info.current_w
screen_h = screen_info.current_h
screen = pygame.display.set_mode((1366, 768), pygame.DOUBLEBUF, vsync=1)

#set caption and icon
pygame.display.set_caption("Catan")
"""icon = pygame.image.load('')
pygame.display.set_icon(icon)"""

clock = pygame.time.Clock()

#managers act in a circular way, every one except game_manager calls every other one
#dependencies are installed after initialization
game_manager = GameManager()
audio_manager = AudioManager()
#TODO: create list of player in game manager
player_manager = PlayerManager()
graphics_manager = GraphicsManager()
input_manager = InputManager()
helper_manager = HelperManager()

animation_manager = AnimationManager()
driver_manager = DriverManager()

# Inject dependencies using BaseManager dependency injection
game_manager.inject('input_manager', input_manager)
game_manager.inject('audio_manager', audio_manager)
game_manager.inject('graphics_manager', graphics_manager)
game_manager.inject('helper_manager', helper_manager)
game_manager.inject('player_manager', player_manager)
game_manager.inject('animation_manager', animation_manager)
game_manager.inject('driver_manager', driver_manager)

input_manager.inject('game_manager', game_manager)
input_manager.inject('graphics_manager', graphics_manager)
input_manager.inject('helper_manager', helper_manager)
input_manager.inject('player_manager', player_manager)
input_manager.inject('audio_manager', audio_manager)

graphics_manager.inject('game_manager', game_manager)
graphics_manager.inject('input_manager', input_manager)
graphics_manager.inject('helper_manager', helper_manager)
graphics_manager.inject('player_manager', player_manager)
graphics_manager.inject('audio_manager', audio_manager)

audio_manager.inject('game_manager', game_manager)
audio_manager.inject('input_manager', input_manager)
audio_manager.inject('helper_manager', helper_manager)
audio_manager.inject('player_manager', player_manager)
audio_manager.inject('graphics_manager', graphics_manager)

player_manager.inject('game_manager', game_manager)
player_manager.inject('input_manager', input_manager)
player_manager.inject('helper_manager', helper_manager)
player_manager.inject('audio_manager', audio_manager)
player_manager.inject('graphics_manager', graphics_manager)

driver_manager.inject('game_manager', game_manager)
driver_manager.inject('input_manager', input_manager)
driver_manager.inject('helper_manager', helper_manager)
driver_manager.inject('player_manager', player_manager)
driver_manager.inject('graphics_manager', graphics_manager)
driver_manager.inject('audio_manager', audio_manager)
driver_manager.inject('animation_manager', animation_manager)

# Initialize all managers after dependencies are injected
game_manager.initialize(screen)
graphics_manager.initialize()
input_manager.initialize()
audio_manager.initialize() 
player_manager.initialize()
helper_manager.initialize()
animation_manager.initialize()
driver_manager.initialize()

# Load layout config before initializing input_manager (which creates UI)
game_manager.load_config("layout", False)

#init all managers
graphics_manager.init(pygame.time.get_ticks())
input_manager.init()  # Creates UI from game_manager.layout

driver_manager.create_driver_registry()

audio_manager.init()
player_manager.init([])
helper_manager.init()

frame_times = []
event_times = []
input_times = []
draw_times = []
update_times = []

while game_manager.running:
    frame_start = time.perf_counter()

    clock.tick(game_manager.framerates[game_manager.framerate_index])
    screen.fill((30, 80, 150))

    #handles events
    event_start = time.perf_counter()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_manager.running = False
        #on a mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            input_start = time.perf_counter()
            input_manager.handle_input(x, y, pygame.MOUSEBUTTONDOWN)
            input_times.append((time.perf_counter() - input_start) * 1000)

        elif event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            input_start = time.perf_counter()
            input_manager.handle_input(x, y, pygame.MOUSEMOTION)
            input_times.append((time.perf_counter() - input_start) * 1000)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            x, y = event.pos
            input_start = time.perf_counter()
            input_manager.handle_input(x, y, pygame.MOUSEBUTTONUP)
            input_times.append((time.perf_counter() - input_start) * 1000)

        #on a keyboard press
        elif event.type == pygame.KEYDOWN:
            key = event.key
            input_start = time.perf_counter()
            input_manager.handle_keyboard(key)
            input_times.append((time.perf_counter() - input_start) * 1000)
    
    event_times.append((time.perf_counter() - event_start) * 1000)

    draw_start = time.perf_counter()
    graphics_manager.draw_screen()
    graphics_manager.time = pygame.time.get_ticks()
    draw_times.append((time.perf_counter() - draw_start) * 1000)

    update_start = time.perf_counter()
    pygame.display.update()
    update_times.append((time.perf_counter() - update_start) * 1000)

    frame_times.append((time.perf_counter() - frame_start) * 1000)
    
    if game_manager.debugging:
        # Print stats every 60 frames (once per second at 60fps)
        if len(frame_times) >= 60:
            print("\n=== Performance Stats (last 60 frames) ===")
            print(f"Total Frame Time: avg={sum(frame_times)/len(frame_times):.2f}ms, max={max(frame_times):.2f}ms")
            print(f"Event Handling:   avg={sum(event_times)/len(event_times):.2f}ms, max={max(event_times):.2f}ms")
            if input_times:
                print(f"Input Processing: avg={sum(input_times)/len(input_times):.2f}ms, max={max(input_times):.2f}ms, count={len(input_times)}")
            print(f"Draw Screen:      avg={sum(draw_times)/len(draw_times):.2f}ms, max={max(draw_times):.2f}ms")
            print(f"Display Update:   avg={sum(update_times)/len(update_times):.2f}ms, max={max(update_times):.2f}ms")
            print(f"Current FPS:      {clock.get_fps():.1f}")
            
            # Clear for next batch
            frame_times.clear()
            event_times.clear()
            input_times.clear()
            draw_times.clear()
            update_times.clear()

pygame.quit()