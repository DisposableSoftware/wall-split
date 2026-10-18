import sys
from gi.repository import Gtk, Gdk, Gio

from wall_split.pairings import viable_pairings, Pairing
from wall_split.preview import PreviewArea
from wall_split.dnd import setup_drop_target
from wall_split.export import show_export_dialog
from wall_split.split import cut_x_for_left_ratio, right_ratio_for_cut


class SplitWindow(Gtk.ApplicationWindow):
    def __init__(self, app, **kwargs):
        super().__init__(application=app, title="Wall Split", default_width=960, default_height=640, **kwargs)

        self.source_w = 0
        self.source_h = 0
        self.pixbuf = None
        self.cut_x = 0
        self.pairings: list[Pairing] = []

        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)
        self.file_label = Gtk.Label(label="No image loaded", halign=Gtk.Align.START)
        header.pack_start(self.file_label)

        self.export_btn = Gtk.Button.new_with_label("Export...")
        self.export_btn.connect("clicked", self._on_export)
        self.export_btn.set_sensitive(False)
        header.pack_end(self.export_btn)
        self.set_titlebar(header)

        # Main layout: preview fills space, controls below
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Stack switches between the drop hint and the preview
        self.stack = Gtk.Stack(hexpand=True, vexpand=True)

        drop_label = Gtk.Label(
            label="Drag and drop an image here",
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
        )
        self.stack.add_named(drop_label, "hint")

        self.preview = PreviewArea(hexpand=True, vexpand=True)
        self.stack.add_named(self.preview, "preview")

        self.stack.set_visible_child_name("hint")
        setup_drop_target(self.stack, self._on_image_loaded)

        # Controls row
        controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        controls_box.set_margin_top(12)
        controls_box.set_margin_bottom(12)
        controls_box.set_margin_start(12)
        controls_box.set_margin_end(12)

        pairing_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.pairing_model = Gtk.StringList()
        self.pairing_dropdown = Gtk.DropDown(model=self.pairing_model)
        self.pairing_dropdown.set_hexpand(True)
        self.pairing_dropdown.connect("notify::selected", self._on_pairing_selected)
        pairing_row.append(self.pairing_dropdown)

        self.left_ratio_label = Gtk.Label(label="Left: —", halign=Gtk.Align.START)
        self.right_ratio_label = Gtk.Label(label="Right: —", halign=Gtk.Align.END, hexpand=True)
        pairing_row.append(self.left_ratio_label)
        pairing_row.append(self.right_ratio_label)

        controls_box.append(pairing_row)

        self.slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 0.01)
        self.slider.set_digits(4)
        self.slider.set_hexpand(True)
        self.slider.connect("value-changed", self._on_slider_changed)
        controls_box.append(self.slider)

        main_box.append(self.stack)
        main_box.append(controls_box)
        self.set_child(main_box)

    def _on_image_loaded(self, pixbuf, gio_file):
        self.pixbuf = pixbuf
        self.source_w = pixbuf.get_width()
        self.source_h = pixbuf.get_height()

        self.file_label.set_text(gio_file.get_basename())

        self.pairings = viable_pairings(self.source_w, self.source_h)
        self._refresh_dropdown()

        # Default cut: first pairing or center
        if self.pairings:
            self.cut_x = self.pairings[0].cut_x
        else:
            self.cut_x = self.source_w // 2

        self.slider.set_range(1, max(self.source_w - 1, 1))
        self.slider.set_value(self.cut_x)

        self.preview.set_image(pixbuf, self.cut_x, self.source_w)
        self.stack.set_visible_child_name("preview")
        self.export_btn.set_sensitive(True)
        self._update_ratio_labels()

    def _refresh_dropdown(self):
        items = []
        for p in self.pairings:
            items.append(f"{p.left_label} + {p.right_label}")
        if not items:
            items.append("Custom")

        self.pairing_model = Gtk.StringList.new(items)
        self.pairing_dropdown.set_model(self.pairing_model)
        self.pairing_dropdown.set_selected(0)

    def _on_pairing_selected(self, dropdown, pspec):
        idx = dropdown.get_selected()
        if idx < len(self.pairings):
            p = self.pairings[idx]
            self.cut_x = p.cut_x
            self.slider.set_value(self.cut_x)
            self.preview.set_image(self.pixbuf, self.cut_x, self.source_w)
            self._update_ratio_labels()

    def _on_slider_changed(self, slider):
        val = slider.get_value()
        new_x = max(1, min(int(val), self.source_w - 1))
        if new_x != self.cut_x:
            self.cut_x = new_x
            self.preview.set_image(self.pixbuf, self.cut_x, self.source_w)

        # Check if slider position matches a pairing — if not, select "Custom"
        match = False
        for i, p in enumerate(self.pairings):
            if p.cut_x == self.cut_x:
                self.pairing_dropdown.set_selected(i)
                match = True
                break

        if not match and len(self.pairings):
            # Select the "Custom" entry (last position if we appended it, but our model doesn't have it by default)
            # Instead just update labels to show custom ratios
            pass

        self._update_ratio_labels()

    def _update_ratio_labels(self):
        if not self.pixbuf:
            return

        left_ratio = self.cut_x / self.source_h if self.source_h else 0
        right_ratio = right_ratio_for_cut(self.source_w, self.source_h, self.cut_x)

        self.left_ratio_label.set_text(
            f"Left: {self.cut_x}×{self.source_h} ({left_ratio:.2f})"
        )
        self.right_ratio_label.set_text(
            f"Right: {self.source_w - self.cut_x}×{self.source_h} ({right_ratio:.2f})"
        )

    def _on_export(self, btn):
        show_export_dialog(self, self.pixbuf, self.cut_x, self.source_w, self.source_h)


class WallSplitApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="lol.weston.wall-split", flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        if not self.get_active_window():
            win = SplitWindow(self)
        win.present()


def main():
    app = WallSplitApp()
    app.run(sys.argv)
