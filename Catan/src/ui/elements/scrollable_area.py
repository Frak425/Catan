import pygame
from src.ui.elements.slider import Slider
from src.ui.ui_element import UIElement

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

class ScrollableArea(UIElement):
    def __init__(self, layout_props: dict, game_manager: GameManager, content_surface: pygame.Surface) -> None:
        # Call parent constructor to initialize common UIElement attributes
        super().__init__(layout_props, game_manager, callback=None, shown=True)
        
        #TODO: implement theme class for images. Currently images are not passed in so default colors are used
        #set defaults
        self.rect = pygame.Rect(0, 0, 300, 400)
        self.exterior_padding = 5
        self.interior_padding = 5
        self.content_surface = content_surface
        self.content_scroll = 0  # current scroll position in pixels
        self.background_color = (240, 240, 240, 255)
        self.background_image = None 
        self.content_background_color = (255, 255, 255, 255)
        self.content_background_image = None
        self.content_width_percentage = .9 # percentage of total width for content area
        self.slider_image = None
        self.slider_handle_image = None
        self.slider_handle_inset = 2
        self.slider_side = "right"  # or "left"

        self.viewable_content_height = self.rect.height - 2 * self.exterior_padding
        # Calculate usable width (after exterior padding and interior padding between content and slider)
        usable_width = self.rect.width - 2 * self.exterior_padding - self.interior_padding
        self.viewable_content_width = int(usable_width * self.content_width_percentage)
        self.max_scroll = max(0, self.content_surface.get_height() - self.viewable_content_height)
        
        self.slider_height = self.viewable_content_height
        self.slider_width = usable_width - self.viewable_content_width
        self.slider_x = self.rect.width - self.exterior_padding - self.slider_width if self.slider_side == "right" else self.exterior_padding
        self.slider_y = self.exterior_padding


        self.slider_layout_props = {
            "name": "slider",
            "rect": [self.slider_x, self.slider_y, self.slider_width, self.slider_height],
            "min_value": 0,
            "max_value": 1,
            "color": [50, 50, 50],  # Dark gray bar
            "handle_color": [255, 255, 0],  # Bright yellow handle
            "handle_radius": int(self.slider_width / 2) - self.slider_handle_inset,
            "direction": "vertical",
            "handle_shape": "circle",
            "handle_length": 0
        }   

        self.read_layout(layout_props)

    def create_surfaces(self):
        self.create_background_surface()
        self.create_slider()

    def create_background_surface(self):
        self.background_surface = pygame.Surface((self.rect.width, self.rect.height))
        if self.background_image:
            self.background_surface.blit(self.background_image, (0, 0))
        else:
            self.background_surface.fill(self.background_color)

    def create_slider(self):
        self.slider = Slider(
            self.slider_layout_props,
            0,  # initial_value
            self.game_manager,
            bar_image=self.slider_image,
            handle_image=self.slider_handle_image,
            callback=self.set_content_scroll
        )

    def calculate_dependent_properties(self):
        self.viewable_content_height = self.rect.height - 2 * self.exterior_padding
        # Calculate usable width (after exterior padding and interior padding between content and slider)
        usable_width = self.rect.width - 2 * self.exterior_padding - self.interior_padding
        self.viewable_content_width = int(usable_width * self.content_width_percentage)
        self.max_scroll = max(0, self.content_surface.get_height() - self.viewable_content_height)

        self.slider_width = usable_width - self.viewable_content_width
        self.slider_x = self.rect.width - self.exterior_padding - self.slider_width if self.slider_side == "right" else self.exterior_padding
        
        self.slider_layout_props.update({
            "rect": [self.slider_x, self.slider_y, self.slider_width, self.slider_height],
            "handle_radius": int(self.slider_width / 2) - self.slider_handle_inset
        })

    #called by slider to update content scroll, the area of the content surface to draw
    def set_content_scroll(self) -> None:
        #takes slider value (0 to 1) and sets content surface scroll accordingly
        self.content_scroll = self.slider.value * self.max_scroll

    #called on mouse drag
    def update_scroll(self, x: int, y: int) -> None:
        # Adjust coordinates to be relative to the scrollable area
        relative_x = x - self.rect.x
        relative_y = y - self.rect.y
        self.slider.update_location(relative_x, relative_y)

    def draw(self, surface: pygame.Surface):
        if not self.shown:
            return
        
        # Draw background
        surface.blit(self.background_surface, (self.rect.x, self.rect.y))

        # Draw content area
        surface.blit(self.content_surface, (self.rect.x + self.exterior_padding, self.rect.y + self.exterior_padding), area=pygame.Rect(0, self.content_scroll, self.viewable_content_width, self.viewable_content_height))
        
        # Draw slider - temporarily adjust slider rect for drawing
        original_slider_x = self.slider.rect.x
        original_slider_y = self.slider.rect.y
        self.slider.rect.x += self.rect.x
        self.slider.rect.y += self.rect.y
        self.slider.draw(surface)
        self.slider.rect.x = original_slider_x
        self.slider.rect.y = original_slider_y

        # Draw guiding lines in dev mode
        if self.is_active:
            self.draw_guiding_lines(surface)

    def read_layout(self, layout_props: dict) -> None:
        self._read_common_layout(layout_props)

        self.slider_layout_props: dict = layout_props.get("slider_layout_props", {})

        self.exterior_padding = layout_props.get("exterior_padding", self.exterior_padding)
        self.interior_padding = layout_props.get("interior_padding", self.interior_padding)

        background_color_data = layout_props.get("background_color", [self.background_color[0], self.background_color[1], self.background_color[2], self.background_color[3]])
        self.background_color = (background_color_data[0], background_color_data[1], background_color_data[2], background_color_data[3])
        
        content_background_color_data = layout_props.get("content_background_color", [self.content_background_color[0], self.content_background_color[1], self.content_background_color[2], self.content_background_color[3]])
        self.content_background_color = (content_background_color_data[0], content_background_color_data[1], content_background_color_data[2], content_background_color_data[3])
                
        self.slider_side = layout_props.get("slider_side", self.slider_side)

        self.content_width_percentage = layout_props.get("content_width_percentage", self.content_width_percentage)

        #recalculate dependent properties
        self.calculate_dependent_properties()
        self.create_surfaces()

    def get_layout(self) -> dict:
        layout = self._get_common_layout()
        layout.update({
            "slider_layout_props": self.slider.get_layout(),
            "exterior_padding": self.exterior_padding,
            "interior_padding": self.interior_padding,
            "viewable_content_height": self.viewable_content_height,
            "viewable_content_width": self.viewable_content_width,
            "background_color": [self.background_color[0], self.background_color[1], self.background_color[2], self.background_color[3]],
            "content_background_color": [self.content_background_color[0], self.content_background_color[1], self.content_background_color[2], self.content_background_color[3]],
            "slider_side": self.slider_side,
            "content_width_percentage": self.content_width_percentage
        })
        #print(self.slider.get_layout())
        return layout
    
    def print_info(self) -> None:
        self.print_common_info()
        print(f"  Exterior Padding: {self.exterior_padding}")
        print(f"  Interior Padding: {self.interior_padding}")
        print(f"  Viewable Content Size: {self.viewable_content_width}x{self.viewable_content_height}")
        print(f"  Max Scroll: {self.max_scroll}")
        print(f"  Content Scroll: {self.content_scroll}")
        print(f"  Slider Side: {self.slider_side}")
        print(f"  Slider Info:")
        self.slider.print_info()

        