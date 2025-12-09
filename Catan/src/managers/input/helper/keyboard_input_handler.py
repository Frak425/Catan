import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_manager import GameManager
    from graphics_manager import GraphicsManager
    from src.managers.audio_manager import AudioManager
    from src.managers.input.helper.mouse_input_handler import MouseInputHandler
    from src.managers.input.helper.dev_mode_handler import DevModeHandler


class KeyboardInputHandler:
    """Handles all keyboard input events."""
    game_manager: 'GameManager'
    graphics_manager: 'GraphicsManager'
    audio_manager: 'AudioManager'
    mouse_handler: 'MouseInputHandler'
    dev_mode_handler: 'DevModeHandler'  # Will be set later to avoid circular import
    
    def __init__(self):
        # Manager references (set after initialization)
        pass

    def set_managers(self, game_manager, graphics_manager, audio_manager, mouse_handler):
        """Set manager references."""
        self.game_manager = game_manager
        self.graphics_manager = graphics_manager
        self.audio_manager = audio_manager
        self.mouse_handler = mouse_handler

    def set_dev_mode_handler(self, dev_mode_handler):
        """Set dev mode handler reference."""
        self.dev_mode_handler = dev_mode_handler

    def handle_keyboard(self, key: int) -> None:
        """Main entry point for handling keyboard events."""
        # Global shortcuts
        if key == pygame.K_ESCAPE:
            self._handle_escape()
            return

        if key == pygame.K_m:
            self.audio_manager.toggle_mute()

        # Toggle dev mode (only when NOT typing)
        if not self.game_manager.dev_mode_typing and key == pygame.K_0:
            self._toggle_dev_mode()
            return

        # Dev mode only logic below this point
        if not self.game_manager.dev_mode:
            return

        # Move active object (arrow keys)
        if self.mouse_handler.active:
            if self._handle_arrow_keys(key):
                return

        # Save layout
        if key == pygame.K_s:
            self.game_manager.save_config("layout", False)
            self.game_manager.save_config("settings", False)

        #restore configs
        if key == pygame.K_r:
            self.game_manager.restore_config("settings")
            self.game_manager.restore_config("layout")



        # Start typing mode
        if key == pygame.K_t and not self.game_manager.dev_mode_typing:
            self.game_manager.dev_mode_typing = True
            self.game_manager.dev_mode_text = ""
            return

        # Handle typing mode
        if self.game_manager.dev_mode_typing:
            self._handle_typing_mode(key)

    def _handle_escape(self) -> None:
        """Handle escape key press."""
        if self.graphics_manager.menu_open:
            self._close_menu()
        elif self.game_manager.dev_mode_typing:
            self.game_manager.dev_mode_typing = False
            self.game_manager.dev_mode_text = ""

    def _toggle_dev_mode(self) -> None:
        """Toggle dev mode on/off."""
        self.game_manager.dev_mode = not self.game_manager.dev_mode

        # Clear active selection
        if not self.game_manager.dev_mode and self.mouse_handler.active:
            self.mouse_handler.active.is_active = False
            self.mouse_handler.active = None

        # Stop typing mode
        self.game_manager.dev_mode_typing = False
        self.game_manager.dev_mode_text = ""

    def _handle_arrow_keys(self, key: int) -> bool:
        assert self.mouse_handler.active is not None
        """Handle arrow key movement in dev mode. Returns True if handled."""
        if key == pygame.K_UP:
            self.mouse_handler.active.dev_mode_drag(0, -1)
            return True
        if key == pygame.K_DOWN:
            self.mouse_handler.active.dev_mode_drag(0, 1)
            return True
        if key == pygame.K_LEFT:
            self.mouse_handler.active.dev_mode_drag(-1, 0)
            return True
        if key == pygame.K_RIGHT:
            self.mouse_handler.active.dev_mode_drag(1, 0)
            return True
        return False

    def _handle_typing_mode(self, key: int) -> None:
        """Handle keyboard input while in typing mode."""
        # Submit command
        if key == pygame.K_RETURN:
            if self.dev_mode_handler:
                self.dev_mode_handler.parse_typing()
            self.game_manager.dev_mode_typing = False
            self.game_manager.dev_mode_text = ""
            return

        # Backspace
        if key == pygame.K_BACKSPACE:
            self.game_manager.dev_mode_text = self.game_manager.dev_mode_text[:-1]
            return

        # Otherwise add characters
        if self.dev_mode_handler:
            self.dev_mode_handler.add_letter_key(key)
            self.dev_mode_handler.add_number_key(key)

    def _close_menu(self) -> None:
        """Close the menu (called from escape handler)."""
        # This will be delegated from input_manager
        # We need access to the menu and buttons to properly close
        pass
