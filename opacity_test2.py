import pygame

pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()

# Create transparent surfaces
circle_surface = pygame.Surface((100, 100), pygame.SRCALPHA)  # Allows transparency
square_surface = pygame.Surface((100, 100), pygame.SRCALPHA)  

# Draw a red square on the transparent surface
pygame.draw.rect(square_surface, (255, 0, 0, 255), (0, 0, 100, 100))  

# Draw a blue circle on another transparent surface
pygame.draw.circle(circle_surface, (0, 0, 255, 255), (50, 50), 50)  

running = True
while running:
    screen.fill((30, 30, 30))  # Fill background with dark gray
    
    # Draw both surfaces on top of each other
    screen.blit(square_surface, (200, 200))  # First, draw the square
    screen.blit(circle_surface, (200, 200))  # Then, draw the circle on top

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    clock.tick(60)

pygame.quit()
