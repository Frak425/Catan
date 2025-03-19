import pygame
import pytweening as tween

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

start_pos = (100, 100)
end_pos = (400, 300)
duration = 2  # seconds
elapsed_time = 0

running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    elapsed_time = min(elapsed_time + dt, duration)
    t = elapsed_time / duration
    eased_t = tween.easeInOutQuad(t)
    current_pos = (
        start_pos[0] + (end_pos[0] - start_pos[0]) * eased_t,
        start_pos[1] + (end_pos[1] - start_pos[1]) * eased_t,
    )

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 0, 0), (*current_pos, 100, 50))
    pygame.display.flip()

pygame.quit()
