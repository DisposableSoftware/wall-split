import os
from dataclasses import dataclass
from pathlib import Path

from gi.repository import GLib

from wall_split.datadir import APP_DIR, read_data

FLAVORS = ("latte", "frappe", "macchiato", "mocha", "gtk")
ACCENTS = (
    "rosewater", "flamingo", "pink", "mauve", "red", "maroon", "peach",
    "yellow", "green", "teal", "sky", "sapphire", "blue", "lavender",
)


@dataclass
class Config:
    flavor: str = "mocha"
    accent: str = "mauve"
    opacity: float = 0.85


def config_dir() -> Path:
    return Path(GLib.get_user_config_dir()) / APP_DIR


def warn(message: str) -> None:
    GLib.log_default_handler("wall-split", GLib.LogLevelFlags.LEVEL_WARNING, message, None)


def load(directory: Path | None = None, example: str | None = None) -> Config:
    """Reads config.ini (CONF-4), creating a commented-out one first when missing (CONF-8)."""
    directory = directory or config_dir()
    create_missing(directory, example)
    return read(directory / "config.ini")


def read(path: Path) -> Config:
    cfg = Config()
    key_file = GLib.KeyFile()
    try:
        key_file.load_from_file(str(path), GLib.KeyFileFlags.NONE)
    except GLib.Error as e:
        if not e.matches(GLib.file_error_quark(), GLib.FileError.NOENT):
            warn(f"{path}: {e.message}")
        return cfg

    def value(key: str) -> str | None:
        try:
            return key_file.get_string("appearance", key).strip()
        except GLib.Error:
            return None

    flavor = value("flavor")
    if flavor is not None:
        if flavor in FLAVORS:
            cfg.flavor = flavor
        else:
            warn(f"{path}: unknown flavor “{flavor}”, using {cfg.flavor}")
    accent = value("accent")
    if accent is not None:
        if accent in ACCENTS:
            cfg.accent = accent
        else:
            warn(f"{path}: unknown accent “{accent}”, using {cfg.accent}")
    opacity = value("opacity")
    if opacity is not None:
        try:
            parsed = float(opacity)
            if parsed != parsed:
                raise ValueError
            cfg.opacity = min(max(parsed, 0.0), 1.0)
        except ValueError:
            warn(f"{path}: opacity “{opacity}” is not a number, using {cfg.opacity}")
    return cfg


def commented(example: str) -> str:
    out = [
        "# Created by Wall Split with every default commented out. To change one,\n",
        "# remove the leading '# ' and edit the value.\n",
    ]
    for line in example.splitlines():
        if line[:1].islower() and " =" in line:
            out.append("# ")
        out.append(line + "\n")
    return "".join(out)


def create_missing(directory: Path, example: str | None = None) -> None:
    """Anything already at the path, a dangling symlink included, is left alone."""
    path = directory / "config.ini"
    if os.path.lexists(path):
        return
    try:
        text = commented(example if example is not None else read_data("config.example.ini"))
        directory.mkdir(parents=True, exist_ok=True)
        with open(path, "x", encoding="utf-8") as f:
            f.write(text)
    except OSError as e:
        warn(f"could not create {path}: {e}")
