"""Migration shims for core systems.

This module re-exports the existing `core` system classes so callers can
import from `engine.systems` during the migration. Over time the implementations
will be moved into this package and the shims removed.
"""
from engine.systems.sound_system import SoundSystem  # noqa: F401
from engine.systems.animation_system import AnimationSystem, AnimationType  # noqa: F401
from engine.systems.ui_system import UISystem, Button, Label, TextInput  # noqa: F401

__all__ = [
    'SoundSystem',
    'AnimationSystem',
    'AnimationType',
    'UISystem',
    'Button',
    'Label',
    'TextInput',
]
"""Systems package re-exports.

Re-export system components from `core` so code can start importing from
`engine.systems` instead of `core` during refactor.
"""
# Legacy re-exports removed — implementations live under engine.systems
