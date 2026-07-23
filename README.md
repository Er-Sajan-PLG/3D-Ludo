# 3D Ludo Game

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
│   ├── textures/                 # Texture files
│   └── fonts/                    # Font files
├── main.py                       # Application entry point
├── setup.py                      # Project setup script
├── requirements.txt              # Python dependencies
├── README.md                     # Documentation (this file)
├── test_simple.py                 # Structure test
├── test_basic.py                 # Basic functionality test
└── .gitignore                    # Git ignore rules
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

For the long-term platform vision, see `docs/PLATFORM_ARCHITECTURE.md`.

### Migration to `engine/`

We are migrating core implementations into a new `engine/` package to
separate engine-level systems (renderer, asset loaders, GPU helpers) from the
compatibility `core/` package. During the migration:

- `engine/` is now the canonical implementation surface for the game engine.
- `engine/game` contains domain logic, `engine/systems` contains audio/UI/
  animation subsystems, and `engine/frontend` contains rendering helpers.
- `core/` remains a compatibility wrapper layer so existing imports continue
  to work while the migration completes.
- Tests are provided under `tests/` to validate each migration step.

Quick commands:

```bash
# Run unit tests
venv/bin/python -m unittest discover -s tests -p "test_*.py" -v

# Run the game (development venv assumed)
venv/bin/python main.py
```

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
