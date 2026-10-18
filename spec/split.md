# Split

The split is non-destructive on the whole image. The controls move one vertical cut; they never crop.

## Requirements

| ID | Requirement | Status | Verified by |
|----|-------------|--------|-------------|
| `SPLIT-1` | A cut at column `x` of a `W`×`H` source gives a left image of `x`×`H` and a right image of `(W−x)`×`H`, in native pixels: every source pixel is in exactly one output, and nothing is rescaled. | done | `tests/test_split.py::test_split_sizes`, `test_split_sizes_clamp`, `test_every_pixel_accounted` |
| `SPLIT-2` | Choosing a left-side ratio `r` puts the cut at `x = round(H·r)`, clamped to `[0, W]`. The right side's ratio is `(W−x)/H`. | done | `tests/test_split.py::test_cut_x_basic`, `test_cut_x_clamps`, `test_right_ratio` |
| `SPLIT-3` | The common monitor ratios are 16:9, 21:9, 16:10, 4:3, 5:4, 32:9 and 1:1. | done | `tests/test_pairings.py::test_common_ratios` |
| `SPLIT-4` | The pairings for a source are found by taking each common ratio as the left side and keeping it when the implied right ratio is within ±2% (relative) of a common ratio, which names the right side. | partial: no test pins the ±2% boundary, or a source with no pairings | `tests/test_pairings.py` |
| `SPLIT-5` | When 16:9 + 16:9 is a pairing (the source is within tolerance of 32:9), it is listed first and is the default. | done | `tests/test_pairings.py::test_32_over_9_gets_169_plus_169`, `test_prefers_169_at_top` |
| `SPLIT-6` | When no pairing fits, the default cut is `W/2` (rounded down). | partial: built, not verified | manual |

## Implementation notes

- The left side of a pairing is always exact, because `x` is computed from it. Only the right side is matched within tolerance.
- The most common ultrawide panel doesn't match 21:9 within ±2%: 3440×1440 is 2.389, 2.4% off 21/9 = 2.333 (2560×1080, at 2.370, does match). A 6000×1440 source (2560 + 3440) therefore gets no 16:9 + 21:9 pairing. Not decided whether that is wanted.
- `split.snap_to_ratio` is not used by the app.
