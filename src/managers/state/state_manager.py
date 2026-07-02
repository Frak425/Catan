import pygame

from src.managers.base_manager import BaseManager

class StateManager(BaseManager):
    def __init__(self):
        super().__init__()
        self.state = None

    def import_dependencies(self) -> None:
        """Initialize manager after all dependencies are injected."""
        self.game_manager = self.get_dependency('game_manager')
        self.input_manager = self.get_dependency('input_manager')
        self.helper_manager = self.get_dependency('helper_manager')
        self.audio_manager = self.get_dependency('audio_manager')
        self.graphics_manager = self.get_dependency('graphics_manager')

    def change_state(self, new_state):
        if self.state is not None:
            self.state.exit()
        self.state = new_state
        self.state.enter()