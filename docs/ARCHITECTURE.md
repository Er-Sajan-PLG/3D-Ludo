Engine architecture and migration plan
====================================

Goal
----
Create a modular, maintainable architecture for the 3D Ludo project that:
- Separates responsibilities (assets, rendering, systems, game logic, utils)
- Makes it easy to swap subsystems (e.g., replace renderer, asset loader)
- Enables safe, incremental refactoring without breaking the current runtime

High-level layout
-----------------
- engine/               -- new modular package (canonical implementation surface)
  - assets/             -- model loading, texture handling
  - renderer/           -- rendering helpers, shaders, GL pipeline
  - systems/            -- audio, UI, animation, input, networking
  - game/               -- Game controller, modes, high-level orchestration
  - utils/              -- config, logging, helpers
- core/                 -- compatibility wrappers for legacy imports during migration

Migration strategy
------------------
1. Shims: provide `engine.*` shims that re-export `core.*` modules. (Done)
2. Gradual move: pick a subsystem (assets or renderer) and port code into
   `engine.*`, updating only a small set of imports to point to `engine.`
3. Tests: run unit/integration tests after each move. Keep `core/` as
   compatibility layer until all code is migrated.
4. Cleanup: once modules live in `engine/`, remove `core/` modules and
   update imports across the codebase.

Immediate next steps
--------------------
- Implement a renderer pipeline under `engine.renderer` (shaders, camera,
  projection). We already added a simple renderer shim that uses immediate
  mode for prototypes.
- Move asset loader logic into `engine.assets` (already re-exported).
- Provide a small migration guide and update import statements in `main.py`
  and other entrypoints to prefer `engine.*`.

Longer-term ideas
-----------------
- Replace legacy immediate-mode draw calls with a shader-based pipeline and
  VAO/VBO management.
- Add an `engine.scene` package with `Scene`, `Entity`, `Component` to
  support an entity-component-system (ECS) architecture for gameplay and
  rendering separation.
- Add tools to pre-process Blender exports into runtime bundles (binary
  buffers / npz) for faster load times.

Notes
-----
The current implementation includes shims under `engine/` that re-export
functionality from `core/`. This allows switching imports incrementally.

Further architecture details
----------------------------
See `docs/PLATFORM_ARCHITECTURE.md` for the long-term platform architecture
and service-oriented game platform design.
