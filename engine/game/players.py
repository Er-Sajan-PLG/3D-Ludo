"""
Player management system for 3D Ludo.
This module handles player data, scores, and game statistics.
"""

import json
import time
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
class PlayerType(Enum):
    HUMAN = "human"
    AI = "ai"
    BOT = "bot"
class GameResult(Enum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"
    FORFEIT = "forfeit"
@dataclass
class PlayerStats:
    """Player statistics."""

    games_played: int = 0
    games_won: int = 0
    games_lost: int = 0
    games_drawn: int = 0
    games_forfeited: int = 0
    pieces_captured: int = 0
    pieces_moved: int = 0
    total_distance_traveled: float = 0.0
    average_turn_time: float = 0.0
    highest_roll: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'games_played': self.games_played,
            'games_won': self.games_won,
            'games_lost': self.games_lost,
            'games_drawn': self.games_drawn,
            'games_forfeited': self.games_forfeited,
            'pieces_captured': self.pieces_captured,
            'pieces_moved': self.pieces_moved,
            'total_distance_traveled': self.total_distance_traveled,
            'average_turn_time': self.average_turn_time,
            'highest_roll': self.highest_roll
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerStats':
        return cls(
            games_played=data.get('games_played', 0),
            games_won=data.get('games_won', 0),
            games_lost=data.get('games_lost', 0),
            games_drawn=data.get('games_drawn', 0),
            games_forfeited=data.get('games_forfeited', 0),
            pieces_captured=data.get('pieces_captured', 0),
            pieces_moved=data.get('pieces_moved', 0),
            total_distance_traveled=data.get('total_distance_traveled', 0.0),
            average_turn_time=data.get('average_turn_time', 0.0),
            highest_roll=data.get('highest_roll', 0)
        )
class Players:
    """
    Player management system.
    Manages player data, scores, and game statistics.
    """

    def __init__(self, player_id: int, name: str, config: Dict[str, Any]):
        """
        Initialize a player.

        Args:
            player_id: Unique ID for the player
            name: Player's name
            config: Player configuration dictionary
        """
        self.player_id = player_id
        self.name = name
        self.config = config

        # Player properties
        self.color = self._get_player_color(player_id)
        self.type = PlayerType(config.get('type', 'human'))
        self.ai_difficulty = config.get('ai_difficulty', 'medium')

        # Game state
        self.is_active = True
        self.is_turn = False
        self.current_pieces: List[int] = []
        self.captured_pieces: List[int] = []
        self.safe_zone_entered = False

        # Statistics
        self.stats = PlayerStats()
        self.last_roll: Optional[int] = None
        self.turn_start_time: float = 0.0
        self.turn_duration: float = 0.0

        # Game preferences
        self.sound_enabled = config.get('sound_enabled', True)
        self.auto_roll = config.get('auto_roll', False)
        self.show_roll_animation = config.get('show_roll_animation', True)
        self.preferred_dice_type = config.get('preferred_dice_type', 'classic')

    def _get_player_color(self, player_id: int) -> str:
        """
        Get color for a player based on ID.

        Args:
            player_id: Player ID

        Returns:
            Color name
        """
        colors = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta', 'orange', 'purple']
        return colors[player_id % len(colors)]

    def can_roll(self) -> bool:
        """
        Check if player can roll this turn.

        Returns:
            True if player can roll, False otherwise
        """
        return self.is_active and self.is_turn and len(self.current_pieces) > 0

    def can_move(self) -> bool:
        """
        Check if player can move a piece this turn.

        Returns:
            True if player can move, False otherwise
        """
        # For now, treat move capability same as roll capability
        return self.can_roll()

    def roll_dice(self, dice_result: int) -> None:
        """
        Process dice roll for the player.

        Args:
            dice_result: Result of dice roll
        """
        self.last_roll = dice_result
        self.turn_start_time = time.time()

        # Update statistics
        self.stats.highest_roll = max(self.stats.highest_roll, dice_result)

        # Apply AI decisions if needed
        if self.type != PlayerType.HUMAN:
            self._ai_decision(dice_result)

    def _ai_decision(self, dice_result: int) -> None:
        """
        Make AI decision based on dice roll.

        Args:
            dice_result: Result of dice roll
        """
        # Simple AI logic for demonstration
        if self.ai_difficulty == 'easy':
            # Easy AI: just move if possible
            self._select_piece_to_move(dice_result)
        elif self.ai_difficulty == 'medium':
            # Medium AI: choose best move
            best_piece = self._find_best_piece(dice_result)
            if best_piece:
                self.current_pieces.remove(best_piece)
                self.current_pieces.append(best_piece)  # Re-add in case of position logic
        elif self.ai_difficulty == 'hard':
            # Hard AI: strategic decisions
            self._strategic_ai_decision(dice_result)

    def _select_piece_to_move(self, dice_result: int) -> None:
        """
        Simple AI piece selection.

        Args:
            dice_result: Dice result
        """
        # For now, just move first available piece
        for piece_id in self.current_pieces[:]:  # Copy list
            if self._is_valid_move(piece_id, dice_result):
                self.current_pieces.remove(piece_id)
                self.current_pieces.append(piece_id)
                break

    def _find_best_piece(self, dice_result: int) -> Optional[int]:
        """
        Find the best piece to move.

        Args:
            dice_result: Dice result

        Returns:
            Best piece ID or None
        """
        # Simple heuristic: prefer pieces that can reach safe zone
        for piece_id in self.current_pieces:
            if self._is_safe_zone_piece(piece_id) and self._is_valid_move(piece_id, dice_result):
                return piece_id

        # Otherwise, find any valid piece
        for piece_id in self.current_pieces:
            if self._is_valid_move(piece_id, dice_result):
                return piece_id

        return None

    def _strategic_ai_decision(self, dice_result: int) -> None:
        """
        Strategic AI decision.

        Args:
            dice_result: Dice result
        """
        # For demonstration, just use medium AI
        self._find_best_piece(dice_result)

    def _is_valid_move(self, piece_id: int, dice_result: int) -> bool:
        """
        Check if a move is valid.

        Args:
            piece_id: ID of piece to move
            dice_result: Dice result

        Returns:
            True if move is valid, False otherwise
        """
        # This would check against the board system in a real implementation
        # For now, always return True for demo
        return True

    def _is_safe_zone_piece(self, piece_id: int) -> bool:
        """
        Check if piece is in safe zone.

        Args:
            piece_id: ID of piece

        Returns:
            True if piece is in safe zone, False otherwise
        """
        # This would check against the board system in a real implementation
        return False

    def get_pieces(self) -> List[int]:
        """
        Get player's current pieces.

        Returns:
            List of piece IDs
        """
        return self.current_pieces.copy()

    def add_piece(self, piece_id: int) -> None:
        """
        Add a piece to player.

        Args:
            piece_id: ID of piece to add
        """
        if piece_id not in self.current_pieces:
            self.current_pieces.append(piece_id)

    def remove_piece(self, piece_id: int) -> bool:
        """
        Remove a piece from player.

        Args:
            piece_id: ID of piece to remove

        Returns:
            True if piece was removed, False otherwise
        """
        if piece_id in self.current_pieces:
            self.current_pieces.remove(piece_id)
            self.captured_pieces.append(piece_id)
            self.stats.pieces_captured += 1
            return True
        return False

    def end_turn(self) -> None:
        """End the player's turn."""
        self.is_turn = False
        self.turn_duration = time.time() - self.turn_start_time

        # Update average turn time
        total_games = self.stats.games_played
        if total_games > 0:
            self.stats.average_turn_time = (
                (self.stats.average_turn_time * (total_games - 1)) + self.turn_duration
            ) / total_games

    def start_turn(self) -> None:
        """Start the player's turn."""
        self.is_turn = True
        self.turn_start_time = time.time()

    def forfeit(self) -> None:
        """Player forfeits the game."""
        self.is_active = False
        self.stats.games_forfeited += 1

    def record_win(self) -> None:
        """Record a win for the player."""
        self.stats.games_won += 1

    def record_loss(self) -> None:
        """Record a loss for the player."""
        self.stats.games_lost += 1

    def record_draw(self) -> None:
        """Record a draw for the player."""
        self.stats.games_drawn += 1

    def record_piece_moved(self) -> None:
        """Record that a piece was moved."""
        self.stats.pieces_moved += 1

    def record_distance_traveled(self, distance: float) -> None:
        """
        Record distance traveled by a piece.

        Args:
            distance: Distance traveled
        """
        self.stats.total_distance_traveled += distance

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert player to dictionary for saving.

        Returns:
            Dictionary representation of player
        """
        return {
            'player_id': self.player_id,
            'name': self.name,
            'color': self.color,
            'type': self.type.value,
            'ai_difficulty': self.ai_difficulty,
            'is_active': self.is_active,
            'is_turn': self.is_turn,
            'current_pieces': self.current_pieces,
            'captured_pieces': self.captured_pieces,
            'safe_zone_entered': self.safe_zone_entered,
            'stats': self.stats.to_dict(),
            'last_roll': self.last_roll,
            'turn_start_time': self.turn_start_time,
            'turn_duration': self.turn_duration,
            'sound_enabled': self.sound_enabled,
            'auto_roll': self.auto_roll,
            'show_roll_animation': self.show_roll_animation,
            'preferred_dice_type': self.preferred_dice_type,
            'config': self.config
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Players':
        """
        Create a player from dictionary.

        Args:
            data: Dictionary representation of player

        Returns:
            Created Players object
        """
        # Create player instance
        player = cls(data['player_id'], data['name'], data['config'])

        # Copy all other attributes
        player.color = data['color']
        player.type = PlayerType(data['type'])
        player.ai_difficulty = data['ai_difficulty']
        player.is_active = data['is_active']
        player.is_turn = data['is_turn']
        player.current_pieces = data['current_pieces']
        player.captured_pieces = data['captured_pieces']
        player.safe_zone_entered = data['safe_zone_entered']
        player.stats = PlayerStats.from_dict(data['stats'])
        player.last_roll = data['last_roll']
        player.turn_start_time = data['turn_start_time']
        player.turn_duration = data['turn_duration']
        player.sound_enabled = data['sound_enabled']
        player.auto_roll = data['auto_roll']
        player.show_roll_animation = data['show_roll_animation']
        player.preferred_dice_type = data['preferred_dice_type']

        return player

    def __str__(self) -> str:
        """String representation of player."""
        return f"{self.name} (Player {self.player_id}) - {self.color}"

    def __repr__(self) -> str:
        """Representation of player."""
        return self.__str__()