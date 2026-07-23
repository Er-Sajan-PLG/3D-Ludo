"""
Configuration management for 3D Ludo.
This module handles game configuration, settings, and options.
"""

import json
import os
from typing import Dict, Any, Optional, List
class GameConfig:
    """
    Configuration for the 3D Ludo game.
    Manages game settings, options, and configuration files.
    """

    def __init__(self, config_file: str = 'config/game_config.json'):
        """
        Initialize game configuration.

        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.default_config = self._get_default_config()

        # Load configuration
        self.load_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default game configuration."""
        return {
            'game': {
                'title': '3D Ludo',
                'version': '1.0.0',
                'developer': '3D Ludo Team',
                'description': 'A simple and modular 3D Ludo game',
                'website': 'https://3dludo.example.com',
                'support_email': 'support@3dludo.example.com'
            },

            'graphics': {
                'renderer': 'opengl',
                'window_width': 1920,
                'window_height': 1080,
                'fullscreen': False,
                'vsync': True,
                'frame_rate': 60,
                'shadow_quality': 'high',
                'texture_quality': 'high',
                'particle_quality': 'high',
                'anti_aliasing': 'fxaa',
                'bloom': True,
                'tone_mapping': ' Reinhard'
            },

            'audio': {
                'enabled': True,
                'volume': 0.7,
                'music_volume': 0.5,
                'sound_effects_volume': 0.8,
                'master_volume': 1.0,
                'audio_api': 'pygame',
                'output_device': 'default',
                'format': 'pcm',
                'channels': 2,
                'sample_rate': 44100
            },

            'input': {
                'mouse_sensitivity': 1.0,
                'keyboard_layout': 'qwerty',
                'controller_enabled': True,
                'controller_deadzone': 0.2,
                'virtual_joystick': False,
                'camera_sensitivity': 1.0
            },

            'gameplay': {
                'board_type': 'classic',
                'board_size': 'standard',
                'num_players': 4,
                'time_per_turn': 30,  # seconds
                'starting_pieces': 4,
                'allow_jumping': False,
                'safe_zones_enabled': True,
                'capture_rules': 'normal',  # normal, aggressive, no_capture
                'dice_type': 'classic',  # classic, power, lucky, magic
                'require_login': True,
                'multiplayer_enabled': True,
                'lobby_timeout': 60,  # seconds
                'game_timeout': 0  # 0 means no timeout
            },

            'sound_system': {
                'enabled': True,
                'music_tracks': [],
                'sound_effects': [],
                'ambience_tracks': [],
                'spatial_audio': False,
                'reverb_enabled': False,
                'audio_compression': 'mp3'
            },

            'animation_system': {
                'enabled': True,
                'animation_speed': 1.0,
                'particle_system_enabled': True,
                'particle_quality': 'medium',
                'max_animations': 20,
                'animation_cleanup_interval': 5.0
            },

            'ui_system': {
                'enabled': True,
                'theme': 'light',
                'font_size_multiplier': 1.0,
                'animation_speed': 1.0,
                'screen_width': 1920,
                'screen_height': 1080,
                'sound_enabled': True
            },

            'game_modes': {
                'enabled': True,
                'initial_mode': 'classic',
                'available_modes': ['classic', 'speed', 'reverse', 'team', 'cooperative', 'battle_royale', 'time_attack', 'match_stops']
            },

            'login_system': {
                'enabled': True,
                'require_login': True,
                'providers': ['local'],
                'session_duration': 86400,  # 24 hours
                'max_failed_login_attempts': 5,
                'account_lockout_duration': 3600,  # 1 hour
                'session_cleanup_interval': 3600,
                'password_reset_cleanup_interval': 86400,
                'require_email_verification': False
            },

            'microtransactions': {
                'enabled': True,
                'payment_provider': 'stripe',
                'currencies_enabled': ['coins', 'gems', 'diamonds', 'renown'],
                'taxes_enabled': True,
                'tax_rate': 0.1
            },

            'data': {
                'data_directory': 'data',
                'save_directory': 'saves',
                'backup_directory': 'backups',
                'auto_save_interval': 300,  # 5 minutes
                'max_save_files': 10
            },

            'debug': {
                'enabled': False,
                'log_level': 'INFO',
                'show_fps': True,
                'show_debug_info': True,
                'profile_performance': False,
                'visualize_colliders': False,
                'test_mode': False
            },

            'development': {
                'hot_reload': False,
                'debug_mode': True,
                'live_reload': False,
                'watch_assets': True,
                'compile_on_startup': True
            }
        }

    def load_config(self) -> bool:
        """
        Load configuration from file.

        Returns:
            True if configuration loaded successfully, False otherwise
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                # Use default configuration
                self.config = self.default_config.copy()
                self.save_config()

            return True

        except Exception as e:
            print(f"Error loading config: {e}")
            # Fall back to default configuration
            self.config = self.default_config.copy()
            return False

    def save_config(self) -> bool:
        """
        Save configuration to file.

        Returns:
            True if configuration saved successfully, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)

            return True

        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Value to set

        Returns:
            True if set successfully, False otherwise
        """
        try:
            keys = key.split('.')
            config = self.config

            # Navigate to the right position
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]

            # Set the value
            config[keys[-1]] = value

            # Save configuration
            self.save_config()

            return True

        except Exception as e:
            print(f"Error setting config: {e}")
            return False

    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to defaults.

        Returns:
            True if reset successfully, False otherwise
        """
        self.config = self.default_config.copy()
        return self.save_config()

    def get_game_config(self) -> Dict[str, Any]:
        """Get game configuration."""
        return self.get('game', {})

    def get_graphics_config(self) -> Dict[str, Any]:
        """Get graphics configuration."""
        return self.get('graphics', {})

    def get_audio_config(self) -> Dict[str, Any]:
        """Get audio configuration."""
        return self.get('audio', {})

    def get_input_config(self) -> Dict[str, Any]:
        """Get input configuration."""
        return self.get('input', {})

    def get_gameplay_config(self) -> Dict[str, Any]:
        """Get gameplay configuration."""
        return self.get('gameplay', {})

    def get_sound_system_config(self) -> Dict[str, Any]:
        """Get sound system configuration."""
        return self.get('sound_system', {})

    def get_animation_system_config(self) -> Dict[str, Any]:
        """Get animation system configuration."""
        return self.get('animation_system', {})

    def get_ui_system_config(self) -> Dict[str, Any]:
        """Get UI system configuration."""
        return self.get('ui_system', {})

    def get_game_modes_config(self) -> Dict[str, Any]:
        """Get game modes configuration."""
        return self.get('game_modes', {})

    def get_login_system_config(self) -> Dict[str, Any]:
        """Get login system configuration."""
        return self.get('login_system', {})

    def get_microtransactions_config(self) -> Dict[str, Any]:
        """Get microtransactions configuration."""
        return self.get('microtransactions', {})

    def get_data_config(self) -> Dict[str, Any]:
        """Get data configuration."""
        return self.get('data', {})

    def get_debug_config(self) -> Dict[str, Any]:
        """Get debug configuration."""
        return self.get('debug', {})

    def get_development_config(self) -> Dict[str, Any]:
        """Get development configuration."""
        return self.get('development', {})

    def validate_config(self) -> List[str]:
        """
        Validate configuration.

        Returns:
            List of error messages (empty if config is valid)
        """
        errors = []

        # Check required sections
        required_sections = ['game', 'graphics', 'audio', 'input', 'gameplay']
        for section in required_sections:
            if section not in self.config:
                errors.append(f"Missing required section: {section}")

        # Validate graphics settings
        graphics_config = self.get_graphics_config()
        if graphics_config.get('window_width', 1920) <= 0:
            errors.append("Window width must be positive")

        if graphics_config.get('window_height', 1080) <= 0:
            errors.append("Window height must be positive")

        # Validate audio settings
        audio_config = self.get_audio_config()
        volume = audio_config.get('volume', 0.7)
        if not (0.0 <= volume <= 1.0):
            errors.append("Audio volume must be between 0.0 and 1.0")

        # Validate gameplay settings
        gameplay_config = self.get_gameplay_config()
        num_players = gameplay_config.get('num_players', 4)
        if not (1 <= num_players <= 8):
            errors.append("Number of players must be between 1 and 8")

        return errors

    def export_config(self) -> Dict[str, Any]:
        """
        Export full configuration.

        Returns:
            Dictionary with full configuration
        """
        return self.config.copy()

    def import_config(self, config: Dict[str, Any]) -> bool:
        """
        Import configuration from dictionary.

        Args:
            config: Configuration dictionary

        Returns:
            True if imported successfully, False otherwise
        """
        try:
            self.config = config.copy()
            return self.save_config()
        except Exception as e:
            print(f"Error importing config: {e}")
            return False

    def __str__(self) -> str:
        """String representation of configuration."""
        return f"GameConfig(file='{self.config_file}', sections={len(self.config)})"

    def __repr__(self) -> str:
        """Representation of configuration."""
        return self.__str__()
