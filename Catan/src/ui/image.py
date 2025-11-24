import pygame

class Image:
    def __init__(self, name: str, rect: pygame.Rect, image_path: str = None, default_color: tuple = (100, 100, 100)):
        self.name = name
        self.rect = rect
        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.image_path = image_path
        if self.image_path:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.surface.blit(self.image, (0, 0))
        else:
            self.surface.fill(default_color)


    def draw(self, surface: pygame.surface.Surface):
        surface.blit(self.surface)
        