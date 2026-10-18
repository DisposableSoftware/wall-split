from gi.repository import Gtk, Gio, GLib


def show_export_dialog(window: Gtk.ApplicationWindow, pixbuf, cut_x: int, source_w: int, source_h: int) -> None:
    dialog = Gtk.FileDialog()

    def _on_chosen(dialog, result):
        try:
            file = dialog.save_finish(result)
        except GLib.GError:
            return

        base_no_ext = _stem(file.get_basename() or "wallpaper")
        directory = file.get_parent()

        right_start = min(cut_x, source_w - 1)
        outputs = [
            (pixbuf.new_subpixbuf(0, 0, cut_x, source_h), directory.get_child(f"{base_no_ext}-left.png")),
            (pixbuf.new_subpixbuf(right_start, 0, source_w - right_start, source_h), directory.get_child(f"{base_no_ext}-right.png")),
        ]
        _save_all(outputs, lambda message: _show_error(window, message))

    dialog.set_initial_name("wallpaper.png")
    dialog.save(window, None, _on_chosen)


def _save_all(outputs, on_error) -> None:
    if not outputs:
        return
    (part, target), rest = outputs[0], outputs[1:]

    def on_closed(stream, result):
        try:
            stream.close_finish(result)
        except GLib.GError as e:
            on_error(e.message)
            return
        _save_all(rest, on_error)

    def on_saved(_part, result, stream):
        try:
            part.save_to_stream_finish(result)
        except GLib.GError as e:
            on_error(e.message)
            return
        stream.close_async(GLib.PRIORITY_DEFAULT, None, on_closed)

    def on_opened(_target, result):
        try:
            stream = target.replace_finish(result)
        except GLib.GError as e:
            on_error(e.message)
            return
        part.save_to_streamv_async(stream, "png", [], [], None, on_saved, stream)

    target.replace_async(None, False, Gio.FileCreateFlags.REPLACE_DESTINATION, GLib.PRIORITY_DEFAULT, None, on_opened)


def _stem(name: str) -> str:
    idx = name.rfind(".")
    if idx == -1:
        return name
    return name[:idx]


def _show_error(window: Gtk.ApplicationWindow, message: str) -> None:
    dialog = Gtk.AlertDialog.new(message)
    dialog.show(window)
