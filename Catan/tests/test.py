# Example file showing a basic pygame "game loop"
import pygame
import math

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

circle_x = 50
circle_y = 50
circle_v_x = 10
circle_v_y = 10

square_x = 200
square_y = 300
square_v_x = 8
square_v_y = 8

square = pygame.Surface((50, 50))
square.fill("white")

circle = pygame.Surface((50, 50), pygame.SRCALPHA)  # per-pixel alpha
pygame.draw.circle(circle, "blue", (25, 25), 25)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    # RENDER YOUR GAME HERE

    #make square bounce around screen
    if (square_x > screen.get_width() - 50):
        square_v_x = -square_v_x
    if (square_x < 0):
        square_v_x = -square_v_x
    if (square_y > screen.get_height() - 50):
        square_v_y = -square_v_y 
    if (square_y < 0):
        square_v_y = -square_v_y

    #make circle bounce around screen
    if (circle_x > screen.get_width() - 50):
        circle_v_x = -circle_v_x
    if (circle_x < 0):
        circle_v_x = -circle_v_x
    if (circle_y > screen.get_height() - 50):
        circle_v_y = -circle_v_y 
    if (circle_y < 0):
        circle_v_y = -circle_v_y
        
    square_x += square_v_x
    square_y += square_v_y

    circle_x += circle_v_x
    circle_y += circle_v_y

    screen.blit(square, (square_x, square_y))
    screen.blit(circle, (circle_x, circle_y))

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(30)  # limits FPS to 60

pygame.quit()