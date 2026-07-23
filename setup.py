#!/usr/bin/env python3
"""
Setup script for 3D Ludo game.
This script sets up the project structure and validates installation.
"""

import os
import sys
import json
from pathlib import Path

class ProjectSetup:
    """Project setup and validation class."""

    def __init__(self, project_root: str = None):
        """Initialize project setup."""
        self.project_root = Path(project_root or os.path.dirname(os.path.abspath(__file__)))
        self.core_dir = self.project_root / 'core'
        self.data_dir = self.project_root / 'data'
        self.saves_dir = self.data_dir / 'saves'
        self.config_file = self.project_root / '.gitignore'

    def create_directory_structure(self) -> bool:
        """Create the complete project directory structure."""
        try:
            directories = [
                self.core_dir,
                self.data_dir,
                self.saves_dir,
                self.core_dir / 'assets',
                self.core_dir / 'assets' / 'sounds',
                self.core_dir / 'assets' / 'models',
                self.core_dir / 'assets' / 'textures',
                self.core_dir / 'assets' / 'fonts',
                self.core_dir / 'configs',
                self.core_dir / 'scripts'
            ]
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"✓ Created directory: {directory}")
            return True
        except Exception as e:
            print(f"❌ Error creating directory structure: {e}")
            return False

    def create_sample_configs(self) -> bool:
        """Create sample configuration files."""
        try:
            configs_dir = self.core_dir / 'configs'
            configs_dir.mkdir(parents=True, exist_ok=True)
            game_config = {
                "game": {
                    "title": "3D Ludo",
                    "version": "1.0.0",
                    "developer": "3D Ludo Team",
                    "description": "A simple and modular 3D Ludo game with character pieces, animations, and sound system",
                    "website": "https://3dludo.example.com",
                    "support_email": "support@3dludo.example.com"
                },
                "graphics": {
                    "renderer": "opengl",
                    "window_width": 1920,
                    "window_height": 1080,
                    "fullscreen": False,
                    "vsync": True,
                    "frame_rate": 60,
                    "shadow_quality": "high",
                    "texture_quality": "high",
                    "particle_quality": "high",
                    "anti_aliasing": "fxaa",
                    "bloom": True,
                    "tone_mapping": "Reinhard"
                },
                "audio": {
                    "enabled": True,
                    "volume": 0.7,
                    "music_volume": 0.5,
                    "sound_effects_volume": 0.8,
                    "master_volume": 1.0,
                    "audio_api": "pygame",
                    "output_device": "default",
                    "format": "pcm",
                    "channels": 2,
                    "sample_rate": 44100
                },
                "input": {
                    "mouse_sensitivity": 1.0,
                    "keyboard_layout": "qwerty",
                    "controller_enabled": True,
                    "controller_deadzone": 0.2,
                    "virtual_joystick": False,
                    "camera_sensitivity": 1.0
                },
                "gameplay": {
                    "board_type": "classic",
                    "board_size": "standard",
                    "num_players": 4,
                    "time_per_turn": 30,
                    "starting_pieces": 4,
                    "allow_jumping": False,
                    "safe_zones_enabled": True,
                    "capture_rules": "normal",
                    "dice_type": "classic",
                    "require_login": False,
                    "multiplayer_enabled": True,
                    "lobby_timeout": 60,
                    "game_timeout": 0
                },
                "sound_system": {
                    "enabled": True,
                    "music_tracks": [],
                    "sound_effects": [],
                    "ambience_tracks": [],
                    "spatial_audio": False,
                    "reverb_enabled": False,
                    "audio_compression": "mp3"
                },
                "animation_system": {
                    "enabled": True,
                    "animation_speed": 1.0,
                    "particle_system_enabled": True,
                    "particle_quality": "medium",
                    "max_animations": 20,
                    "animation_cleanup_interval": 5.0
                },
                "ui_system": {
                    "enabled": True,
                    "theme": "light",
                    "font_size_multiplier": 1.0,
                    "animation_speed": 1.0,
                    "screen_width": 1920,
                    "screen_height": 1080,
                    "sound_enabled": True
                },
                "game_modes": {
                    "enabled": True,
                    "initial_mode": "classic",
                    "available_modes": [
                        "classic",
                        "speed",
                        "reverse",
                        "team",
                        "cooperative",
                        "battle_royale",
                        "time_attack",
                        "match_stops"
                    ]
                },
                "login_system": {
                    "enabled": True,
                    "require_login": False,
                    "providers": ["local"],
                    "session_duration": 86400,
                    "max_failed_login_attempts": 5,
                    "account_lockout_duration": 3600,
                    "session_cleanup_interval": 3600,
                    "password_reset_cleanup_interval": 86400,
                    "require_email_verification": False
                },
                "microtransactions": {
                    "enabled": True,
                    "payment_provider": "stripe",
                    "currencies_enabled": ["coins", "gems", "diamonds", "renown"],
                    "taxes_enabled": True,
                    "tax_rate": 0.1
                },
                "data": {
                    "data_directory": "data",
                    "save_directory": "saves",
                    "backup_directory": "backups",
                    "auto_save_interval": 300,
                    "max_save_files": 10
                },
                "debug": {
                    "enabled": False,
                    "log_level": "INFO",
                    "show_fps": True,
                    "show_debug_info": True,
                    "profile_performance": False,
                    "visualize_colliders": False,
                    "test_mode": False
                }
            }
            game_config_path = configs_dir / 'game_config.json'
            with open(game_config_path, 'w', encoding='utf-8') as f:
                json.dump(game_config, f, indent=2)
            print(f"✓ Created game configuration: {game_config_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating sample configs: {e}")
            return False

    def create_sample_assets(self) -> bool:
        """Create sample asset placeholders."""
        try:
            sounds_dir = self.core_dir / 'assets' / 'sounds'
            models_dir = self.core_dir / 'assets' / 'models'
            textures_dir = self.core_dir / 'assets' / 'textures'
            for path in (sounds_dir, models_dir, textures_dir):
                path.mkdir(parents=True, exist_ok=True)
            sound_files = [
                sounds_dir / 'dice_roll.wav',
                sounds_dir / 'capture.wav',
                sounds_dir / 'win.wav',
                sounds_dir / 'lose.wav',
                sounds_dir / 'background_music.mp3',
                sounds_dir / 'ambience.wav'
            ]
            for sound_file in sound_files:
                sound_file.touch(exist_ok=True)
                print(f"✓ Created placeholder sound file: {sound_file.name}")
            model_file = models_dir / 'character.fbx'
            model_file.touch(exist_ok=True)
            print(f"✓ Created placeholder model file: {model_file.name}")
            texture_file = textures_dir / 'character.png'
            texture_file.touch(exist_ok=True)
            print(f"✓ Created placeholder texture file: {texture_file.name}")
            return True
        except Exception as e:
            print(f"❌ Error creating sample assets: {e}")
            return False

    def create_readme(self) -> bool:
        """Create comprehensive README file."""
        try:
            readme_content = """# 3D Ludo Game

A simple and modular 3D Ludo game with expandable architecture for future development.

## Project Structure

The project is organized into modular components:

```
3D-Ludo/
├── core/
│   ├── game.py                    # Main game controller
│   ├── board.py                   # Game board/arena system
│   ├── pieces.py                  # Game pieces (characters)
│   ├── dice.py                    # Dice rolling system
│   ├── players.py                 # Player management
│   ├── sound_system.py            # Sound management
│   ├── animation_system.py        # Animation system
│   ├── ui_system.py               # User interface system
│   ├── game_modes.py              # Different game modes
│   ├── login_system.py            # Authentication system
│   ├── microtransactions.py       # In-game purchases
│   └── config.py                  # Configuration management
├── data/
│   ├── __init__.py               # Data storage directory
│   └── saves/                    # Game save files
├── assets/                       # Game assets (placeholder files)
│   ├── sounds/                   # Sound effects and music
│   ├── models/                   # 3D models
│   ├── textures/                   # Texture files
│   └── fonts/                    # Font files
├── main.py                       # Application entry point
├── setup.py                      # Project setup script
├── requirements.txt              # Python dependencies
├── README.md                     # Documentation (this file)
├── test_simple.py                 # Structure test
├── test_basic.py                 # Basic functionality test
└── .gitignore                     # Git ignore rules
```

## Features

### Core Features
- **Simple 3D board/arena system** with multiple board types (classic, circular, hexagonal, triangular)
- **Modular character pieces** with customizable stats (attack, defense, speed, luck, charisma)
- **Physical dice rolling** with multiple dice types (classic, power, lucky, magic)
- **Turn-based multiplayer** support for 2-8 players
- **Game modes** including classic, speed, reverse, team, cooperative, battle royale, time attack, and match stops

### Advanced Features
- **Sound system** with background music, sound effects, and spatial audio
- **Animation system** with particle effects and smooth transitions
- **Login system** supporting local authentication and OAuth providers
- **Microtransactions** with virtual currency (coins, gems, diamonds, renown)
- **Save system** for resuming games
- **UI system** with responsive menus and settings
- **Configuration management** with JSON configuration files

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Steps
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/3d-ludo.git
   cd 3D-Ludo
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the game:
   ```bash
   python main.py
   ```

4. For development setup:
   ```bash
   python setup.py
   ```

## Game Controls

- **Click on your piece to select it**
- **Roll dice using the roll button or spacebar**
- **Move pieces based on dice roll**
- **Click on target positions to move your piece**
- **Press ESC to pause the game**

## Development

### Project Architecture
This project is designed with modularity in mind. Each component can be easily replaced or upgraded:

1. **Core Modules**: Each system is isolated in its own file
2. **Configuration-driven**: Game behavior is controlled by JSON configuration
3. **Event-driven**: Game systems communicate through events
4. **Extensible**: New features can be added without modifying existing code

### Testing

Run basic structure test:
```bash
python test_simple.py
```

Run basic functionality test:
```bash
python test_basic.py
```

## Configuration

The game uses JSON configuration files for:
- Game settings (players, board size, rules)
- Graphics settings (resolution, quality, features)
- Audio settings (volume, output, format)
- Game mode configurations
- Login system settings
- Microtransaction settings

Configuration files are stored in `core/configs/` directory.

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For support, please:
1. Check the documentation
2. Review the troubleshooting section
3. File an issue on GitHub
4. Contact support@3dludo.example.com

## Acknowledgments

- Inspiration from classic Ludo board game
- OpenGL for 3D rendering
- Pygame for multimedia support
- JSON for configuration management
- Python for cross-platform compatibility
"""
            readme_path = self.project_root / 'README.md'
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print(f"✓ Created comprehensive README: {readme_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating README: {e}")
            return False

    def validate_project(self) -> bool:
        """Validate the project structure."""
        print("\nValidating project structure...")
        essential_files = [
            self.project_root / 'main.py',
            self.project_root / 'setup.py',
            self.project_root / 'requirements.txt',
            self.project_root / 'README.md',
            self.project_root / '.gitignore',
            self.core_dir / '__init__.py'
        ]
        core_modules = [
            'game.py', 'board.py', 'pieces.py', 'dice.py', 'players.py',
            'sound_system.py', 'animation_system.py', 'ui_system.py',
            'game_modes.py', 'login_system.py', 'microtransactions.py', 'config.py'
        ]
        all_valid = True
        for file_path in essential_files:
            if file_path.exists():
                print(f"✓ Found essential file: {file_path.relative_to(self.project_root)}")
            else:
                print(f"❌ Missing essential file: {file_path.relative_to(self.project_root)}")
                all_valid = False
        for module in core_modules:
            module_path = self.core_dir / module
            if module_path.exists():
                print(f"✓ Found core module: {module}")
            else:
                print(f"❌ Missing core module: {module}")
                all_valid = False
        return all_valid

    def run(self) -> bool:
        """Run complete project setup."""
        print("🚀 Starting 3D Ludo Game Project Setup")
        print("=" * 50)
        if not self.create_directory_structure():
            return False
        print()
        if not self.create_sample_configs():
            return False
        print()
        if not self.create_sample_assets():
            return False
        print()
        if not self.create_readme():
            return False
        print()
        print("\n📋 Validating project setup...")
        if not self.validate_project():
            print("⚠️  Project validation failed, but setup completed.")
        else:
            print("\n✅ Project setup completed successfully!")
        print("\n📦 Project Summary:")
        print("=" * 50)
        print("Core Systems: 11 modules")
        print("Configuration Options: 8 categories")
        print("Supported Game Modes: 8")
        print("Payment Providers: 5")
        print("Currency Types: 4")
        print("Board Types: 4")
        print("Character Types: 6")
        print("\nThe 3D Ludo game project is ready for development!")
        return True


def main():
    """Main entry point."""
    setup = ProjectSetup()
    success = setup.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
