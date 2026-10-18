# Integration

## Nix and launching

| ID | Requirement | Status | Verified by |
|----|-------------|--------|-------------|
| `INT-1` | `nix develop` gives a shell with Python, PyGObject, pytest and GTK 4, in which `pytest` runs the tests. | done | `nix develop -c pytest` |
| `INT-2` | Inside the devshell, `python -m wall_split` from `src/` starts the app. | partial: not verified; `__main__.py` patches `sys.path` and calls `main()` without a `__name__` guard | manual |
| `INT-3` | The flake exports `packages.<system>.default` for x86_64-linux and aarch64-linux: `bin/wall-split`, wrapped by `wrapGAppsHook4`. `nix build` runs the tests. | planned: the flake only has an x86_64-linux devshell | `nix build`, then `./result/bin/wall-split` |
| `INT-4` | `nix flake check` passes and runs the tests. | planned | `nix flake check` |

The manual scripts in `scripts/manual/` launch `./result/bin/wall-split`, so they need `INT-3`.
