"""Rendering helpers for the engine package.

Re-exports the simple renderer and GPU helpers from `core`.
"""
from engine.frontend.renderer import draw_model  # noqa: F401
from engine.frontend.gpu_mesh import upload_positions_vbo  # noqa: F401
