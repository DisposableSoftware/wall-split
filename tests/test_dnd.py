import gi
import pytest

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gtk

from wall_split.dnd import setup_drop_target


@pytest.mark.xfail(strict=True, reason="WIN-3: fails until fixed")
def test_drop_target_accepts_copy_and_move():
    if not Gtk.init_check():
        pytest.skip("no display")
    target = setup_drop_target(Gtk.Label(), lambda *a: None, lambda: None)
    actions = target.get_actions()
    assert actions & Gdk.DragAction.COPY
    # Hyprland reports a file manager's drag as MOVE before the target answers; without
    # MOVE here GTK refuses the drop (WIN-3).
    assert actions & Gdk.DragAction.MOVE
