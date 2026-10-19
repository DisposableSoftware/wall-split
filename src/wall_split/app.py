import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gtk, Gdk, Gio, GLib

from wall_split.pairings import viable_pairings, pairing_index_for_cut, Pairing
from wall_split.preview import PreviewArea
from wall_split.dnd import setup_drop_target, load_file
from wall_split.export import crop_parts, show_export_dialog, split_parts
from wall_split.split import cut_x_for_left_ratio, right_ratio_for_cut
from wall_split.crop import MAX_MONITOR_SIDE, Box, box_ratio, crop_rects, cut_fraction, fit_box, monitor_sizes, reshape


REJECT_CSS = b".rejected { outline: 3px solid #e01b24; outline-offset: -3px; }"
REJECT_FLASH_MS = 1500


class SplitWindow(Gtk.ApplicationWindow):
    def __init__(self, app, **kwargs):
        super().__init__(application=app, title="Wall Split", default_width=960, default_height=640, **kwargs)

        css = Gtk.CssProvider()
        css.load_from_bytes(GLib.Bytes.new(REJECT_CSS))
        Gtk.StyleContext.add_provider_for_display(self.get_display(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self._reject_timeout = 0

        self.source_w = 0
        self.source_h = 0
        self.pixbuf = None
        self.cut_x = 0
        self.pairings: list[Pairing] = []
        self.box: Box | None = None

        self.mode = "split"

        self.split_btn = Gtk.ToggleButton(label="Split", active=True)
        self.crop_btn = Gtk.ToggleButton(label="Crop", group=self.split_btn)
        self.crop_btn.connect("toggled", self._on_mode_toggled)
        mode_box = Gtk.Box(css_classes=["linked"], valign=Gtk.Align.CENTER)
        mode_box.append(self.split_btn)
        mode_box.append(self.crop_btn)

        self.export_btn = Gtk.Button.new_with_label("Export...")
        self.export_btn.set_valign(Gtk.Align.CENTER)
        self.export_btn.set_action_name("win.export")

        self.export_action = Gio.SimpleAction.new("export", None)
        self.export_action.connect("activate", self._on_export)
        self.export_action.set_enabled(False)
        self.add_action(self.export_action)
        for name, button in (("split-mode", self.split_btn), ("crop-mode", self.crop_btn)):
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", lambda _a, _p, b=button: b.set_active(True))
            self.add_action(action)

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
        self.preview.on_box_changed = self._set_box
        self.stack.add_named(self.preview, "preview")

        self.stack.set_visible_child_name("hint")
        setup_drop_target(self.stack, self._on_image_loaded, self._on_rejected)

        controls = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        controls.set_margin_top(12)
        controls.set_margin_bottom(12)
        controls.set_margin_start(12)
        controls.set_margin_end(12)
        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        top_row.append(mode_box)
        top_row.append(Gtk.Box(hexpand=True))
        top_row.append(self.export_btn)
        self.controls_stack = Gtk.Stack(hexpand=True)
        controls.append(top_row)
        controls.append(self.controls_stack)

        controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.controls_stack.add_named(controls_box, "split")
        self.controls_stack.add_named(self._build_crop_controls(), "crop")

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

        self.slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 1)
        self.slider.set_digits(0)
        self.slider.set_draw_value(True)
        self.slider.set_format_value_func(self._format_slider_value)
        self.slider.set_hexpand(True)
        self.slider.connect("value-changed", self._on_slider_changed)
        controls_box.append(self.slider)

        main_box.append(self.stack)
        main_box.append(controls)
        self.set_child(main_box)

    def _build_crop_controls(self) -> Gtk.Widget:
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, valign=Gtk.Align.CENTER)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        page.append(row)
        self.monitor_fields = []
        for side, (w, h) in zip(("Left", "Right"), self._connected_monitor_sizes()):
            if side == "Right":
                row.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL, margin_start=6, margin_end=6))
            row.append(Gtk.Label(label=side))
            width = Gtk.SpinButton.new_with_range(1, MAX_MONITOR_SIDE, 1)
            height = Gtk.SpinButton.new_with_range(1, MAX_MONITOR_SIDE, 1)
            width.set_value(w)
            height.set_value(h)
            row.append(width)
            row.append(Gtk.Label(label="×"))
            row.append(height)
            self.monitor_fields.append((width, height))
            width.connect("value-changed", self._on_monitor_changed)
            height.connect("value-changed", self._on_monitor_changed)
        self.box_label = Gtk.Label(label="Box: —", halign=Gtk.Align.START)
        page.append(self.box_label)
        return page

    def _connected_monitor_sizes(self):
        monitors = self.get_display().get_monitors()
        found = []
        for i in range(monitors.get_n_items()):
            monitor = monitors.get_item(i)
            g = monitor.get_geometry()
            found.append((g.x, g.y, g.width, g.height, monitor.get_scale()))
        return monitor_sizes(found)

    def _on_mode_toggled(self, button):
        self.mode = "crop" if self.crop_btn.get_active() else "split"
        self.controls_stack.set_visible_child_name(self.mode)
        self.preview.set_mode(self.mode)
        if self.mode == "crop":
            self._place_box()

    def _monitors(self):
        return tuple((w.get_value_as_int(), h.get_value_as_int()) for w, h in self.monitor_fields)

    def _place_box(self):
        if not self.pixbuf:
            return
        self._set_box(fit_box(self.source_w, self.source_h, box_ratio(*self._monitors())))

    def _set_box(self, box: Box):
        self.box = box
        self.preview.set_crop(box, cut_fraction(*self._monitors()), box_ratio(*self._monitors()))
        self.box_label.set_text(f"Box: {round(box.w)}×{round(box.h)} at {round(box.x)}, {round(box.y)}")

    def _on_monitor_changed(self, _field):
        if self.box:
            self._set_box(reshape(self.box, box_ratio(*self._monitors()), self.source_w, self.source_h))

    def _on_rejected(self):
        self.stack.add_css_class("rejected")
        if self._reject_timeout:
            GLib.source_remove(self._reject_timeout)
        self._reject_timeout = GLib.timeout_add(REJECT_FLASH_MS, self._end_reject_flash)

    def _end_reject_flash(self):
        self.stack.remove_css_class("rejected")
        self._reject_timeout = 0
        return GLib.SOURCE_REMOVE

    def _on_image_loaded(self, pixbuf, gio_file):
        self.pixbuf = pixbuf
        self.source_w = pixbuf.get_width()
        self.source_h = pixbuf.get_height()
        self.set_title(f"{gio_file.get_basename()} — Wall Split")

        self.slider.set_range(1, max(self.source_w - 1, 1))
        self.slider.set_increments(1, max(self.source_w // 100, 1))

        self.pairings = viable_pairings(self.source_w, self.source_h)
        self._refresh_dropdown()

        if self.pairings:
            self.cut_x = self.pairings[0].cut_x
        else:
            self.cut_x = self.source_w // 2

        self.slider.set_value(self.cut_x)

        self.preview.set_image(pixbuf, self.cut_x, self.source_w)
        self.stack.set_visible_child_name("preview")
        self.export_action.set_enabled(True)
        self._update_ratio_labels()
        if self.mode == "crop":
            self._place_box()

    def _refresh_dropdown(self):
        items = [f"{p.left_label} + {p.right_label}" for p in self.pairings]
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
        new_x = max(1, min(round(slider.get_value()), self.source_w - 1))
        if new_x != self.cut_x:
            self.cut_x = new_x
            self.preview.set_image(self.pixbuf, self.cut_x, self.source_w)

        self.pairing_dropdown.set_selected(pairing_index_for_cut(self.pairings, self.cut_x))
        self._update_ratio_labels()

    def _format_slider_value(self, scale, value):
        if not self.source_h:
            return ""
        return f"{round(value) / self.source_h:.2f}"

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

    def _on_export(self, _action, _param):
        pixbuf = self.pixbuf
        if self.mode == "crop" and self.box:
            monitors = self._monitors()
            rects = crop_rects(self.box, *monitors, self.source_w, self.source_h)
            show_export_dialog(self, lambda: crop_parts(pixbuf, rects, monitors))
        else:
            cut_x = self.cut_x
            show_export_dialog(self, lambda: split_parts(pixbuf, cut_x))


class WallSplitApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="io.github.DisposableSoftware.WallSplit", flags=Gio.ApplicationFlags.HANDLES_OPEN)

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.set_accels_for_action("win.export", ["<Ctrl>e"])
        self.set_accels_for_action("win.split-mode", ["<Ctrl>1"])
        self.set_accels_for_action("win.crop-mode", ["<Ctrl>2"])

    def _window(self) -> SplitWindow:
        return self.get_active_window() or SplitWindow(self)

    def do_activate(self):
        self._window().present()

    def do_open(self, files, n_files, hint):
        win = self._window()
        if files:
            load_file(files[0], win._on_image_loaded, win._on_rejected)
        win.present()


def main():
    app = WallSplitApp()
    app.run(sys.argv)
