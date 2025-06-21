import pygame
from src.ui.button import Button

class HelperManager:
    def __init__(self):
        pass

    def midpoint(self, point1: tuple[int], point2: tuple[int]) -> tuple:
        return ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)

    def check_point_in_rect(self, rect: list[int], point: tuple[int]) -> bool:
        x, y, w, h = rect
        px, py = point
        if (px > x and px < (x + w)) and \
        (py > y and py < (y + h)):
            return True
        else:
            return False

    def point_in_polygon(self, point: tuple[int], polygon: list[tuple[int]]) -> bool:
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
                if y > min(p1.y, p2.y):
                    # Check if the point is below the maximum y coordinate of the edge
                    if y <= max(p1.y, p2.y):
                        # Check if the point is to the left of the maximum x coordinate of the edge
                        if x <= max(p1.x, p2.x):
                            # Calculate the x-intersection of the line connecting the point to the edge
                            x_intersection = (y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x
        
                            # Check if the point is on the same line as the edge or to the left of the x-intersection
                            if p1.x == p2.x or x <= x_intersection:
                                # Flip the inside flag
                                inside = not inside
        
                # Store the current point as the first point for the next iteration
                p1 = p2
        
            # Return the value of the inside flag
            return inside

    def check_button_list_clicked(self, buttons: list[Button], mouse_location: tuple[int], menu_offset_x = 0, menu_offset_y = 0) -> Button:
        for i in range(len(buttons)):
            if (self.check_point_in_rect(buttons[i].rect, (mouse_location[0] + menu_offset_x, mouse_location[1] + menu_offset_y))):
                return buttons[i]
