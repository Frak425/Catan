import pygame
import pytweening
import os
from src.managers.base_manager import BaseManager

from .animation import SpriteAnimation
from .driver import AnimationDriver

class AnimationManager(BaseManager):
    """
    Initializer and handler for loading and managing animations

    - Each ui element can have multiple sprite and driver animations

    Both SpriteAmination and Driver objects are of the form:
    {
        "target_element_id": {
            "target_1_attribute": AnimationDriver/SpriteAnimation,
            "target_2_attribute": AnimationDriver/SpriteAnimation,
            ...
        }
    }

    These objects will populate sprite animation and driver registries respective to their types
    All animations and drivers are hardcoded for now, but will be loaded from config files later
    TODO: create a serialization system for animations and drivers

    """
    def __init__(self):
        super().__init__()
        self.animations = {}
        
    def initialize(self) -> None:
        """Initialize manager after all dependencies are injected."""
        self.create_animation_drivers()
        self.create_sprite_animations()

    def create_sprite_animations(self):
        #test sprite animation for home screen image
        # Get the project root directory (3 levels up from this file)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        asset_path = os.path.join(project_root, "src", "assets", "Home Screen.png")
        self.home_screen = pygame.image.load(asset_path)
        self.home_screen_animation = SpriteAnimation(self.home_screen, 3, 2, 1)

        self.animations["sprite"] = {
            "main_menu_background": self.home_screen_animation
        }

    def create_animation_drivers(self):
        test_driver = AnimationDriver(tween_function="")
        self.animations["driver"] = {
            "target": [
                {
                    "play": test_driver
                }
            ]
        }



