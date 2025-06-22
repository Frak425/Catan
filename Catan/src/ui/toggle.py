import pygame
import pytweening as tween

class Toggle:
    def __init__(self, time: int, time_to_flip: float, location: tuple[int], height: int, center_width: int, fill_color: tuple[int], toggle_color: tuple[int], toggle_gap: int, toggle_name: str, on: bool = False, callback=None) -> None:
        self.name = toggle_name
        self.callback = callback

        #Background properties
        self.height = height
        self.center_width = center_width
        self.radius = height / 2
        self.rect = pygame.Rect(location[0], location[1], center_width + height, height)
        self.fill_color = fill_color

        #Toggle circle properties
        self.toggle_color = toggle_color
        self.toggle_gap = toggle_gap
        self.toggle_radius = self.height / 2 - self.toggle_gap

        #Animation properties
        self.start_time = time
        self.time_to_flip = time_to_flip
        self.location = location
        self.on = on
        self.animating = False
        self.toggle_circle_on_location = (self.height // 2, self.height // 2)
        self.toggle_circle_off_location = (self.height // 2 + self.center_width, self.height // 2)

        #Create the toggle's background surface
        self.surface = pygame.Surface((self.center_width + self.height, self.height), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))  # Transparent background
        pygame.draw.circle(self.surface, self.fill_color, (self.radius, self.height // 2), self.radius)
        pygame.draw.circle(self.surface, self.fill_color, (self.center_width + self.height - self.radius, self.height // 2), self.radius)
        pygame.draw.rect(self.surface, self.fill_color, (self.height / 2, 0, self.center_width, self.height))

        #Create the toggle circle
        self.toggle_circle = pygame.Surface((self.height - self.toggle_gap, self.height - self.toggle_gap), pygame.SRCALPHA)
        self.toggle_circle.fill((0, 0, 0, 0))  # Transparent background
        pygame.draw.circle(self.toggle_circle, self.toggle_color, (self.toggle_radius, self.toggle_radius), self.toggle_radius)
    
    def set_animating(self, time: int):
        self.animating = True
        self.time = time
        self.start_time = time
        self.end_time = time + int(self.time_to_flip * 1000)
    
    def update(self, new_time: int):
        if self.animating:
            if new_time >= self.end_time:
                self.animating = False
                self.on = not self.on
                return
            
            progress = (new_time - self.start_time) / (self.end_time - self.start_time)
            progress = tween.easeInOutQuad(progress)
            if self.on:
                self.toggle_circle_on_location = (self.height // 2 + int((self.center_width - self.height) * progress), self.height // 2)
            else:
                self.toggle_circle_off_location = (self.height // 2 + int((self.center_width - self.height) * progress), self.height // 2)

    def draw(self, surface: pygame.Surface):
        # Draw the toggle on the background and then the background to the surfac 
        self.surface.blit(self.toggle_circle, self.toggle_circle_on_location if self.on else self.toggle_circle_off_location)
        surface.blit(self.surface, self.rect.topleft)
