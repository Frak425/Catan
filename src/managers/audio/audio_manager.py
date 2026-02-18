import pygame
from pathlib import Path
from src.managers.base_manager import BaseManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.managers.game.game_manager import GameManager
    from src.managers.input.input_manager import InputManager
    from src.managers.helper.helper_manager import HelperManager
    from src.managers.player.player_manager import PlayerManager
    from src.managers.graphics.graphics_manager import GraphicsManager
    

class AudioManager(BaseManager):
    def __init__(self):
        super().__init__()
        
    def initialize(self) -> None:
        """Initialize manager after all dependencies are injected."""
        self.game_manager = self.get_dependency('game_manager')
        self.input_manager = self.get_dependency('input_manager')
        self.helper_manager = self.get_dependency('helper_manager')
        self.player_manager = self.get_dependency('player_manager')
        self.graphics_manager = self.get_dependency('graphics_manager')
        
    def init(self):
        pygame.mixer.init()

        self.sound_effects: dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: dict[str, pygame.mixer.Sound] = {}
        self.ui_effects: dict[str, pygame.mixer.Sound] = {}

        self.master_volume = 1.0
        self.music_volume = 1.0
        self.sfx_volume = 1.0
        self.ui_volume = 1.0
        self.muted = False

        #create channels for sound effects, music, and ui sounds
        self.channel_sfx = pygame.mixer.Channel(0)
        self.channel_music = pygame.mixer.Channel(1)
        self.channel_ui = pygame.mixer.Channel(2)

        self.fx_by_type = {
            "music": self.music_tracks,
            "ui": self.ui_effects,
            "sfx": self.sound_effects
        }

        self.channel_by_type = {
            "music": self.channel_music,
            "ui": self.channel_ui,
            "sfx": self.channel_sfx
        }

        self.volume_by_type = {
            "master": self.master_volume,
            "music": self.music_volume,
            "ui": self.ui_volume,
            "sfx": self.sfx_volume
        }
        self.load_assets(Path("assets/audio"))

    def load_assets(self, asset_path: Path):
        sfx_path = asset_path / "sfx"
        music_path = asset_path / "music"

        # Load sound effects and music tracks
        for sound_file in sfx_path.glob("*"):
            self.sound_effects[sound_file.stem] = pygame.mixer.Sound(sound_file)
            self.sound_effects[sound_file.stem].set_volume(self.sfx_volume)

        for music_file in music_path.glob("*"):
            self.music_tracks[music_file.stem] = pygame.mixer.Sound(music_file)
            self.music_tracks[music_file.stem].set_volume(self.music_volume)

    def play_sound(self, type: str, name: str, loop=False, fade_ms=500):
        if name not in self.fx_by_type[type]:
            return
        
        if type == "music":
            self.channel_music.fadeout(fade_ms)

        self.channel_by_type[type].set_volume(self.volume_by_type[type] if not self.muted else 0)
        self.channel_by_type[type].play(self.fx_by_type[type][name], loops=-1 if loop else 0, fade_ms=fade_ms)

    def toggle_mute(self):
        self.muted = not self.muted
        new_music_volume = 0 if self.muted else self.music_volume
        new_sfx_volume = 0 if self.muted else self.sfx_volume
        new_ui_volume = 0 if self.muted else self.ui_volume
        self.update_volumes(self.master_volume, new_ui_volume, new_music_volume, new_sfx_volume)
        
    def update_volumes(self, master_volume: float, ui_volume: float, music_volume: float, sfx_volume: float):
        #update music channel volume
        pygame.mixer.music.set_volume(master_volume)
        self.channel_music.set_volume(music_volume)
        self.channel_sfx.set_volume(sfx_volume)
        self.channel_ui.set_volume(ui_volume)

    def set_game_manager(self, game_manager: 'GameManager'):
        self.game_manager = game_manager 
    
    def set_input_manager(self, input_manager: 'InputManager'):
        self.input_manager = input_manager

    def set_helper_manager(self, helper_manager: 'HelperManager'):
        self.helper_manager = helper_manager

    def set_player_manager(self, player_manager: 'PlayerManager'):
        self.player_manager = player_manager

    def set_graphics_manager(self, graphics_manager: 'GraphicsManager'):
        self.graphics_manager = graphics_manager