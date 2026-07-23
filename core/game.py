"""Core compatibility wrapper for the game controller.

This module re-exports the engine implementation so old imports
like `from core.game import Game` continue to work.
"""
from engine.game.game import Game, GameState  # noqa: F401
