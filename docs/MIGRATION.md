# Migration Guide: Moving functionality into `engine/`

This document describes the project's staged migration approach from `core/`
to the new `engine/` package. The migration keeps runtime compatibility by
providing shims and re-exports while features are moved incrementally.

Goals
- Separate engine concerns (renderer, GPU mesh, asset loaders) into `engine/`.
- Keep `core/` as a compatibility layer during migration to avoid breaking imports.
- Add unit tests and run them after each move.

Current conventions
- New engine modules live under `engine/<area>/...` (e.g. `engine/systems`,
  `engine/frontend`, `engine/core`).
- `engine/*` modules should be importable directly (e.g. `from engine.systems import UISystem`).
- `core/__init__.py` may re-export selected symbols from `engine.*` during migration.

Migration recipe (per module)
1. Add the new module under `engine/...` as a copy of the existing `core/...` file.
2. Update `engine` shims (e.g. `engine/systems/__init__.py`) to export from the new location.
3. Update `core/__init__.py` to re-export the moved symbol from `engine.*` if external code still imports from `core`.
4. Run unit tests: `venv/bin/python -m unittest discover -s tests -p "test_*.py" -v`.
5. Search codebase for remaining `core.<module>` imports and update callers to import from `engine.*` where appropriate.
6. After tests and runtime checks pass, remove the original `core/<module>.py` file.

Developer tips
- Keep shims minimal and well-documented to avoid circular imports.
- Add unit tests that exercise the public API of the module before moving it.
- Use `venv/bin/python -c "import engine.assets; print('ok')"` to smoke-test simple imports.
- Move asset loader logic into `engine.assets` and remove the temporary `engine.core` migration layer.

Next recommended tasks
- Update developer README with the migration status (done).
- Migrate remaining subsystems or tools into `engine/` following the recipe.
