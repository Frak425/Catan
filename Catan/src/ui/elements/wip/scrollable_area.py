import pygame
from src.ui.elements.slider import Slider
from src.ui.ui_element import UIElement

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager

class ScrollableArea(UIElement):
    def __init__(self, layout_props: dict, game_manager: GameManager, content_surface: pygame.Surface) -> None:
        self.game_manager = game_manager

        #TODO: implement theme class for images. Currently images are not passed in so default colors are used
        #set defaults
        self.rect = pygame.Rect(0, 0, 300, 400)
        self.exterior_padding = 5
        self.interior_padding = 5
        self.viewable_content_height = 300
        self.viewable_content_width = 200
        self.content_surface = content_surface
        self.max_scroll = max(0, self.content_surface.get_height() - self.viewable_content_height)
        self.content_scroll = 0  # current scroll position in pixels
        self.background_color = (240, 240, 240, 255)
        self.background_image = None 
        self.content_background_color = (255, 255, 255, 255)
        self.content_background_image = None
        self.slider_width = self.rect.width - 2 * self.exterior_padding - self.viewable_content_width - self.interior_padding
        self.slider_image = None
        self.slider_handle_image = None
        self.slider_side = "right"  # or "left"

        self.slider_layout_props = {
            "name": "slider",
            "rect": [self.interior_padding + self.exterior_padding + self.viewable_content_width, self.exterior_padding, self.rect.width - 2 * self.exterior_padding - self.viewable_content_width - self.interior_padding, self.viewable_content_height],
            "min_value": 0,
            "max_value": 1,
            "bar_color": [0, 100, 0],
            "handle_color": [100, 0, 0],
            "handle_radius": 10,
            "direction": "vertical",
            "handle_shape": "stadium",
            "handle_length": 0
        }   

        self.create_surfaces()
        self.read_layout(layout_props)

    def create_surfaces(self):
        self.create_background_surface()
        self.create_content_surface()
        self.create_slider()

    def create_background_surface(self):
        self.background_surface = pygame.Surface((self.rect.width, self.rect.height))
        if self.background_image:
            self.background_surface.blit(self.background_image, (0, 0))
        else:
            self.background_surface.fill(self.background_color)

    def create_content_surface(self):
        self.content_surface = pygame.Surface((self.viewable_content_width, self.viewable_content_height))
        if self.content_background_image:
            self.content_surface.blit(self.content_background_image, (0, 0))
        else:
            self.content_surface.fill(self.content_background_color)

    def create_slider(self):
        self.slider = Slider(
            self.slider_layout_props,
            0,  # initial_value
            self.game_manager,
            bar_image=self.slider_image,
            handle_image=self.slider_handle_image
        )

    #called by slider to update content scroll, the area of the content surface to draw
    def set_content_scroll(self) -> None:
        #takes slider value (0 to 1) and sets content surface scroll accordingly
        self.content_scroll = self.slider.value * self.max_scroll

    #called on mouse drag
    def update_scroll(self, new_slider_y: int) -> None:
        self.slider.slider_position = self.slider.calculate_slider_position(new_slider_y)
        self.slider.value = self.slider.calculate_value()
        self.set_content_scroll()

    def draw(self, surface: pygame.Surface):
        if not self.shown:
            return
        
        # Draw background
        surface.blit(self.background_surface, (self.rect.x, self.rect.y))

        # Draw content area
        surface.blit(self.content_surface, (self.rect.x + self.exterior_padding, self.rect.y + self.exterior_padding), area=pygame.Rect(0, self.content_scroll, self.viewable_content_width, self.viewable_content_height))
        
        # Draw slider
        self.slider.draw(surface)

    def read_layout(self, layout_props: dict) -> None:
        self._read_common_layout(layout_props)

        self.slider_layout_props = layout_props.get("slider_layout_props", {})

        self.exterior_padding = layout_props.get("exterior_padding", self.exterior_padding)
        self.interior_padding = layout_props.get("interior_padding", self.interior_padding)

        self.viewable_content_height = layout_props.get("viewable_content_height", self.viewable_content_height)
        self.viewable_content_width = layout_props.get("viewable_content_width", self.viewable_content_width)

        background_color_data = layout_props.get("background_color", [self.background_color[0], self.background_color[1], self.background_color[2], self.background_color[3]])
        self.background_color = (background_color_data[0], background_color_data[1], background_color_data[2], background_color_data[3])
        
        content_background_color_data = layout_props.get("content_background_color", [self.content_background_color[0], self.content_background_color[1], self.content_background_color[2], self.content_background_color[3]])
        self.content_background_color = (content_background_color_data[0], content_background_color_data[1], content_background_color_data[2], content_background_color_data[3])
                
        self.slider_side = layout_props.get("slider_side", self.slider_side)
        #read slider bar layout props here if needed

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
            "slider_side": self.slider_side
        })
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

        