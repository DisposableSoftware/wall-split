# Integration

## Nix and launching

| ID | Requirement | Status | Verified by |
|----|-------------|--------|-------------|
| `INT-1` | `nix develop` gives a shell with Python, PyGObject, pytest and GTK 4, in which `pytest` runs the tests. | done | `nix develop -c pytest` |
| `INT-2` | Inside the devshell, `python -m wall_split` from `src/` starts the app. | done | headless: `cd src && nix develop -c python -m wall_split` opens the window with the app ID |
| `INT-3` | The flake exports `packages.<system>.default` for x86_64-linux and aarch64-linux: `bin/wall-split`, wrapped by `wrapGAppsHook4`. `nix build` runs the tests. | done | `nix build` (runs pytest), then `./result/bin/wall-split` opens the window headless; aarch64-linux evaluates (`nix eval .#packages.aarch64-linux.default.drvPath`) but was not built |
| `INT-4` | `nix flake check` passes and runs the tests. | done | `nix flake check` (its `tests` check is the package build) |
| `INT-5` | Desktop entry `io.github.DisposableSoftware.WallSplit.desktop`: `Name=Wall Split`, a `Comment`, `Exec=wall-split %f`, `Icon=io.github.DisposableSoftware.WallSplit` (`LOOK-1`), `StartupWMClass=io.github.DisposableSoftware.WallSplit` (so docks and window switchers match windows to it, `WIN-2`), `Keywords=` for launcher search (wallpaper, monitor, split, dual) and `Categories=Graphics;`. It lists no `MimeType`, so it never offers itself for opening images. It passes `desktop-file-validate`. | planned | `desktop-file-validate` |
| `INT-6` | The package also installs the desktop entry in `share/applications`, the app icon in `share/icons/hicolor/scalable/apps` and the symbolic icon in `share/icons/hicolor/symbolic/apps`. | planned | `nix build`, then the three files are in `result/share` |

The manual scripts in `scripts/manual/` launch `./result/bin/wall-split`, so they need `INT-3`.
