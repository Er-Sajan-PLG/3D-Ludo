"""Game-related exports for the engine package.

This module re-exports the main `Game` controller from the engine game package
so consumers can continue importing from `engine.game` during migration.
"""
from engine.game.game import Game, GameState  # noqa: F401
