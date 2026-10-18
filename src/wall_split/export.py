from gi.repository import Gtk, Gio


def show_export_dialog(window: Gtk.ApplicationWindow, pixbuf, cut_x: int, source_w: int, source_h: int) -> None:
    dialog = Gtk.FileDialog()

    def _on_exported(dialog, result):
        try:
            file = dialog.save_finish(result)
            base_name = file.get_basename() or "wallpaper"
            directory = file.get_parent() if file else Gio.File.new_for_path(".")

            left_pb = pixbuf.new_subpixbuf(0, 0, cut_x, source_h)
            right_start = min(cut_x, source_w - 1)
            right_w = source_w - right_start
            right_pb = pixbuf.new_subpixbuf(right_start, 0, right_w, source_h)

            base_no_ext = _stem(base_name)

            left_file = directory.get_child(f"{base_no_ext}-left.png")
            right_file = directory.get_child(f"{base_no_ext}-right.png")

            left_pb.savev(left_file.get_path(), "png", [], [])
            right_pb.savev(right_file.get_path(), "png", [], [])

        except Exception as e:
            _show_error(window, str(e))

    dialog.set_initial_name("wallpaper.png")
    dialog.save(window, None, _on_exported)


def _stem(name: str) -> str:
    idx = name.rfind(".")
    if idx == -1:
        return name
    return name[:idx]


def _show_error(window: Gtk.ApplicationWindow, message: str) -> None:
    dialog = Gtk.AlertDialog.new(message)
    dialog.show(window)
