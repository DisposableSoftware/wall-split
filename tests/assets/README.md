# Test assets

Files for manual checks, such as dragging onto the window on Hyprland (`WIN-3`, `WIN-4`).

| File | Content | Expected |
|------|---------|----------|
| `wide.png` | 5120×1440 PNG, blue left half, green right half | Loads; "16:9 + 16:9", cut on the colour boundary |
| `picture.txt` | 2000×1000 magenta PNG with a `.txt` name | Loads (the content decides); "Custom", 1000 \| 1000 |
| `notes.txt` | Plain text | Rejected: red border, image kept |
| `fake.png` | Plain text with a `.png` name | Rejected: red border, image kept |
