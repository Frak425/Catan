import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_manager import GameManager
    from graphics_manager import GraphicsManager
    from src.managers.audio_manager import AudioManager
    from src.managers.input.helper.mouse_input_handler import MouseInputHandler
    from src.managers.input.helper.dev_mode_handler import DevModeHandler


class KeyboardInputHandler:
    """
    Handles all keyboard input events including shortcuts and dev mode commands.
    
    Responsibilities:
    - Process pygame keyboard events (KEYDOWN)
    - Route global shortcuts (ESC, M for mute)
    - Toggle dev mode (0 key)
    - Handle dev mode typing mode for text commands
    - Arrow key navigation for dev mode repositioning
    - Save/restore config files in dev mode
    
    Key Bindings:
    Global (always active):
    - ESC: Close menu or exit typing mode
    - M: Toggle audio mute
    - 0: Toggle dev mode on/off
    
    Dev Mode Only:
    - T: Enter typing mode for commands
    - S: Save layout and settings configs
    - R: Restore configs from backup
    - Arrow keys: Move active UI element (1px per press)
    - RETURN: Submit typed command (in typing mode)
    - BACKSPACE: Delete last character (in typing mode)
    
    Architecture:
    - Priority: ESC → Typing mode → Global shortcuts → Dev mode commands
    - Typing mode captures all keys except ESC and RETURN
    - Dev mode commands require dev_mode=True to activate
    """
    game_manager: 'GameManager'
    graphics_manager: 'GraphicsManager'
    audio_manager: 'AudioManager'
    mouse_handler: 'MouseInputHandler'
    dev_mode_handler: 'DevModeHandler'  # Set after initialization to avoid circular import
    
    ## --- INITIALIZATION --- ##
    
    def __init__(self):
        """
        Initialize KeyboardInputHandler.
        
        Note: Manager references are set separately via set_managers() and
              set_dev_mode_handler() to avoid circular import issues.
        """
        pass  # All dependencies injected via setters

    ## --- DEPENDENCY INJECTION --- ##

    def set_managers(self, game_manager, graphics_manager, audio_manager, mouse_handler):
        """
        Set manager dependencies required for keyboard input handling.
        
        Args:
            game_manager: Central game state (dev_mode, dev_mode_typing, text buffer)
            graphics_manager: Graphics timing (currently unused by keyboard handler)
            audio_manager: Audio control (toggle_mute)
            mouse_handler: Mouse state access (active element for arrow key movement)
        
        Note: Must be called before handle_keyboard() to avoid AttributeError.
        """
        self.game_manager = game_manager
        self.graphics_manager = graphics_manager
        self.audio_manager = audio_manager
        self.mouse_handler = mouse_handler

    def set_dev_mode_handler(self, dev_mode_handler):
        """
        Set dev mode handler reference (called after DevModeHandler creation).
        
        Args:
            dev_mode_handler: Handler for dev mode text commands and special input
        
        Note: Set separately to break circular dependency:
              KeyboardInputHandler → DevModeHandler → KeyboardInputHandler
        """
        self.dev_mode_handler = dev_mode_handler

    ## --- EVENT HANDLING --- ##

    def handle_keyboard(self, key: int) -> None:
        """
        Main entry point for handling all keyboard events.
        
        Args:
            key: pygame key constant (pygame.K_*)
        
        Priority Order (highest to lowest):
        1. ESC: Always handled (close menu or exit typing mode)
        2. Typing mode: Captures all keys except ESC
        3. Global shortcuts: M (mute)
        4. Dev mode toggle: 0 key
        5. Dev mode commands: Arrow keys, S, R, T (requires dev_mode=True)
        
        Control Flow:
        - ESC → _handle_escape() → return
        - If typing mode → _handle_typing_mode() → return
        - M key → toggle mute (always available)
        - 0 key → toggle dev mode → return
        - If not dev mode → return (stop processing)
        - Arrow keys → move active element → return
        - S key → save configs → return
        - R key → restore configs → return
        - T key → enter typing mode → return
        """
        # Priority 1: Global ESC key (highest priority)
        if key == pygame.K_ESCAPE:
            self._handle_escape()
            return
        
        
        # Handle typing mode
        if self.game_manager.dev_mode_typing:
            self._handle_typing_mode(key)
            return
        
        #if not typing, handle other global keys
        if key == pygame.K_m:
            self.audio_manager.toggle_mute()

        # Toggle dev mode
        if key == pygame.K_0:
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
            return

        #restore configs
        if key == pygame.K_r:
            self.game_manager.restore_config("settings")
            self.game_manager.restore_config("layout")
            return



        # Start typing mode
        if key == pygame.K_t and not self.game_manager.dev_mode_typing:
            self.game_manager.dev_mode_typing = True
            self.game_manager.dev_mode_text = ""
            return


    ## --- GLOBAL SHORTCUTS --- ##

    def _handle_escape(self) -> None:
        """
        Handle escape key press - close menus or exit typing mode.
        
        Priority:
        1. If menus are open → close top menu
        2. Else if typing mode active → exit typing mode and clear buffer
        3. Else → no action
        
        Note: Menus checked via InputManager.get_open_menus() which returns
              list of currently open menus (can be multiple with different z-indices).
        """
        # Check if any menus are open by asking InputManager
        if hasattr(self.game_manager, 'input_manager') and self.game_manager.input_manager.get_open_menus():
            for menu in self.game_manager.input_manager.get_open_menus():
                menu.close()
        elif self.game_manager.dev_mode_typing:
            self.game_manager.dev_mode_typing = False
            self.game_manager.dev_mode_text = ""

    ## --- DEV MODE MANAGEMENT --- ##

    def _toggle_dev_mode(self) -> None:
        """
        Toggle dev mode on/off (triggered by 0 key).
        
        When Disabling Dev Mode:
        1. Clear active element selection
        2. Deactivate the previously active element
        3. Exit typing mode if active
        4. Clear text buffer
        
        When Enabling Dev Mode:
        - All UI elements become draggable
        - TextDisplay and Menu backgrounds become selectable
        - Arrow keys can move selected elements
        - Config save/restore commands available
        """
        self.game_manager.dev_mode = not self.game_manager.dev_mode

        # Clear active selection when exiting dev mode
        if not self.game_manager.dev_mode and self.mouse_handler.active:
            self.mouse_handler.active.is_active = False
            self.mouse_handler.active = None

        # Stop typing mode when toggling dev mode
        self.game_manager.dev_mode_typing = False
        self.game_manager.dev_mode_text = ""

    ## --- DEV MODE INPUT HANDLING --- ##

    def _handle_arrow_keys(self, key: int) -> bool:
        """
        Handle arrow key movement in dev mode for repositioning UI elements.
        
        Args:
            key: pygame key constant (pygame.K_UP, K_DOWN, K_LEFT, K_RIGHT)
        
        Returns:
            bool: True if an arrow key was handled, False otherwise
        
        Movement:
        - UP: Move element 1 pixel up (dy=-1)
        - DOWN: Move element 1 pixel down (dy=+1)
        - LEFT: Move element 1 pixel left (dx=-1)
        - RIGHT: Move element 1 pixel right (dx=+1)
        
        Note: Requires an active element selected via mouse click.
              Uses element.dev_mode_drag() to update position.
        """
        assert self.mouse_handler.active is not None
        
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
        """
        Handle keyboard input while in typing mode (activated by T key in dev mode).
        
        Args:
            key: pygame key constant
        
        Special Keys:
        - RETURN: Submit command to dev_mode_handler.parse_typing(), exit typing mode
        - BACKSPACE: Delete last character from text buffer
        - ESC: Handled before this method (exits typing mode without submission)
        
        Text Input:
        - Letters: Added via dev_mode_handler.add_letter_key()
        - Numbers: Added via dev_mode_handler.add_number_key()
        - Special chars: Added via dev_mode_handler.add_special_key()
        
        Text Buffer:
        - Stored in game_manager.dev_mode_text
        - Displayed on screen during typing mode
        - Cleared after command submission or ESC
        """
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

        # Shift-aware special handling
        # On many layouts, '_' is Shift + '-'. Pygame often reports this as
        # K_MINUS with shift in modifiers rather than K_UNDERSCORE.
        mods = pygame.key.get_mods()
        shift_held = bool(mods & pygame.KMOD_SHIFT)
        if shift_held and key == pygame.K_MINUS:
            self.game_manager.dev_mode_text += "_"
            return

        # Add characters to buffer (letters, numbers, special chars)
        if self.dev_mode_handler:
            self.dev_mode_handler.add_letter_key(key)
            self.dev_mode_handler.add_number_key(key)
            self.dev_mode_handler.add_special_key(key)

    ## --- MENU MANAGEMENT --- ##

    def _close_menu(self) -> None:
        """
        Close the currently open menu (called from ESC handler).
        
        TODO: This is currently a stub. Menu closing is handled by InputManager directly.
              This method may be deprecated and could be removed if InputManager handles
              ESC key menu closing through a different path.
        
        Expected Implementation:
        - Get top menu from InputManager.get_open_menus()
        - Call InputManager.close_menu() or menu.close()
        - Handle menu state cleanup
        
        Note: ESC handler checks for open menus and calls this, but actual closing
              may happen elsewhere in the codebase.
        """
        # This will be delegated from input_manager
        # We need access to the menu and buttons to properly close
        pass
