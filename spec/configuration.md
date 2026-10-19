# Configuration

## Requirements

| ID | Requirement | Status | Verified by |
|----|-------------|--------|-------------|
| `CONF-1` | `[appearance] flavor`: latte, frappe, macchiato or mocha, or `gtk` to follow the GTK theme (`LOOK-10`). Any other value is warned about and mocha is used. | done | `tests/test_config.py`, `tests/test_spec.py` |
| `CONF-2` | `[appearance] accent`: any Catppuccin accent name. Any other value is warned about and mauve is used. It is ignored when `flavor` is `gtk`. | done | `tests/test_config.py`, `tests/test_spec.py` |
| `CONF-3` | `[appearance] opacity`: the window background alpha, clamped to 0.0 to 1.0. A value that is not a number is warned about and the default is used. | done | `tests/test_config.py`, `tests/test_spec.py` |
| `CONF-4` | Settings are read from `$XDG_CONFIG_HOME/wall-split/config.ini` (GLib key-file / INI syntax). A missing file is not an error. A file that can't be read or parsed is warned about on stderr, and the defaults are used. Every key is optional. | done | `tests/test_config.py` |
| `CONF-5` | Extra GTK CSS is read from `$XDG_CONFIG_HOME/wall-split/style.css` (`LOOK-7`). A missing file is not an error. | done | `tests/test_theme.py::test_css_is_assembled_in_order` |
| `CONF-6` | Changes to `config.ini` and `style.css` apply when the app is restarted. | done code review: the config and CSS are read once in `do_startup` |
| `CONF-7` | `data/config.example.ini` lists every setting with its default. The package installs it, with `themes/` and `style.css`, to `share/wall-split/`. | done | `tests/test_spec.py::test_example_config_matches_spec`, `nix build` |
| `CONF-8` | When Wall Split starts and `config.ini` doesn't exist in `$XDG_CONFIG_HOME/wall-split/`, it creates the file (and the folder) from the example, with every setting listed at its default but commented out, so the file changes nothing until a line is uncommented. A file that exists is never written to, whether it is a regular file, a symlink or a dangling symlink. If the file can't be created, that is warned about on stderr and Wall Split starts normally. | done | `tests/test_config.py` (temp folder: created and loads as the defaults; existing files and symlinks unchanged; an unwritable folder only warns), `scripts/manual/theme.sh` (first run with an empty temp `XDG_CONFIG_HOME`) |

## Defaults

<!-- spec:config:begin -->
| Section | Key | Default |
|---------|-----|---------|
| `appearance` | `flavor` | `mocha` |
| `appearance` | `accent` | `mauve` |
| `appearance` | `opacity` | `0.85` |
<!-- spec:config:end -->

## Implementation notes

- To add a key, edit the defaults table, `Config` in `src/wall_split/config.py`, `tests/test_spec.py` and `data/config.example.ini`, and the README. The spec test fails until they agree.
