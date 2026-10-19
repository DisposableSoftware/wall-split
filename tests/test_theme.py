import re
from pathlib import Path

import pytest

from wall_split import theme
from wall_split.config import ACCENTS, FLAVORS, Config
from wall_split.datadir import read_data

STYLE = read_data("style.css")
CATPPUCCIN = ("latte", "frappe", "macchiato", "mocha")


def rules(css: str):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return [m.group(1) for m in re.finditer(r"([^{}]+)\{", css)]


def test_every_rule_is_scoped():
    selectors = [s.strip() for r in rules(STYLE) for s in r.split(",")]
    assert selectors
    for s in selectors:
        assert s.startswith("window.wall-split"), s


def test_style_has_no_hex_colours():
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", STYLE)


def test_reject_outline_is_red_and_scoped():
    assert re.search(r"window\.wall-split \.rejected\s*\{[^}]*outline:[^;]*@red", STYLE)


def defined(css: str) -> set[str]:
    return {m.group(1) for m in re.finditer(r"^\s*@define-color (\w+) ", css, re.M)}


def used(css: str) -> set[str]:
    return set(re.findall(r"@(\w+)", css))


@pytest.mark.parametrize("flavor", FLAVORS)
def test_every_flavor_defines_the_colours_used(flavor):
    names = defined(theme.css(Config(flavor=flavor)))
    if flavor == "gtk":
        names |= defined(theme.GTK_FALLBACK)
    for name in used(STYLE) | set(ACCENTS):
        assert name in names, f"{flavor}: @{name} is not defined"


@pytest.mark.parametrize("flavor", CATPPUCCIN)
def test_theme_files_define_26_colours(flavor):
    assert len(defined(theme.palette(flavor))) == 26


def test_theme_files_match_the_style_guide():
    guide = Path(__file__).resolve().parents[2] / "style-guide" / "reference" / "themes"
    if not guide.is_dir():
        pytest.skip("style guide not next to the repo")
    for flavor in CATPPUCCIN:
        assert theme.palette(flavor) == (guide / f"{flavor}.css").read_text()


def test_unknown_flavor_and_accent_fall_back():
    out = theme.css(Config(flavor="nord", accent="beige"))
    assert theme.palette("mocha") in out
    assert "@define-color accent @mauve;" in out


def test_gtk_flavor_uses_the_theme_accent():
    out = theme.css(Config(flavor="gtk", accent="red"))
    assert "@define-color accent @accent_bg_color;" in out
    assert "@define-color base @window_bg_color;" in out
    assert "@define-color mauve #cba6f7;" in out
    assert "@define-color accent @red;" in theme.css(Config(accent="red"))


def test_css_is_assembled_in_order():
    out = theme.css(Config(opacity=0.5), "/* user */ window.wall-split { color: @mauve; }")
    marks = [
        "@define-color base #1e1e2e;",
        "@define-color accent @mauve;",
        "@define-color bg alpha(@base, 0.5);",
        "window.wall-split {\n  background-color: @bg;",
        "/* user */",
    ]
    positions = [out.index(m) for m in marks]
    assert positions == sorted(positions)


def rgb(css: str, name: str):
    m = re.search(rf"@define-color {name} #(\w{{6}});", css)
    return [int(m.group(1)[i : i + 2], 16) for i in (0, 2, 4)]


def luminance(c):
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = map(lin, c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


@pytest.mark.parametrize("flavor", CATPPUCCIN)
def test_selected_text_contrasts_with_the_selection(flavor):
    css = theme.palette(flavor)
    base, text = rgb(css, "base"), rgb(css, "text")
    for accent in ACCENTS:
        a = rgb(css, accent)
        selection = [b * 0.65 + x * 0.35 for b, x in zip(base, a)]
        l1, l2 = luminance(text), luminance(selection)
        ratio = (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
        assert ratio >= 3.0, f"{flavor} {accent}: {ratio:.2f}:1"
