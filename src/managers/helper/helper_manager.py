import pygame
from typing import Dict
from src.ui.elements.button import Button
from src.managers.base_manager import BaseManager

class HelperManager(BaseManager):
    def __init__(self):
        super().__init__()
        
    def initialize(self) -> None:
        """Initialize manager after all dependencies are injected."""
        pass
        
    def init(self):
        pass

    def midpoint(self, point1: tuple[int, int], point2: tuple[int, int]) -> tuple:
        return ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)

    def check_point_in_rect(self, rect: pygame.Rect, point: tuple[int, int]) -> bool:
        x, y, w, h = rect
        px, py = point
        if (px > x and px < (x + w)) and \
        (py > y and py < (y + h)):
            return True
        else:
            return False

    def point_in_polygon(self, point: tuple[int, int], polygon: list[tuple[int, int]]) -> bool:
            num_vertices = len(polygon)
            x, y = point[0], point[1]
            inside = False
        
            # Store the first point in the polygon and initialize the second point
            p1 = polygon[0]
        
            # Loop through each edge in the polygon
            for i in range(1, num_vertices + 1):
                # Get the next point in the polygon
                p2 = polygon[i % num_vertices]
        
                # Check if the point is above the minimum y coordinate of the edge
                if y > min(p1[1], p2[1]):
                    # Check if the point is below the maximum y coordinate of the edge
                    if y <= max(p1[1], p2[1]):
                        # Check if the point is to the left of the maximum x coordinate of the edge
                        if x <= max(p1[0], p2[0]):
                            # Calculate the x-intersection of the line connecting the point to the edge
                            x_intersection = (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]) + p1[0]
        
                            # Check if the point is on the same line as the edge or to the left of the x-intersection
                            if p1[0] == p2[0] or x <= x_intersection:
                                # Flip the inside flag
                                inside = not inside
        
                # Store the current point as the first point for the next iteration
                p1 = p2
        
            # Return the value of the inside flag
            return inside

    #TODO: proper type annotations for clickables
    def check_clickable_from_dict(self, clickables, mouse_location: tuple[int, int], offset_x = 0, offset_y = 0):
        for name, class_instance in clickables.items():
            if hasattr(class_instance, 'shown') and not class_instance.shown:
                continue
            if hasattr(class_instance, 'active') and not class_instance.active:
                continue
            if class_instance.rect.collidepoint(mouse_location[0] - offset_x, mouse_location[1] - offset_y):
                return class_instance
                
        return None

    