"""
Game modes system for 3D Ludo.
This module handles different game modes and their configurations.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass
from dataclasses import dataclass

class GameMode(Enum):
    CLASSIC = "classic"
    SPEED = "speed"
    REVERSE = "reverse"
    TEAM = "team"
    COOPERATIVE = "cooperative"
    BATTLE_ROYALE = "battle_royale"
    TIME_ATTACK = "time_attack"
    MATCH_STOPS = "match_stops"
@dataclass
class GameModeConfig:
    """Configuration for a game mode."""

    mode: GameMode
    num_players: int = 4
    board_size: str = "standard"
    starting_pieces: int = 4
    dice_rolls_per_turn: int = 1
    can_roll_twice: bool = False
    allow_jumping: bool = False
    safe_zones_enabled: bool = True
    capture_rules: str = "normal"  # normal, aggressive, no_capture
    time_limit: Optional[int] = None  # in seconds
    extra_rules: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'mode': self.mode.value,
            'num_players': self.num_players,
            'board_size': self.board_size,
            'starting_pieces': self.starting_pieces,
            'dice_rolls_per_turn': self.dice_rolls_per_turn,
            'can_roll_twice': self.can_roll_twice,
            'allow_jumping': self.allow_jumping,
            'safe_zones_enabled': self.safe_zones_enabled,
            'capture_rules': self.capture_rules,
            'time_limit': self.time_limit,
            'extra_rules': self.extra_rules or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameModeConfig':
        return cls(
            mode=GameMode(data['mode']),
            num_players=data.get('num_players', 4),
            board_size=data.get('board_size', 'standard'),
            starting_pieces=data.get('starting_pieces', 4),
            dice_rolls_per_turn=data.get('dice_rolls_per_turn', 1),
            can_roll_twice=data.get('can_roll_twice', False),
            allow_jumping=data.get('allow_jumping', False),
            safe_zones_enabled=data.get('safe_zones_enabled', True),
            capture_rules=data.get('capture_rules', 'normal'),
            time_limit=data.get('time_limit'),
            extra_rules=data.get('extra_rules', {})
        )
class GameModes:
    """
    Game modes system for 3D Ludo.
    Handles different game modes and their configurations.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the game modes system with configuration.

        Args:
            config: Game modes configuration dictionary
        """
        self.config = config
        self.is_enabled = config.get('enabled', True)
        self.available_modes = self._get_available_game_modes(config)
        self.current_mode: Optional[GameMode] = None
        self.current_mode_config: Optional[GameModeConfig] = None
        self.mode_history: List[GameMode] = []

        # Initialize current mode if specified
        initial_mode = config.get('initial_mode', 'classic')
        if initial_mode in [mode.value for mode in GameMode]:
            self.set_current_mode(GameMode(initial_mode))
        else:
            self.set_current_mode(GameMode.CLASSIC)

    def _get_available_game_modes(self, config: Dict[str, Any]) -> List[GameMode]:
        """
        Get list of available game modes based on configuration.

        Args:
            config: Configuration dictionary

        Returns:
            List of available game modes
        """
        # Get available modes from config
        available_modes_config = config.get('available_modes', [])

        if not available_modes_config:
            # Default to all modes
            return list(GameMode)

        # Filter to only available modes
        available_modes = []
        for mode_config in available_modes_config:
            if isinstance(mode_config, dict):
                mode_name = mode_config.get('mode', 'classic')
            else:
                mode_name = mode_config

            try:
                mode = GameMode(mode_name)
                available_modes.append(mode)
            except ValueError:
                # Skip invalid modes
                pass

        return available_modes

    def set_current_mode(self, mode: GameMode) -> bool:
        """
        Set current game mode.

        Args:
            mode: Game mode to set

        Returns:
            True if mode set successfully, False otherwise
        """
        if not self.is_enabled:
            return False

        if mode in self.available_modes:
            # Store previous mode
            if self.current_mode:
                self.mode_history.append(self.current_mode)

            # Set new mode
            self.current_mode = mode
            self.current_mode_config = self._get_mode_config(mode)

            # Log mode change
            if self.config.get('debug', False):
                print(f"Game mode changed to: {mode.value}")

            return True

        return False

    def get_current_mode(self) -> Optional[GameMode]:
        """Get current game mode."""
        return self.current_mode

    def get_current_mode_config(self) -> Optional[Dict[str, Any]]:
        """Get current game mode configuration as a dict."""
        return self.current_mode_config.to_dict() if self.current_mode_config else None

    def get_mode_config(self, mode: GameMode) -> Optional[GameModeConfig]:
        """
        Get configuration for a specific game mode.

        Args:
            mode: Game mode to get configuration for

        Returns:
            Game mode configuration or None if mode not available
        """
        if mode in self.available_modes:
            return self._get_mode_config(mode)
        return None

    def _get_mode_config(self, mode: GameMode) -> GameModeConfig:
        """
        Get default configuration for a game mode.

        Args:
            mode: Game mode

        Returns:
            Game mode configuration
        """
        mode_configs = {
            GameMode.CLASSIC: GameModeConfig(
                mode=GameMode.CLASSIC,
                num_players=4,
                board_size='standard',
                starting_pieces=4,
                dice_rolls_per_turn=1,
                can_roll_twice=False,
                allow_jumping=False,
                safe_zones_enabled=True,
                capture_rules='normal'
            ),
            GameMode.SPEED: GameModeConfig(
                mode=GameMode.SPEED,
                num_players=2,
                board_size='large',
                starting_pieces=4,
                dice_rolls_per_turn=1,
                can_roll_twice=True,
                allow_jumping=False,
                safe_zones_enabled=False,
                capture_rules='normal'
            ),
            GameMode.REVERSE: GameModeConfig(
                mode=GameMode.REVERSE,
                num_players=4,
                board_size='standard',
                starting_pieces=4,
                dice_rolls_per_turn=1,
                can_roll_twice=False,
                allow_jumping=False,
                safe_zones_enabled=True,
                capture_rules='reverse'
            ),
            GameMode.TEAM: GameModeConfig(
                mode=GameMode.TEAM,
                num_players=4,
                board_size='standard',
                starting_pieces=4,
                dice_rolls_per_turn=1,
                can_roll_twice=False,
                allow_jumping=False,
                safe_zones_enabled=True,
                capture_rules='normal',
                extra_rules={'teams': [{'id': 0, 'members': [0, 1]}, {'id': 1, 'members': [2, 3]}]}
            ),
            GameMode.COOPERATIVE: GameModeConfig(
                mode=GameMode.COOPERATIVE,
                num_players=2,
                board_size='standard',
                starting_pieces=2,
                dice_rolls_per_turn=2,
                can_roll_twice=False,
                allow_jumping=True,
                safe_zones_enabled=True,
                capture_rules='no_capture',
                extra_rules={'shared_pieces': True}
            ),
            GameMode.BATTLE_ROYALE: GameModeConfig(
                mode=GameMode.BATTLE_ROYALE,
                num_players=8,
                board_size='small',
                starting_pieces=2,
                dice_rolls_per_turn=1,
                can_roll_twice=False,
                allow_jumping=False,
                safe_zones_enabled=False,
                capture_rules='aggressive',
                time_limit=15 * 60,  # 15 minutes
                extra_rules={'elimination_zone': True}
            ),
            GameMode.TIME_ATTACK: GameModeConfig(
                mode=GameMode.TIME_ATTACK,
                num_players=2,
                board_size='standard',
                starting_pieces=4,
                dice_rolls_per_turn=1,
                can_roll_twice=False,
                allow_jumping=False,
                safe_zones_enabled=True,
                capture_rules='normal',
                time_limit=10 * 60,  # 10 minutes
                extra_rules={'objective': 'capture_all_pieces'}
            ),
            GameMode.MATCH_STOPS: GameModeConfig(
                mode=GameMode.MATCH_STOPS,
                num_players=4,
                board_size='standard',
                starting_pieces=4,
                dice_rolls_per_turn=1,
                can_roll_twice=False,
                allow_jumping=False,
                safe_zones_enabled=True,
                capture_rules='normal',
                extra_rules={'match_points': True, 'highest_roll_wins': True}
            )
        }

        return mode_configs.get(mode, GameModeConfig(mode=GameMode.CLASSIC))

    def get_available_modes(self) -> List[GameMode]:
        """Get list of available game modes."""
        return self.available_modes.copy()

    def get_mode_names(self) -> List[str]:
        """Get list of available mode names."""
        return [mode.value for mode in self.available_modes]

    def is_mode_available(self, mode: GameMode) -> bool:
        """
        Check if a game mode is available.

        Args:
            mode: Game mode to check

        Returns:
            True if mode is available, False otherwise
        """
        return mode in self.available_modes

    def update_turn_time(self, turn_time: float) -> None:
        """
        Update turn time for current mode.

        Args:
            turn_time: Time elapsed for turn
        """
        # This could apply time-based penalties or bonuses based on mode
        if self.current_mode_config and self.current_mode_config.time_limit:
            # Check for time limit violations
            pass

    def get_game_rules(self) -> Dict[str, Any]:
        """
        Get game rules for current mode.

        Returns:
            Dictionary with game rules
        """
        if not self.current_mode_config:
            return {}

        rules = {
            'num_players': self.current_mode_config.num_players,
            'board_size': self.current_mode_config.board_size,
            'starting_pieces': self.current_mode_config.starting_pieces,
            'dice_rolls_per_turn': self.current_mode_config.dice_rolls_per_turn,
            'can_roll_twice': self.current_mode_config.can_roll_twice,
            'allow_jumping': self.current_mode_config.allow_jumping,
            'safe_zones_enabled': self.current_mode_config.safe_zones_enabled,
            'capture_rules': self.current_mode_config.capture_rules,
            'time_limit': self.current_mode_config.time_limit,
            'extra_rules': self.current_mode_config.extra_rules or {}
        }

        return rules

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert game modes system to dictionary for saving.

        Returns:
            Dictionary representation of game modes
        """
        return {
            'is_enabled': self.is_enabled,
            'available_modes': [mode.value for mode in self.available_modes],
            'current_mode': self.current_mode.value if self.current_mode else None,
            'current_mode_config': self.current_mode_config.to_dict() if self.current_mode_config else None,
            'mode_history': [mode.value for mode in self.mode_history]
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load game modes system from dictionary.

        Args:
            data: Dictionary representation of game modes
        """
        self.is_enabled = data['is_enabled']

        # Restore available modes
        available_modes = []
        for mode_name in data['available_modes']:
            try:
                mode = GameMode(mode_name)
                available_modes.append(mode)
            except ValueError:
                pass
        self.available_modes = available_modes

        # Restore current mode
        if data['current_mode']:
            try:
                current_mode = GameMode(data['current_mode'])
                if current_mode in self.available_modes:
                    self.current_mode = current_mode
                    if data['current_mode_config']:
                        self.current_mode_config = GameModeConfig.from_dict(data['current_mode_config'])
            except ValueError:
                pass

        # Restore mode history
        mode_history = []
        for mode_name in data['mode_history']:
            try:
                mode = GameMode(mode_name)
                mode_history.append(mode)
            except ValueError:
                pass
        self.mode_history = mode_history

    def update(self) -> None:
        """Update game modes system."""
        # Update logic for time-limited modes, etc.
        if self.current_mode_config and self.current_mode_config.time_limit:
            # Check for time limit
            pass

    def cleanup(self) -> None:
        """Cleanup game modes system."""
        self.mode_history.clear()
        self.current_mode = None
        self.current_mode_config = None
