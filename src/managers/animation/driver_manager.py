import pygame
import math

from src.managers.game_manager import GameManager
from src.managers.graphics_manager import GraphicsManager
from src.managers.input.input_manager import InputManager
from src.ui.ui_element import UIElement
from .driver import AnimationDriver

class DriverManager:
    def __init__(self, game_manager: 'GameManager', input_manager: 'InputManager', graphics_manager: 'GraphicsManager') -> None:
        self.game_manager = game_manager
        self.input_manager = input_manager
        self.graphics_manager = graphics_manager
        
        self.driver_registry: list[AnimationDriver] = []
        # Stores the original (baseline) value per (element_id, property_path)
        # so additive drivers do not accumulate over time.
        self._baselines: dict[tuple[str, str], object] = {}

    def create_driver_registry(self) -> None:
        play_button_driver_x = AnimationDriver(
            value_function=lambda ctx: math.cos(ctx["time"] / 500) * 10,
            target_element_id="play",
            target_property="rect.x",
            blend_mode="add"
        )
        play_button_driver_y = AnimationDriver(
            value_function=lambda ctx: math.sin(ctx["time"] / 500) * 10,
            target_element_id="play",
            target_property="rect.y",
            blend_mode="add"
        )

        self.driver_registry = [play_button_driver_x, play_button_driver_y]

    def register_driver(self, driver: AnimationDriver) -> None:
        self.driver_registry.append(driver)

    def _get_time(self) -> int:
        if self.graphics_manager and hasattr(self.graphics_manager, "time"):
            return self.graphics_manager.time
        return pygame.time.get_ticks()

    def _collect_elements(self) -> dict[str, UIElement]:
        registry: dict[str, UIElement] = {}

        def add_elements(container: dict):
            for value in container.values():
                if isinstance(value, UIElement):
                    registry[value.name] = value
                elif isinstance(value, dict):
                    add_elements(value)

        add_elements(self.input_manager.buttons)
        add_elements(self.input_manager.sliders)
        add_elements(self.input_manager.toggles)
        add_elements(self.input_manager.images)
        add_elements(self.input_manager.text_displays)
        add_elements(self.input_manager.scrollable_areas)

        # menus are stored separately as Menu objects
        for menu in self.input_manager.menus.values():
            registry[menu.name] = menu

        return registry

    def _get_property(self, target: object, property_path: str):
        if not property_path:
            return None
        current = target
        for part in property_path.split("."):
            if not hasattr(current, part):
                return None
            current = getattr(current, part)
        return current

    def _set_property(self, target: object, property_path: str, value) -> None:
        if not property_path:
            return
        parts = property_path.split(".")
        current = target
        for part in parts[:-1]:
            if not hasattr(current, part):
                return
            current = getattr(current, part)
        if not hasattr(current, parts[-1]):
            return
        setattr(current, parts[-1], value)
        if property_path.startswith("rect.") and isinstance(target, UIElement):
            target._invalidate_absolute_rect()

    def evaluate_drivers(self):
        """
          Evaluate all registered drivers and apply chained results to targets.

          Pipeline:
          1) Build a registry of UI elements by name (for cross-element access).
          2) Build a per-frame context (time, managers, registry).
          3) Group drivers by (target_element_id, target_property).
          4) Sort each group by priority and chain results using each driver's
              blend mode (override/add/mul/lerp) against the current value.
          5) Apply the final value to the target property and invalidate caches
              if rect properties are changed.

          Notes:
          - Drivers with missing target metadata are skipped.
                    - Base value is a cached baseline (first-seen property value)
                        for each (element, property) pair. This prevents additive
                        drivers from integrating over time.
          - Each driver can use a custom `value_function(context)` for
             cross-element or time-dependent logic.
        """
        if not self.driver_registry:
            return

        registry = self._collect_elements()
        context = {
            "time": self._get_time(),
            "registry": registry,
            "game_manager": self.game_manager,
            "input_manager": self.input_manager,
            "graphics_manager": self.graphics_manager,
        }

        # Group drivers per target element/property
        grouped: dict[tuple[str, str], list[AnimationDriver]] = {}
        for driver in self.driver_registry:
            if not driver.target_element_id or not driver.target_property:
                continue
            key = (driver.target_element_id, driver.target_property)
            grouped.setdefault(key, []).append(driver)

        for (element_id, property_path), drivers in grouped.items():
            target = registry.get(element_id)
            if not target:
                continue

            drivers.sort(key=lambda d: d.priority)

            # Use a fixed baseline per (element, property) so that
            # additive drivers apply offsets from this original value
            # each frame instead of accumulating over time.
            key = (element_id, property_path)
            if key not in self._baselines:
                initial = self._get_property(target, property_path)
                if initial is None:
                    continue
                self._baselines[key] = initial

            base_value = self._baselines[key]
            current_value = base_value
            for driver in drivers:
                driver_value = driver.evaluate(context)
                if driver_value is None:
                    continue
                current_value = driver.blend(current_value, driver_value)

            if current_value != base_value:
                self._set_property(target, property_path, current_value)
    
    """
    def create_all_drivers(self) -> dict:
        return {
            "button": self.create_button_drivers(),
            "slider": self.create_slider_drivers(),
            "image": self.create_image_drivers(),
            "text_display": self.create_text_display_drivers(),
            "scrollable_area": self.create_scrollable_area_drivers(),
            "toggle": self.create_toggle_drivers()
        }
    
    def create_button_drivers(self) -> dict:
        return {}
    
    def create_slider_drivers(self) -> dict:
        return {}
    
    def create_image_drivers(self) -> dict:
        return {}
    
    def create_text_display_drivers(self) -> dict:
        return {}
    
    def create_scrollable_area_drivers(self) -> dict:
        return {}
    
    def create_toggle_drivers(self) -> dict:
        return {}
    
"""