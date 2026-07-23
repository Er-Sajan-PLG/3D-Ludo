"""Asset loader consolidated into engine.assets.

This module is the canonical engine asset loader implementation and
replaces the legacy `engine.core.asset_loader` migration target.
"""
from typing import Any, Optional
import os


def _ext(path: str) -> str:
    return os.path.splitext(path)[1].lower()


def load_model(path: str) -> Any:
    """Load a model by file extension and return a loader-specific object.

    Supported formats: .gltf, .glb, .obj

    Returns:
        loader-specific object (e.g., pygltflib.GLTF2 or pywavefront.Wavefront)
    """
    ext = _ext(path)
    if ext in ('.gltf', '.glb'):
        return load_gltf(path)
    if ext == '.obj':
        return load_obj(path)
    raise ValueError(f"Unsupported model format: {ext}")


def load_gltf(path: str) -> Any:
    """Load a glTF/glb file using `pygltflib`.

    Returns the `pygltflib.GLTF2` object.
    """
    try:
        from pygltflib import GLTF2
    except Exception as e:
        raise RuntimeError("pygltflib is required to load glTF files") from e

    gltf = GLTF2().load(path)
    return gltf


def load_obj(path: str) -> Any:
    """Load an OBJ file using `pywavefront`.

    Returns the `pywavefront.Wavefront` object.
    """
    try:
        import pywavefront
    except Exception as e:
        raise RuntimeError("pywavefront is required to load OBJ files") from e

    mesh = pywavefront.Wavefront(path, create_materials=True, collect_faces=True)
    return mesh


def try_load(path: str) -> Optional[Any]:
    """Try to load a model, returning None on failure (no exception raised).

    Useful for IDE-level quick tests where failure shouldn't interrupt flow.
    """
    try:
        return load_model(path)
    except Exception:
        return None


def obj_to_numpy_mesh(wave: Any):
    """Convert a `pywavefront.Wavefront` object into a simple numpy positions
    array. Returns a dict { 'positions': np.ndarray(shape=(N,3), dtype=float32) }
    or None if conversion failed.
    """
    try:
        import numpy as _np
    except Exception:
        return None

    positions = []

    materials = getattr(wave, 'materials', None)
    if not materials:
        meshes = getattr(wave, 'meshes', None)
        if meshes:
            for m in meshes:
                verts = getattr(m, 'vertices', [])
                if not verts:
                    continue
                stride = 3
                for s in (3, 6, 8):
                    if len(verts) % s == 0:
                        stride = s
                        break
                for i in range(0, len(verts), stride):
                    positions.append(tuple(verts[i:i+3]))
    else:
        for mat in materials.values():
            verts = getattr(mat, 'vertices', [])
            if not verts:
                continue
            stride = 3
            for s in (3, 6, 8):
                if len(verts) % s == 0:
                    stride = s
                    break
            for i in range(0, len(verts), stride):
                positions.append(tuple(verts[i:i+3]))

    if not positions:
        return None

    return {'positions': _np.array(positions, dtype=_np.float32)}
