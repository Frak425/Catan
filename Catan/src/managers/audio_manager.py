import pygame
from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.managers.game_manager import GameManager
    from src.managers.input_manager import InputManager
    from src.managers.helper_manager import HelperManager
    from src.managers.player_manager import PlayerManager
    from src.managers.graphics_manager import GraphicsManager
    

class AudioManager:
    def init(self):
        pygame.mixer.init()

        self.sound_effects: dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: dict[str, pygame.mixer.Sound] = {}

        self.master_volume = 1.0
        self.music_volume = 1.0
        self.sfx_volume = 1.0
        self.ui_volume = 1.0
        self.muted = False

        #create channels for sound effects, music, and ui sounds
        self.channel_sfx = pygame.mixer.Channel(0)
        self.channel_music = pygame.mixer.Channel(1)
        self.channel_ui = pygame.mixer.Channel(2)

        self.load_assets(Path("assets/audio"))

    def load_assets(self, asset_path: Path):
        sfx_path = asset_path / "sfx"
        music_path = asset_path / "music"

        for sound_file in sfx_path.glob("*"):
            self.sound_effects[sound_file.stem] = pygame.mixer.Sound(sound_file)
            self.sound_effects[sound_file.stem].set_volume(self.sfx_volume)

        for music_file in music_path.glob("*"):
            self.music_tracks[music_file.stem] = pygame.mixer.Sound(music_file)
            self.music_tracks[music_file.stem].set_volume(self.music_volume)

    def play_music(self, name: str, loop=False, fade_ms=500):
        if name not in self.music_tracks:
            return

        self.channel_music.fadeout(fade_ms)
        self.channel_music.set_volume(self.music_volume if not self.muted else 0)
        self.channel_music.play(self.music_tracks[name], loops=-1 if loop else 0, fade_ms=fade_ms)

    def play_sound_effect(self, name: str):
        if name not in self.sound_effects:
            return

        self.channel_sfx.set_volume(self.sfx_volume if not self.muted else 0)
        self.channel_sfx.play(self.sound_effects[name])

    def play_ui_sound(self, name: str):
        if name not in self.sound_effects:
            return

        self.channel_ui.set_volume(self.ui_volume if not self.muted else 0)
        self.channel_ui.play(self.sound_effects[name])

    def toggle_mute(self):
        self.muted = not self.muted
        new_music_volume = 0 if self.muted else self.music_volume
        new_sfx_volume = 0 if self.muted else self.sfx_volume
        new_ui_volume = 0 if self.muted else self.ui_volume
        self.update_sound(self.master_volume, new_ui_volume, new_music_volume, new_sfx_volume)
        
    def update_sound(self, master_volume: float, ui_volume: float, music_volume: float, sfx_volume: float):
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