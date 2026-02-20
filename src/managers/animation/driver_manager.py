import pygame
import math
from src.managers.base_manager import BaseManager

from src.managers.animation.animation_manager import AnimationManager
from src.managers.audio.audio_manager import AudioManager
from src.managers.game.game_manager import GameManager
from src.managers.graphics.graphics_manager import GraphicsManager
from src.managers.helper.helper_manager import HelperManager
from src.managers.input.input_manager import InputManager
from src.managers.player.player_manager import PlayerManager
from src.ui.ui_element import UIElement
from .driver import AnimationDriver

class DriverManager(BaseManager):
    def __init__(self) -> None:
        super().__init__()
        self.driver_registry: list[AnimationDriver] = []
        # Stores the original (baseline) value per (element_id, property_path)
        # so additive drivers do not accumulate over time.
        self._baselines: dict[tuple[str, str], object] = {}
        # Pre-grouped drivers per (element_id, property_path) to avoid
        # rebuilding this mapping every frame.
        self._groups: dict[tuple[str, str], list[AnimationDriver]] = {}
        # Cached UI element registry; built on first use.
        self._element_registry: dict[str, UIElement] = {}
        
    def initialize(self) -> None:
        """Initialize manager after all dependencies are injected."""
        self.input_manager = self.get_dependency('input_manager')
        self.audio_manager = self.get_dependency('audio_manager')
        self.graphics_manager = self.get_dependency('graphics_manager')
        self.helper_manager = self.get_dependency('helper_manager')
        self.player_manager = self.get_dependency('player_manager')
        self.animation_manager = self.get_dependency('animation_manager')
        self.game_manager = self.get_dependency('game_manager')
        """Inject GameManager dependency. Used for circular dependency resolution."""

    @property
    def drivers(self) -> dict:
        """
        Get drivers organized by element name for external access.
        
        Returns:
            dict: Drivers organized as {element_name: [driver1, driver2, ...]}
        """
        drivers_by_element = {}
        for driver in self.driver_registry:
            if driver.target_element_id:
                if driver.target_element_id not in drivers_by_element:
                    drivers_by_element[driver.target_element_id] = []
                drivers_by_element[driver.target_element_id].append(driver)
        return drivers_by_element

    def add_driver_for_element(self, element_name: str, driver) -> None:
        """
        Add a driver for a specific UI element from external code.
        
        Args:
            element_name: Name of the target UI element
            driver: AnimationDriver instance to add
        """
        driver.target_element_id = element_name
        self.register_driver(driver)

    def remove_drivers_for_element(self, element_name: str) -> None:
        """
        Remove all drivers targeting a specific UI element.
        
        Args:
            element_name: Name of the target UI element
        """
        self.driver_registry = [d for d in self.driver_registry if d.target_element_id != element_name]
        # Clear cached groups for this element
        keys_to_remove = [key for key in self._groups.keys() if key[0] == element_name]
        for key in keys_to_remove:
            del self._groups[key]
        # Clear cached baselines for this element
        baseline_keys_to_remove = [key for key in self._baselines.keys() if key[0] == element_name]
        for key in baseline_keys_to_remove:
            del self._baselines[key]

    def get_drivers_for_element(self, element_name: str) -> list:
        """
        Get all drivers targeting a specific UI element.
        
        Args:
            element_name: Name of the target UI element
            
        Returns:
            list: AnimationDriver instances targeting the element
        """
        return [d for d in self.driver_registry if d.target_element_id == element_name]

    def create_driver_registry(self) -> None:
        # Clear any existing drivers/groups before creating test drivers
        self.driver_registry = []
        self._groups.clear()

        """play_button_driver_x = AnimationDriver(
            value_function=lambda ctx: math.cos(ctx["time"] / 250) * 30,
            target_element_id="play",
            target_property="rect.x",
            blend_mode="add"
        )

        self.register_driver(play_button_driver_x)"""

    def register_driver(self, driver: AnimationDriver) -> None:
        self.driver_registry.append(driver)
        if driver.target_element_id and driver.target_property:
            key = (driver.target_element_id, driver.target_property)
            self._groups.setdefault(key, []).append(driver)

    def _get_time(self) -> int:
        if self.graphics_manager and hasattr(self.graphics_manager, "time"):
            return self.graphics_manager.time
        return pygame.time.get_ticks()

    def _collect_elements(self) -> dict[str, UIElement]:
        # Cache the element registry; UI is mostly static so we
        # avoid walking all containers every frame.
        if self._element_registry:
            return self._element_registry

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

        self._element_registry = registry
        return self._element_registry

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
        current_time = self._get_time()
        context = {
            "time": current_time,
            "registry": registry,
            "game_manager": self.game_manager,
            "input_manager": self.input_manager,
            "graphics_manager": self.graphics_manager,
        }

        # Use pre-grouped drivers per target element/property
        for (element_id, property_path), drivers in self._groups.items():
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
                current_value = driver.blend(current_value, driver_value) # type: ignore

            if current_value != base_value:
                self._set_property(target, property_path, current_value)