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
| `CONF-9` | Keybindings are user-changeable: `$XDG_CONFIG_HOME/wall-split/keybindings.ini` has `name = accel;accel` lines under the keys table (`CONF-10`), merged over the defaults. An empty value unbinds the action. An unknown name or an accelerator that can't be parsed is warned about on stderr and ignored; a missing or unreadable file only means the defaults. First run writes the file from the example with every binding commented out, as `CONF-8` does for `config.ini`. Source: `docs/interaction.md` (Keybindings, Config files). | planned | `tests/test_keybindings.py` (merge, unbind, bad name, bad accelerator, missing file, first-run file) |
| `CONF-10` | `data/keybindings.example.ini` lists every binding with its default, and this spec gets a keybinding table (name, action, description, default accelerators) listing the same set. A test fails when the spec table, the example file and the code disagree, as for the config table. Source: `docs/interaction.md`. | planned | `tests/test_spec.py` (keys table against the code and the example file) |
| `CONF-11` | `[window] width` and `height` set the default window size in logical px, defaulting to 960 and 640 (`WIN-1`) and clamped to a sane range (300 to 8192). Not a number: warned about, default used. Adding the keys means editing the defaults table below, `Config`, the example config and `tests/test_spec.py` together. Source: `docs/layout.md` (Window). | planned | `tests/test_config.py`, `tests/test_spec.py` |

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
