Components Overview
===================

This document outlines the high-level components and recommended boundaries for
3D Ludo's new engine architecture.

Frontend (engine.frontend)
-------------------------
- renderer: rendering pipeline, shaders, camera, scene graph
- ui: UI widgets and input handling (wraps pygame)
- audio client: sound playback hooks (delegates to systems)

Backend (engine.backend)
------------------------
- game: high-level game controller (`Game`), modes, rules
- systems: animation, sound, microtransactions, login
- persistence: save/load game state, user data

Core (engine.core)
------------------
- math, geometry, low-level helpers
- GPU helpers (VBO/VAO abstraction)

Frontend (engine.frontend)
--------------------------
- renderer helpers
- asset loading and import
- GPU buffer creation

Tools / Pipeline
----------------
- exporter tools: Blender -> glTF/OBJ -> runtime bundles
- preprocessors: pack textures, optimize meshes, generate binary buffers

Migration Plan
--------------
1. Provide `engine.*` shims that re-export `core.*` (done).
2. Move or re-implement modules into `engine.frontend`, `engine.backend`, and
   `engine.core` one subsystem at a time, updating a small set of imports and
   running tests.
3. Replace shims with direct implementations and delete `core/` modules when
   migration is complete.

API Stability
-------------
- Keep public APIs stable during migration. Add compatibility wrappers if
  internal signatures must change.

Testing
-------
- Add unit tests for each subsystem as it is migrated.
- Add integration tests that exercise `Game` startup and basic flows.

