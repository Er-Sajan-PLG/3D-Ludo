"""
Sound system for 3D Ludo (migrated into engine.systems).

This is a direct copy of `core/sound_system.py` to be used as the new
implementation location during migration.
"""
try:
    import pygame
except Exception:
    # Minimal pygame fallback for headless/testing environments
    class _DummyMixer:
        def init(self, *a, **kw):
            pass
        def quit(self):
            pass
        class music:
            @staticmethod
            def load(path):
                pass
            @staticmethod
            def play(arg=None):
                pass
            @staticmethod
            def stop():
                pass
            @staticmethod
            def set_volume(v):
                pass
            @staticmethod
            def get_busy():
                return False
            @staticmethod
            def pause():
                pass
            @staticmethod
            def unpause():
                pass
        @staticmethod
        def Sound(path):
            class _S:
                def __init__(self, p):
                    pass
                def play(self, *a, **kw):
                    pass
                def stop(self):
                    pass
                def set_volume(self, v):
                    pass
                def get_num_channels(self):
                    return 0
            return _S(path)

    class _DummyPygame:
        mixer = _DummyMixer()
        class error(Exception):
            pass

    pygame = _DummyPygame()

import threading
import time
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import os
class SoundType(Enum):
    EFFECT = "effect"
    MUSIC = "music"
    AMBIENCE = "ambience"
    VOICE = "voice"
class SoundSystem:
    """
    Sound system for 3D Ludo.
    Handles audio playback, sound effects, and background music.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the sound system with configuration.

        Args:
            config: Sound configuration dictionary
        """
        self.config = config
        self.is_enabled = config.get('enabled', True)
        self.volume = config.get('volume', 0.7)
        self.music_volume = config.get('music_volume', 0.5)
        self.sound_effects_volume = config.get('sound_effects_volume', 0.8)


        # Audio channels: try to initialize mixer; if unavailable, disable sound
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception as e:
            print(f"Warning: mixer module not available ({e}) — disabling sound")
            self.is_enabled = False
            # Create empty containers to avoid attribute errors later
            self.sound_effects: Dict[str, Any] = {}
            self.music_tracks: Dict[str, str] = {}
            self.ambience_tracks: Dict[str, str] = {}
            self.current_music = None
            self.current_ambience = None
            self.is_music_playing = False
            self.is_ambience_playing = False
            # Skip loading configuration when mixer isn't available
            return

        # Sound libraries
        self.sound_effects: Dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: Dict[str, str] = {}
        self.ambience_tracks: Dict[str, str] = {}

        # Playback state
        self.current_music: Optional[str] = None
        self.current_ambience: Optional[str] = None
        self.is_music_playing = False
        self.is_ambience_playing = False
        self.playlist: List[str] = []
        self.playlist_index = 0
        self.shuffle_playlist = config.get('shuffle_playlist', False)
        self.repeat_playlist = config.get('repeat_playlist', True)

        # Load sound configuration
        self._load_sound_configuration()

    def _load_sound_configuration(self) -> None:
        """Load sound configuration from files."""
        # Sound effects configuration
        sound_effects_config = self.config.get('sound_effects', {})

        # Load sound effects
        effects_dir = sound_effects_config.get('directory', 'assets/sounds/effects')
        if os.path.exists(effects_dir):
            for filename in os.listdir(effects_dir):
                if filename.endswith(('.wav', '.mp3', '.ogg')):
                    sound_name = os.path.splitext(filename)[0]
                    sound_path = os.path.join(effects_dir, filename)
                    try:
                        sound = pygame.mixer.Sound(sound_path)
                        sound.set_volume(self.sound_effects_volume)
                        self.sound_effects[sound_name] = sound
                    except pygame.error as e:
                        print(f"Error loading sound {sound_name}: {e}")

        # Music tracks configuration
        music_config = self.config.get('music', {})
        music_dir = music_config.get('directory', 'assets/sounds/music')
        if os.path.exists(music_dir):
            for filename in os.listdir(music_dir):
                if filename.endswith(('.wav', '.mp3', '.ogg')):
                    track_name = os.path.splitext(filename)[0]
                    track_path = os.path.join(music_dir, filename)
                    self.music_tracks[track_name] = track_path

        # Ambience tracks configuration
        ambience_config = self.config.get('ambience', {})
        ambience_dir = ambience_config.get('directory', 'assets/sounds/ambience')
        if os.path.exists(ambience_dir):
            for filename in os.listdir(ambience_dir):
                if filename.endswith(('.wav', '.mp3', '.ogg')):
                    track_name = os.path.splitext(filename)[0]
                    track_path = os.path.join(ambience_dir, filename)
                    self.ambience_tracks[track_name] = track_path

    def play_sound(self, sound_name: str, volume: Optional[float] = None, loop: bool = False) -> bool:
        """Play a sound effect."""
        if not self.is_enabled:
            return False

        if sound_name not in self.sound_effects:
            print(f"Sound effect '{sound_name}' not found")
            return False

        try:
            sound = self.sound_effects[sound_name]
            sound_volume = volume if volume is not None else self.sound_effects_volume
            sound.set_volume(sound_volume)

            if loop:
                sound.play(-1)  # -1 means loop indefinitely
            else:
                sound.play()

            return True

        except pygame.error as e:
            print(f"Error playing sound '{sound_name}': {e}")
            return False

    def stop_sound(self, sound_name: str) -> bool:
        if sound_name not in self.sound_effects:
            return False

        try:
            self.sound_effects[sound_name].stop()
            return True
        except pygame.error:
            return False

    def play_music(self, track_name: str, volume: Optional[float] = None, loop: bool = True) -> bool:
        if not self.is_enabled:
            return False

        if track_name not in self.music_tracks:
            print(f"Music track '{track_name}' not found")
            return False

        try:
            pygame.mixer.music.stop()
            track_path = self.music_tracks[track_name]
            pygame.mixer.music.load(track_path)
            music_volume = volume if volume is not None else self.music_volume
            pygame.mixer.music.set_volume(music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
            self.current_music = track_name
            self.is_music_playing = True
            return True
        except pygame.error as e:
            print(f"Error playing music '{track_name}': {e}")
            return False

    def stop_music(self) -> bool:
        if not self.is_enabled:
            self.is_music_playing = False
            return False

        try:
            pygame.mixer.music.stop()
            self.is_music_playing = False
            return True
        except Exception:
            self.is_music_playing = False
            return False

    def pause_music(self) -> bool:
        if not self.is_enabled:
            return False

        try:
            pygame.mixer.music.pause()
            return True
        except Exception:
            return False

    def resume_music(self) -> bool:
        if not self.is_enabled:
            return False

        try:
            pygame.mixer.music.unpause()
            return True
        except Exception:
            return False

    def play_ambience(self, track_name: str, volume: Optional[float] = None, loop: bool = True) -> bool:
        if not self.is_enabled:
            return False

        if track_name not in self.ambience_tracks:
            print(f"Ambience track '{track_name}' not found")
            return False

        try:
            if self.current_ambience:
                self.stop_ambience()

            track_path = self.ambience_tracks[track_name]
            ambience_sound = pygame.mixer.Sound(track_path)
            ambience_volume = volume if volume is not None else self.music_volume
            ambience_sound.set_volume(ambience_volume)

            if loop:
                self.current_ambience_source = ambience_sound
                self.current_ambience_source.play(-1)
            else:
                self.current_ambience_source = ambience_sound
                self.current_ambience_source.play()

            self.current_ambience = track_name
            self.is_ambience_playing = True

            return True

        except pygame.error as e:
            print(f"Error playing ambience '{track_name}': {e}")
            return False

    def stop_ambience(self) -> bool:
        try:
            if hasattr(self, 'current_ambience_source'):
                self.current_ambience_source.stop()
            self.is_ambience_playing = False
            return True
        except pygame.error:
            return False

    def set_volume(self, volume: float) -> None:
        self.volume = max(0.0, min(1.0, volume))
        self.sound_effects_volume = self.volume * 0.9
        self.music_volume = self.volume * 0.7

        for sound in self.sound_effects.values():
            try:
                sound.set_volume(self.sound_effects_volume)
            except Exception:
                pass

        if self.is_enabled:
            try:
                pygame.mixer.music.set_volume(self.music_volume)
            except Exception:
                pass

    def cleanup(self) -> None:
        """Cleanup sound system resources."""
        try:
            if self.is_enabled:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception:
            pass
        self.sound_effects.clear()
        self.music_tracks.clear()
        self.ambience_tracks.clear()
        self.current_music = None
        self.current_ambience = None
        self.is_music_playing = False
        self.is_ambience_playing = False
