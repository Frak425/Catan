from typing import Optional, Callable, Union
import pygame
import pytweening
import math

class AnimationDriver:
    """
    Driver for animations, similar to Blender drivers.

    Drives any animation based on given parameters to smoothly interpolate between values.
    Example: Animate a menu with ease-in-out when opening, transitioning from start to stop coordinates.

    Value animations:
    - Can be either sinusoidal, pytweening functions, or custom
    - If custom, user must provide function that takes in time (0-1) and outputs factor (0-1)
    - Tweens between start_value and stop_value
    - Periodic functions loop infinitely over the duration
    - Custom functions can be sinusoidal or tweening
    - If custom is sinusoidal, user must handle periodicity themselves to avoid discontinuities
    - Current value is accessed via .value attribute
    
    NOTE: All functions are parameterized between 0 and 1 over duration.
          Periodic functions reset after each cycle.
    
    Attributes:
        animating (bool): Whether the animation is currently running.
        periodic (bool): Whether the animation loops indefinitely.
        custom_function (func): Custom easing function.
        tween_function (str): Name of pytweening function to use.
        start_value: Starting value of the animation.
        stop_value: Ending value of the animation.
        duration (int): Duration of one animation cycle in milliseconds.
        start_time (int): Timestamp when animation started.
        value: Current interpolated value.
        paused_elapsed (int): Accumulated elapsed time before pause.
        on_complete (Callable[[], None]): Callback when animation completes.
    """

    def __init__(self, custom_function: Optional[Callable[[float], float]] = None, tween_function: Optional[str] = None, start_value: float = 0.0, stop_value: float = 1.0, duration: int = 1000, periodic: bool = False, on_complete: Optional[Callable[[], None]] = None) -> None:
        """
        Initialize an AnimationDriver.
        
        Args:
            custom_function: Custom easing function taking t (0-1) returning factor (0-1).
            tween_function: Name of pytweening function (e.g., 'easeInOutQuad').
            start_value: Starting value of the animation.
            stop_value: Ending value of the animation.
            duration: Duration of one cycle in milliseconds.
            periodic: If True, animation loops indefinitely.
            on_complete: Optional callback function called when non-periodic animation completes.
        """
        self.animating: bool = False
        self.periodic: bool = periodic
        
        self.custom_function: Optional[Callable[[float], float]] = custom_function
        self.tween_function: Optional[str] = tween_function
        self.start_value: float = start_value
        self.stop_value: float = stop_value
        self.duration: int = duration  # in milliseconds
        self.start_time: Optional[int] = None
        self.value: float = start_value
        self.paused_elapsed: int = 0  # Track elapsed time when paused
        self.on_complete: Optional[Callable[[], None]] = on_complete
        self._completed: bool = False  # Track if callback has been called

        
    def update(self, current_time: int) -> None:
        """
        Update the animation value based on current time.
        
        Args:
            current_time: Current timestamp in milliseconds (typically from pygame.time.get_ticks()).
        """
        if not self.animating or self.start_time is None:
            return
        
        # Calculate elapsed time, accounting for pause/resume
        elapsed_time = self.paused_elapsed + (current_time - self.start_time)
        
        # Handle periodic wrapping or clamping
        if self.periodic:
            elapsed_time %= self.duration
        
        t = min(elapsed_time / self.duration, 1.0)

        # Calculate easing factor based on function type
        if self.custom_function:
            factor = self.custom_function(t)
        elif self.tween_function:
            tween_func = getattr(pytweening, self.tween_function, None)
            if tween_func:
                factor = tween_func(t)
            else:
                print(f"AnimationDriver: Invalid tween function '{self.tween_function}'")
                factor = t
        else:
            # Default to linear interpolation
            factor = t

        # Interpolate between start and stop values
        self.value = self.start_value + factor * (self.stop_value - self.start_value)
        
        # Handle completion for non-periodic animations
        if t >= 1.0 and not self.periodic:
            self.animating = False
            if self.on_complete and not self._completed:
                self._completed = True
                self.on_complete()

    def start(self, current_time: int) -> None:
        """
        Start or restart the animation from the beginning.
        
        Args:
            current_time: Current timestamp in milliseconds.
        """
        self.start_time = current_time
        self.animating = True
        self.paused_elapsed = 0
        self._completed = False

    def stop(self) -> None:
        """
        Stop the animation immediately without triggering completion callback.
        """
        self.start_time = None
        self.animating = False
        self.paused_elapsed = 0

    def reset(self) -> None:
        """
        Reset the animation to its initial state.
        Sets value back to start_value and stops animation.
        """
        self.value = self.start_value
        self.animating = False
        self.start_time = None
        self.paused_elapsed = 0
        self._completed = False

    def pause(self, current_time: int) -> None:
        """
        Pause the animation, preserving current progress.
        
        Args:
            current_time: Current timestamp in milliseconds.
        """
        if self.animating and self.start_time is not None:
            self.paused_elapsed += (current_time - self.start_time)
            self.animating = False
            self.start_time = None

    def resume(self, current_time: int) -> None:
        """
        Resume a paused animation from where it left off.
        
        Args:
            current_time: Current timestamp in milliseconds.
        """
        if not self.animating and self.paused_elapsed > 0:
            self.start_time = current_time
            self.animating = True

    def is_complete(self, current_time: int) -> bool:
        """
        Check if the animation has completed.
        
        Args:
            current_time: Current timestamp in milliseconds.
            
        Returns:
            True if animation is complete, False otherwise.
            Periodic animations always return False.
        """
        if self.periodic:
            return False
        if self.start_time is None and self.paused_elapsed == 0:
            return True
        if not self.animating and self._completed:
            return True
        if self.start_time is not None:
            elapsed_time = self.paused_elapsed + (current_time - self.start_time)
            return elapsed_time >= self.duration
        return False
    
