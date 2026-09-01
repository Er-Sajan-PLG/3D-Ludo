# 3D-Ludo Versioning

**Version:** 1.0.0
**Status:** Active
**Owner:** Governance
**Applies To:** 3D-Ludo game (Ludo-on-TFT, C# Core + Unity)
**Related:** `README.md`, workspace `docs/WORKSPACE-VERSIONING.md`

---

## 1. Purpose

Tracks a single repository semantic version (`VERSION`) as the release source of truth,
kept in sync with the workspace versioning system so doc markers stay fresh and every build
has a stable reference.

## 2. Source of truth

- **Repository version:** root `VERSION` (semver, e.g. `1.0.0`).

## 3. Bumping rules

Semver `X.Y.Z`:
- **MAJOR** — breaking change to the game/contract.
- **MINOR** — new feature or capability.
- **PATCH** — bugfix / small corrective change.

Bump + sync with the workspace tool:

```bash
python3 ../scripts/version_bump.py bump minor --scope 3D-Ludo
python3 ../scripts/version_bump.py check --scope 3D-Ludo   # must exit 0
```

Conventional Commits accompany every release.

## 4. Enforcement

- Workspace pre-commit `check-doc-versions` / CI verifies `**Version:**` doc markers match
  `VERSION` before merge.
- This repository's own governance overrides workspace defaults inside this repo.

---

*Derived from workspace `docs/WORKSPACE-VERSIONING.md`.*