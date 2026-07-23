"""
Main game class for 3D Ludo.
This is the core game controller that manages all systems and game flow.
"""

import time
import json
try:
    import pygame
except ImportError:
    pygame = None
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass

from .board import Board
from .pieces import Pieces
from .dice import Dice
from .players import Players
from engine.systems import SoundSystem
from engine.systems import AnimationSystem
from engine.systems import UISystem
from .game_modes import GameModes
from .login_system import LoginSystem
from .microtransactions import Microtransactions
class GameState(Enum):
    LOBBY = "lobby"
    SETUP = "setup"
    PLAYING = "playing"
    PAUSED = "paused"
    FINISHED = "finished"
class Game:
    """
    Main game controller class.
    Manages all game systems and controls the game flow.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the game with configuration.

        Args:
            config: Game configuration dictionary
        """
        self.config = config
        self.state = GameState.SETUP
        self.players: List[Players] = []
        self.current_player: Optional[Players] = None
        self.current_turn: int = 0
        self.winner: Optional[Players] = None
        self.turn_start_time: float = 0.0

        # Initialize game systems
        self.gameplay_config = config.get('gameplay', {})
        self.board = Board(config.get('board', {}))
        self.pieces = Pieces(config.get('pieces', {}))
        self.dice = Dice(config.get('dice', {}))
        self.sound_system = SoundSystem(config.get('sound', {}))
        self.animation_system = AnimationSystem(config.get('animation', {}))
        self.ui_system = UISystem(config.get('ui', {}))
        self.game_modes = GameModes(config.get('game_modes', {}))
        self.login_system = LoginSystem(config.get('login', {}))
        self.microtransactions = Microtransactions(config.get('microtransactions', {}))

        # Game callbacks
        self.on_state_change: Callable[[GameState], None] = lambda state: None
        self.on_player_turn: Callable[[Players], None] = lambda player: None
        self.on_piece_moved: Callable[[Pieces, int], None] = lambda piece, position: None
        self.on_game_finished: Callable[[Players], None] = lambda winner: None

    def initialize_game(self) -> bool:
        """
        Initialize the game with players and setup.

        Returns:
            True if game initialized successfully, False otherwise
        """
        try:
            # Setup login system if enabled
            if self.config.get('require_login', False):
                if not self.login_system.is_authenticated():
                    self.login_system.show_login()

            # Create players based on game mode
            game_mode_config = self.game_modes.get_current_mode_config()
            num_players = game_mode_config.get('num_players', 2)

            for i in range(num_players):
                player = Players(
                    player_id=i,
                    name=f"Player {i + 1}",
                    config=self.gameplay_config.get('players', {})
                )
                self.players.append(player)

            # Setup board with player pieces
            self.board.setup_board(self.players, self.pieces)

            # Start first player's turn
            self.current_player = self.players[0]
            self.state = GameState.PLAYING
            self.turn_start_time = time.time()

            self.on_state_change(GameState.PLAYING)
            self.on_player_turn(self.current_player)

            # Play background music if enabled
            if self.config.get('sound', {}).get('enable_background_music', False):
                self.sound_system.play_background_music()

            return True

        except Exception as e:
            print(f"Error initializing game: {e}")
            return False

    def process_turn(self) -> None:
        """Process the current player's turn."""
        if self.state != GameState.PLAYING or not self.current_player:
            return

        try:
            # Roll dice
            dice_result = self.dice.roll()

            # Play dice sound
            self.sound_system.play_sound('dice_roll')

            # Check if all players have pieces in start position
            if self.current_player.can_roll():
                self.current_player.roll_dice(dice_result)

                # Process piece movement
                moved_pieces = self.process_piece_movement()

                # Check for win condition
                if self.check_win_condition():
                    self.state = GameState.FINISHED
                    self.sound_system.play_sound('win')
                    self.on_game_finished(self.winner)
                else:
                    # Switch to next player
                    self.next_turn()
                    self.on_player_turn(self.current_player)

        except Exception as e:
            print(f"Error processing turn: {e}")
            self.next_turn()

    def process_piece_movement(self) -> List[Pieces]:
        """
        Process piece movement based on dice roll.

        Returns:
            List of pieces that were moved
        """
        moved_pieces = []
        dice_result = self.dice.last_roll

        for piece_id in self.current_player.get_pieces():
            piece = self.pieces.get_piece_by_id(piece_id) # Retrieve the actual Piece object
            if piece and piece.can_move() and not piece.is_selected:
                continue

            target_position = piece.calculate_target_position(dice_result) if piece else None
            if piece and target_position is not None and self.board.is_valid_position(target_position):
                # Animate piece movement
                self.animation_system.animate_piece_movement(piece, target_position)

                # Move piece
                old_position = piece.position
                piece.position = target_position

                # Check for special positions (safe zones, ladders, etc.)
                self.apply_position_effects(piece)

                # Check for capture
                captured_piece = self.check_capture(piece)
                if captured_piece:
                    self.pieces.capture_piece(captured_piece)
                    self.sound_system.play_sound('capture')

                # Log move
                self.log_move(piece, old_position, target_position, captured_piece)

                moved_pieces.append(piece)
                self.on_piece_moved(piece, target_position)

                # Break if piece reached the end path
                if self.board.is_safe_position(target_position):
                    piece.reached_end = True

                break  # Only one piece can move per turn

        return moved_pieces

    def apply_position_effects(self, piece: Pieces) -> None:
        """
        Apply special effects for certain positions.

        Args:
            piece: The piece that moved
        """
        position_info = self.board.get_position_info(piece.position)

        if position_info.get('type') == 'safe_zone' and piece.player_id != 0:
            # Safe zone - prevent capture
            pass

        elif position_info.get('type') == 'ladder':
            self.animation_system.animate_ladder_climb(piece)
            self.sound_system.play_sound('ladder')

        elif position_info.get('type') == 'snake':
            self.animation_system.animate_snake_bite(piece)
            self.sound_system.play_sound('snake')

    def check_capture(self, piece: Pieces) -> Optional[Pieces]:
        """
        Check if a piece was captured.

        Args:
            piece: The moving piece

        Returns:
            The captured piece if any, None otherwise
        """
        opponent_pieces = self.pieces.get_opponent_pieces(piece.player_id)
        opponent_pieces_in_safe_zone = [
            p for p in opponent_pieces
            if p.position in self.board.get_safe_zone_positions(piece.player_id)
        ]

        return opponent_pieces_in_safe_zone[0] if opponent_pieces_in_safe_zone else None

    def check_win_condition(self) -> bool:
        """
        Check if any player has won the game.

        Returns:
            True if game has been won, False otherwise
        """
        for player in self.players:
            player_pieces = self.pieces.get_player_pieces(player.player_id)
            if all(piece.reached_end for piece in player_pieces):
                self.winner = player
                return True

        return False

    def next_turn(self) -> None:
        """Switch to the next player's turn."""
        current_index = self.players.index(self.current_player)
        next_index = (current_index + 1) % len(self.players)
        self.current_player = self.players[next_index]

        # Update turn timer
        turn_time = time.time() - self.turn_start_time
        self.game_modes.update_turn_time(turn_time)

        self.turn_start_time = time.time()

    def pause_game(self) -> None:
        """Pause the game."""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
            self.sound_system.play_sound('pause')
            self.on_state_change(GameState.PAUSED)

    def resume_game(self) -> None:
        """Resume the game."""
        if self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
            self.turn_start_time = time.time()
            self.sound_system.play_sound('resume')
            self.on_state_change(GameState.PLAYING)

    def save_game(self, filepath: str) -> bool:
        """
        Save the current game state.

        Args:
            filepath: Path to save the game

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            game_data = {
                'config': self.config,
                'state': self.state.value,
                'players': [player.to_dict() for player in self.players],
                'current_player': self.current_player.player_id if self.current_player else None,
                'current_turn': self.current_turn,
                'winner': self.winner.player_id if self.winner else None,
                'board': self.board.to_dict(),
                'pieces': self.pieces.to_dict(),
                'dice': self.dice.to_dict(),
                'turn_start_time': self.turn_start_time,
                'timestamp': time.time()
            }

            with open(filepath, 'w') as f:
                json.dump(game_data, f, indent=2)

            self.sound_system.play_sound('save')
            return True

        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self, filepath: str) -> bool:
        """
        Load a saved game state.

        Args:
            filepath: Path to load the game from

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                game_data = json.load(f)

            # Restore game state
            self.state = GameState(game_data['state'])
            self.config = game_data['config']

            # Recreate players
            self.players = []
            for player_data in game_data['players']:
                player = Players(player_data['player_id'], player_data['name'], player_data['config'])
                self.players.append(player)

            # Set current state
            if game_data['current_player'] is not None:
                self.current_player = self.players[game_data['current_player']]

            self.current_turn = game_data['current_turn']
            if game_data['winner'] is not None:
                self.winner = self.players[game_data['winner']]

            # Restore other systems (these would need proper to_dict/load_dict methods)
            # For now, we'll need to implement these
            self.turn_start_time = game_data['turn_start_time']

            self.sound_system.play_sound('load')
            return True

        except Exception as e:
            print(f"Error loading game: {e}")
            return False

    def log_move(self, piece: Pieces, old_pos: int, new_pos: int, captured: Optional[Pieces]) -> None:
        """
        Log a piece move for replay or analytics.

        Args:
            piece: The piece that moved
            old_pos: Previous position
            new_pos: New position
            captured: The captured piece if any
        """
        move_data = {
            'timestamp': time.time(),
            'player_id': piece.player_id,
            'piece_id': piece.piece_id,
            'old_position': old_pos,
            'new_position': new_pos,
            'captured_piece_id': captured.piece_id if captured else None,
            'dice_roll': self.dice.last_roll
        }

        # Log move to file
        with open('game_moves.log', 'a') as f:
            f.write(json.dumps(move_data) + '\n')

    def update(self, delta_time: float) -> None:
        """
        Update game state based on elapsed time.

        Args:
            delta_time: Time elapsed since last update
        """
        if self.state == GameState.PLAYING:
            self.animation_system.update(delta_time)

            # Check for turn timeout
            if self.current_player and not self.current_player.can_move():
                self.next_turn()
                self.on_player_turn(self.current_player)

    def render(self, screen) -> None:
        """
        Render the game to the screen.

        Args:
            screen: The rendering surface
        """
        # Render game systems
        self.board.render(screen)
        self.pieces.render(screen)
        self.animation_system.render(screen)
        # Draw any loaded prototype models (VBOs or position arrays)
        try:
            from engine.renderer import draw_model
            if hasattr(self, 'loaded_models') and self.loaded_models:
                for name, data in self.loaded_models.items():
                    draw_model(data)
        except Exception:
            pass
        self.ui_system.render(screen)

        # Render UI elements
        self.ui_system.render_turn_info(screen, self.current_player, {'last_roll': self.dice.last_roll})
        self.ui_system.render_score(screen, self.players)

    def is_game_over(self) -> bool:
        """Check if the game has ended."""
        return self.state == GameState.FINISHED

    def get_game_stats(self) -> Dict[str, Any]:
        """
        Get game statistics.

        Returns:
            Dictionary with game statistics
        """
        return {
            'game_state': self.state.value,
            'current_player': self.current_player.player_id if self.current_player else None,
            'turn_number': self.current_turn,
            'winner': self.winner.player_id if self.winner else None,
            'total_players': len(self.players),
            'game_time': time.time() - self.turn_start_time
        }
