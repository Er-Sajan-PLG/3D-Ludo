"""Frontend renderer implementation (migration target).

This module mirrors the previous `core.simple_renderer` implementation but
lives under `engine.frontend` for clearer separation.
"""
from typing import Any


def _has_gl():
    try:
        import OpenGL.GL as _gl  # type: ignore
        return True
    except Exception:
        return False


def draw_model(data: Any) -> None:
    """Draw a mesh provided as VBO or numpy positions. Non-fatal if GL missing."""
    if not _has_gl():
        return

    try:
        from OpenGL.GL import (
            glBindBuffer, glEnableClientState, glVertexPointer, glDrawArrays,
            glDisableClientState, GL_VERTEX_ARRAY, GL_FLOAT, GL_ARRAY_BUFFER,
            GL_TRIANGLES, glPushMatrix, glPopMatrix, glTranslatef, glScalef, glRotatef
        )
        import numpy as _np

        mesh = data
        transform = None
        if isinstance(data, dict) and 'mesh' in data:
            mesh = data['mesh']
            transform = data.get('transform')

        if transform:
            glPushMatrix()
            tx, ty, tz = transform.get('translate', (0.0, 0.0, 0.0))
            sx, sy, sz = transform.get('scale', (1.0, 1.0, 1.0))
            rx, ry, rz = transform.get('rotate', (0.0, 0.0, 0.0))
            try:
                glTranslatef(float(tx), float(ty), float(tz))
                glScalef(float(sx), float(sy), float(sz))
                if rx:
                    glRotatef(float(rx), 1.0, 0.0, 0.0)
                if ry:
                    glRotatef(float(ry), 0.0, 1.0, 0.0)
                if rz:
                    glRotatef(float(rz), 0.0, 0.0, 1.0)
            except Exception:
                pass

        if isinstance(mesh, dict) and 'vbo' in mesh:
            vbo = mesh['vbo']
            count = int(mesh.get('count', 0))
            if count > 0:
                glBindBuffer(GL_ARRAY_BUFFER, vbo)
                glEnableClientState(GL_VERTEX_ARRAY)
                glVertexPointer(3, GL_FLOAT, 0, None)
                glDrawArrays(GL_TRIANGLES, 0, count)
                glDisableClientState(GL_VERTEX_ARRAY)
                glBindBuffer(GL_ARRAY_BUFFER, 0)
        elif isinstance(mesh, dict) and 'positions' in mesh:
            arr = _np.ascontiguousarray(mesh['positions'], dtype=_np.float32)
            count = int(arr.shape[0])
            if count > 0:
                glEnableClientState(GL_VERTEX_ARRAY)
                glVertexPointer(3, GL_FLOAT, 0, arr)
                glDrawArrays(GL_TRIANGLES, 0, count)
                glDisableClientState(GL_VERTEX_ARRAY)

        if transform:
            glPopMatrix()
    except Exception:
        return
