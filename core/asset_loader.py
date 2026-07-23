"""Core compatibility wrapper for the engine asset loader.

This module re-exports the engine-side asset loader implementation during the
migration from `core` to `engine`.
"""
from typing import Any, Optional

from engine.assets.asset_loader import load_model, load_gltf, load_obj, try_load, obj_to_numpy_mesh  # noqa: F401

