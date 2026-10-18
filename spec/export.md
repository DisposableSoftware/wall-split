# Export

## Requirements

| ID | Requirement | Status | Verified by |
|----|-------------|--------|-------------|
| `EXP-1` | "Export..." opens one save dialog every time, suggesting `wallpaper.png`. The chosen name without its extension is the base, and the app writes `<dir>/<base>-left.png` and `<dir>/<base>-right.png`. | partial: built, not verified | manual |
| `EXP-2` | Both outputs are PNG with 8 bits per channel, keep the source's alpha channel if it has one, and hold the source's pixels unchanged (`SPLIT-1`). | partial: built, not verified | manual (compare the columns either side of the cut with the source) |
| `EXP-3` | If writing either file fails, an alert dialog shows the error. | partial: built, not verified | manual (export into a read-only directory) |
