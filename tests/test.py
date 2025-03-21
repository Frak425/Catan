import pygame
from src.ui.toggle import Toggle
from helperFunctions import *

pygame.init()
#set resolution
screen_info = pygame.display.Info()
screen_w = screen_info.current_w
screen_h = screen_info.current_h
screen = pygame.display.set_mode((screen_w, screen_h))

clock = pygame.time.Clock()

l = 25
w = l
toggle = Toggle(screen, (screen_w / 2, screen_h / 2), size = (l, w), checked = False)
#slider = Slider(screen, (screen_w / 2, screen_h / 2), 200)

running = True
while running:
    toggle.draw()
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            if check_point_in_rect(toggle.rect, (x, y)):
                toggle.handle_click()

    pygame.display.flip()

pygame.quit()