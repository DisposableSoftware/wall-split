import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gdk, Gtk

from wall_split.config import ACCENTS, Config, config_dir
from wall_split.datadir import read_data

WINDOW_CLASS = "wall-split"

# Defines the libadwaita names flavor = gtk reads, for themes that only have GTK's
# older names. The theme's own definitions take precedence over these.
GTK_FALLBACK = """\
@define-color window_bg_color @theme_bg_color;
@define-color window_fg_color @theme_fg_color;
@define-color accent_bg_color @theme_selected_bg_color;
"""

# Fractions of the way from base to text, measured on mocha and latte.
SHADES = (
    ("surface0", 0.11),
    ("surface1", 0.22),
    ("surface2", 0.33),
    ("overlay0", 0.45),
    ("overlay1", 0.55),
    ("overlay2", 0.67),
    ("subtext0", 0.78),
    ("subtext1", 0.89),
)


def palette(flavor: str) -> str:
    if flavor not in ("latte", "frappe", "macchiato"):
        flavor = "mocha"
    return read_data(f"themes/{flavor}.css")


def gtk_palette() -> str:
    """flavor = gtk (LOOK-10): shades from the theme's window colours; accents keep mocha's."""
    accents = "".join(
        line + "\n"
        for line in palette("mocha").splitlines()
        if any(line.startswith(f"@define-color {a} ") for a in ACCENTS)
    )
    shades = "".join(f"@define-color {n} mix(@base, @text, {f});\n" for n, f in SHADES)
    # Catppuccin's mantle and crust are 3 and 6 points of lightness below base.
    return (
        "@define-color base @window_bg_color;\n"
        "@define-color text @window_fg_color;\n"
        "@define-color mantle hsl(from @base h s calc(l - 3));\n"
        "@define-color crust hsl(from @base h s calc(l - 6));\n"
        f"{shades}{accents}"
    )


def css(cfg: Config, user_css: str = "") -> str:
    """Palette, accent, background, data/style.css, user CSS, in that order (LOOK-7)."""
    if cfg.flavor == "gtk":
        colours, accent = gtk_palette(), "accent_bg_color"
    else:
        colours = palette(cfg.flavor)
        accent = cfg.accent if cfg.accent in ACCENTS else "mauve"
    return (
        f"{colours}\n@define-color accent @{accent};\n"
        f"@define-color bg alpha(@base, {cfg.opacity});\n"
        f"{read_data('style.css')}\n{user_css}"
    )


def load(cfg: Config) -> None:
    display = Gdk.Display.get_default()
    if cfg.flavor == "gtk":
        fallback = Gtk.CssProvider()
        fallback.load_from_string(GTK_FALLBACK)
        Gtk.StyleContext.add_provider_for_display(display, fallback, Gtk.STYLE_PROVIDER_PRIORITY_FALLBACK)
    try:
        user_css = (config_dir() / "style.css").read_text(encoding="utf-8")
    except OSError:
        user_css = ""
    provider = Gtk.CssProvider()
    provider.load_from_string(css(cfg, user_css))
    Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
