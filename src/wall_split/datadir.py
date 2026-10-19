from pathlib import Path

from gi.repository import GLib

APP_DIR = "wall-split"


def _candidates():
    yield Path(__file__).resolve().parents[2] / "data"
    for base in GLib.get_system_data_dirs():
        yield Path(base) / APP_DIR


def data_file(name: str) -> Path:
    """A shipped data file: from the checkout when run from source, else share/wall-split."""
    for root in _candidates():
        path = root / name
        if path.is_file():
            return path
    raise FileNotFoundError(f"{name}: not found in the checkout's data/ or in $XDG_DATA_DIRS/{APP_DIR}")


def read_data(name: str) -> str:
    return data_file(name).read_text(encoding="utf-8")
