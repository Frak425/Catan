import pygame
from src.managers.game_manager import GameManager
from src.ui.slider import Slider

pygame.init()
#set resolution
screen_info = pygame.display.Info()
screen_w = screen_info.current_w
screen_h = screen_info.current_h
screen = pygame.display.set_mode((screen_w, screen_h))

game_manager = GameManager(screen)

clock = pygame.time.Clock()

l = 25
w = l
slider = Slider(game_manager, (100, 100))

running = True
while running:
    slider.draw()
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        slider.handle_event(event)

    pygame.display.flip()

pygame.quit()