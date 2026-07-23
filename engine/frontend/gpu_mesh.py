"""GPU mesh helpers for engine frontend.

Mirrors `core.gpu_mesh` but lives under `engine.frontend` for migration.
"""
from typing import Dict, Any


def _has_opengl():
    try:
        import OpenGL.GL as gl  # type: ignore
        return True
    except Exception:
        return False


def upload_positions_vbo(positions) -> Dict[str, Any]:
    """Upload positions (numpy array of shape (N,3)) to a GPU VBO if possible.

    Returns: {'vbo': int, 'count': N} on success (OpenGL), or {'positions': positions} on
    fallback.
    """
    if not _has_opengl():
        return {'positions': positions}

    try:
        from OpenGL.GL import glGenBuffers, glBindBuffer, glBufferData, GL_ARRAY_BUFFER, GL_STATIC_DRAW
        import numpy as _np

        arr = _np.ascontiguousarray(positions, dtype=_np.float32)
        size = arr.nbytes

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, arr, GL_STATIC_DRAW)

        return {'vbo': vbo, 'count': int(arr.shape[0])}
    except Exception:
        return {'positions': positions}
