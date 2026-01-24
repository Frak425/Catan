from typing import Optional, Callable, List
import pygame

class SpriteAnimation:
    """
    Handles sprite sheet animations for UI elements.
    
    Parses a sprite sheet into individual frames and animates through them
    at a specified speed. Supports looping, single-shot playback, and callbacks.
    
    Attributes:
        sprite_sheet (pygame.Surface): The sprite sheet image.
        rows (int): Number of rows in the sprite sheet.
        columns (int): Number of columns in the sprite sheet.
        speed (float): Animation speed in frames per second.
        frames (List[pygame.Surface]): List of individual frame surfaces.
        total_frames (int): Total number of frames in the animation.
        current_frame (int): Index of the current frame.
        animating (bool): Whether the animation is currently playing.
        loop (bool): Whether the animation should loop indefinitely.
        on_complete (Optional[Callable]): Callback when animation completes.
    """
    
    def __init__(self, sprite_sheet: pygame.Surface, rows: int, columns: int, speed: float, loop: bool = True, start_frame: int = 0, on_complete: Optional[Callable[[], None]] = None) -> None:
        """
        Initialize a SpriteAnimation.
        
        Args:
            sprite_sheet: The sprite sheet surface containing all frames.
            rows: Number of rows in the sprite sheet grid.
            columns: Number of columns in the sprite sheet grid.
            speed: Animation speed in frames per second.
            loop: If True, animation loops indefinitely. If False, plays once.
            start_frame: Frame index to start at (default 0).
            on_complete: Optional callback called when non-looping animation completes.
        """
        self.sprite_sheet: pygame.Surface = sprite_sheet
        self.rows: int = rows
        self.columns: int = columns
        self.speed: float = speed
        self.loop: bool = loop
        self.on_complete: Optional[Callable[[], None]] = on_complete

        self.total_frames: int = rows * columns
        self.current_frame: int = start_frame
        self.last_update_time: Optional[int] = None
        self.animating: bool = False
        self._completed: bool = False

        self.frame_width: int = sprite_sheet.get_width() // columns
        self.frame_height: int = sprite_sheet.get_height() // rows

        # Parse sprite sheet into individual frames
        self.frames: List[pygame.Surface] = []
        for row in range(rows):
            for col in range(columns):
                rect = pygame.Rect(
                    col * self.frame_width, 
                    row * self.frame_height, 
                    self.frame_width, 
                    self.frame_height
                )
                frame = sprite_sheet.subsurface(rect)
                self.frames.append(frame)

    def update(self, current_time: int) -> None:
        """
        Update the current frame based on elapsed time.
        
        Args:
            current_time: Current timestamp in milliseconds (from pygame.time.get_ticks()).
        """
        if not self.animating:
            return
        
        # Initialize timing on first update
        if self.last_update_time is None:
            self.last_update_time = current_time
            return
        
        # Calculate frame duration in milliseconds
        frame_duration = 1000 / self.speed
        
        if current_time - self.last_update_time >= frame_duration:
            self.current_frame += 1
            self.last_update_time = current_time
            
            # Handle loop/completion
            if self.current_frame >= self.total_frames:
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = self.total_frames - 1
                    self.animating = False
                    if self.on_complete and not self._completed:
                        self._completed = True
                        self.on_complete()

    def start(self, current_time: int) -> None:
        """
        Start the animation from the beginning.
        
        Args:
            current_time: Current timestamp in milliseconds.
        """
        self.current_frame = 0
        self.last_update_time = current_time
        self.animating = True
        self._completed = False

    def pause(self) -> None:
        """Pause the animation at the current frame."""
        self.animating = False

    def resume(self, current_time: int) -> None:
        """
        Resume the animation from where it was paused.
        
        Args:
            current_time: Current timestamp in milliseconds.
        """
        if not self.animating:
            self.last_update_time = current_time
            self.animating = True

    def stop(self) -> None:
        """Stop the animation and reset to first frame."""
        self.animating = False
        self.current_frame = 0
        self.last_update_time = None
        self._completed = False

    def reset(self) -> None:
        """Reset animation to initial state without changing play state."""
        self.current_frame = 0
        self.last_update_time = None
        self._completed = False

    def set_frame(self, frame_index: int) -> None:
        """
        Jump to a specific frame.
        
        Args:
            frame_index: Index of the frame to jump to (0 to total_frames-1).
        """
        if 0 <= frame_index < self.total_frames:
            self.current_frame = frame_index
        else:
            print(f"SpriteAnimation: Frame index {frame_index} out of range (0-{self.total_frames-1})")

    def get_current_frame(self) -> pygame.Surface:
        """
        Get the current frame surface.
        
        Returns:
            The pygame.Surface for the current frame.
        """
        return self.frames[self.current_frame]
    
    def is_complete(self) -> bool:
        """
        Check if the animation has completed.
        
        Returns:
            True if non-looping animation has finished, False otherwise.
            Looping animations always return False.
        """
        if self.loop:
            return False
        return not self.animating and self._completed

    def get_frame_count(self) -> int:
        """
        Get the total number of frames in the animation.
        
        Returns:
            Total frame count.
        """
        return self.total_frames