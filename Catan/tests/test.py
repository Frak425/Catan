import pygame, sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

clicks = []  # store all click positions

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            print("DOWN", event.pos)
            clicks.append(("down", event.pos))

        if event.type == pygame.MOUSEBUTTONUP:
            print("UP", event.pos)
            clicks.append(("up", event.pos))

    # clear screen
    screen.fill((30, 30, 30))

    # draw circles for each click
    for etype, pos in clicks:
        color = (255, 0, 0) if etype == "down" else (0, 255, 0)
        pygame.draw.circle(screen, color, pos, 6)

    pygame.display.flip()
    clock.tick(60)
