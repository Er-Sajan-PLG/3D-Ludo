"""Engine package compatibility layer.

This package provides a migration path from the current `core` layout to a
more modular `engine` architecture. Modules here re-export functionality from
`engine` components so existing imports continue to work while we incrementally
move code.
"""

# Re-export some high-level helpers
from engine.utils.config import GameConfig  # noqa: F401
