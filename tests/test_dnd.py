import gi
import pytest

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gtk

from wall_split.dnd import setup_drop_target


def test_drop_target_accepts_copy_and_move():
    # PyGObject's Gtk.init_check() returns True even without a display.
    if not Gtk.init_check() or Gdk.Display.get_default() is None:
        pytest.skip("no display")
    target = setup_drop_target(Gtk.Label(), lambda *a: None, lambda: None)
    actions = target.get_actions()
    assert actions & Gdk.DragAction.COPY
    # Hyprland reports a file manager's drag as MOVE before the target answers; without
    # MOVE here GTK refuses the drop (WIN-3).
    assert actions & Gdk.DragAction.MOVE
