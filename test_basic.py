#!/usr/bin/env python3
"""
Basic test for 3D Ludo game functionality.
"""

from engine.game import Game, GameState
from engine.utils import GameConfig
import sys

def test_basic_functionality():
    """Test basic game functionality."""
    print("Testing basic 3D Ludo game functionality...")

    # Load configuration
    config = GameConfig()
    print(f"✓ Configuration loaded: {config.get('game', {}).get('title', '3D Ludo')}")

    # Test game initialization
    game_config = {
        'board': {'type': 'classic', 'size': {'width': 20, 'height': 20}},
        'dice': {'type': 'classic', 'num_dice': 2},
        'sound': {'enabled': True},
        'animation': {'enabled': True},
        'ui': {'enabled': True},
        'game_modes': {'enabled': True},
        'login': {'enabled': False},
        'microtransactions': {'enabled': False},
        'require_login': False
    }

    try:
        game = Game(game_config)
        print("✓ Game instance created successfully")

        # Test game initialization
        if game.initialize_game():
            print("✓ Game initialized successfully")

            # Test game state
            stats = game.get_game_stats()
            print(f"✓ Game state: {stats}")

            # Test dice roll
            dice_result = game.dice.roll()
            print(f"✓ Dice rolled: {dice_result}")

            # Test piece creation
            pieces = game.pieces.get_all_pieces()
            print(f"✓ Created {len(pieces)} pieces")

            # Test board setup
            if game.board:
                print(f"✓ Board setup: {game.board.board_type.value} board with {len(game.board.positions)} positions")

            print("\n✅ Basic functionality test PASSED!")
            return True
        else:
            print("❌ Failed to initialize game")
            return False

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
if __name__ == '__main__':
    success = test_basic_functionality()
    sys.exit(0 if success else 1)