# Wall Split: specification

This folder is the source of truth for what Wall Split does. The code implements the spec. If the code and the spec disagree, the code is wrong, or the spec must be changed first.

## Files

| File | Prefix | Covers |
|------|--------|--------|
| [product.md](product.md) | `PROD` | Goals, non-goals, platform and stack constraints |
| [split.md](split.md) | `SPLIT` | The cut: split math, common ratios, pairings |
| [window.md](window.md) | `WIN` | The window, drag-and-drop, preview and controls |
| [crop.md](crop.md) | `CROP` | Crop mode: the monitor sizes, the box, and cutting from it |
| [export.md](export.md) | `EXP` | Writing the two output images |
| [appearance.md](appearance.md) | `LOOK` | The app icon |
| [integration.md](integration.md) | `INT` | Nix, launching |
| [roadmap.md](roadmap.md) | — | The order of planned work, which `/implement` follows |

Add a file with a new prefix when a feature area doesn't fit these, and list it here.

## Requirement format

Each requirement is one line in a table:

| ID | Requirement | Status | Verified by |
|----|-------------|--------|-------------|
| `WIN-1` | One sentence that can be checked. | done | `tests/test_x.py::test_name` |

- **IDs are permanent.** Do not renumber them or reuse one. When a requirement is dropped, keep its row, set the status to `dropped`, and give the reason.
- **Status** is one of:
  - `planned`: agreed but not built.
  - `partial`: built, but with a known gap. The gap is written in the row.
  - `done`: built and verified.
  - `dropped`: no longer wanted.
- Write behaviour, not implementation. Keep the "how" short, and put it under **Implementation notes** when it is not obvious or a past attempt failed.
- **Verified by** names the test, or says `manual` with what to check.
