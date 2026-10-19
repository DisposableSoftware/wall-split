import re
from pathlib import Path

from gi.repository import GLib

from wall_split.config import ACCENTS, Config
from wall_split.datadir import data_file

SPEC = Path(__file__).resolve().parents[1] / "spec" / "configuration.md"


def spec_rows():
    text = SPEC.read_text()
    table = text.split("<!-- spec:config:begin -->")[1].split("<!-- spec:config:end -->")[0]
    rows = [[c.strip().strip("`") for c in line.strip().strip("|").split("|")] for line in table.strip().splitlines()]
    return [r for r in rows[2:]]


def default_value(cfg: Config, section: str, key: str) -> str:
    return {("appearance", "flavor"): cfg.flavor, ("appearance", "accent"): cfg.accent,
            ("appearance", "opacity"): str(cfg.opacity)}[(section, key)]


def test_defaults_table_matches_the_code():
    rows = spec_rows()
    assert len(rows) == 3
    for section, key, default in rows:
        assert default_value(Config(), section, key) == default


def test_example_config_matches_spec():
    kf = GLib.KeyFile()
    kf.load_from_file(str(data_file("config.example.ini")), GLib.KeyFileFlags.NONE)
    rows = spec_rows()
    assert kf.get_groups()[0] == ["appearance"]
    assert sorted(kf.get_keys("appearance")[0]) == sorted(k for _, k, _ in rows)
    for section, key, default in rows:
        assert kf.get_value(section, key) == default


def test_example_lists_every_accent():
    text = data_file("config.example.ini").read_text()
    assert all(a in text for a in ACCENTS)


def test_every_spec_row_has_a_status():
    for name in ("appearance.md", "configuration.md"):
        for line in (SPEC.parent / name).read_text().splitlines():
            m = re.match(r"\| `(LOOK|CONF)-\d+` \|", line)
            if m:
                assert re.search(r"\| (planned|partial|done|dropped)\b[^|]* \|", line), line
