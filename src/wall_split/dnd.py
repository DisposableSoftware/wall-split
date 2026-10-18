from gi.repository import Gtk, Gdk, Gio, GLib, GdkPixbuf


def setup_drop_target(widget: Gtk.Widget, on_image_loaded, on_rejected) -> Gtk.DropTarget:
    target = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
    target.connect("drop", _on_drop, on_image_loaded, on_rejected)
    widget.add_controller(target)
    return target


def _on_drop(widget, value: Gdk.FileList, x, y, on_image_loaded, on_rejected):
    files = value.get_files()
    if not files:
        on_rejected()
        return False
    return load_file(files[0], on_image_loaded, on_rejected)


def load_file(file: Gio.File, on_image_loaded, on_rejected) -> bool:
    """Returns False at once for a non-image name; a decode failure arrives later as on_rejected."""
    content_type = Gio.content_type_guess(file.get_basename(), None)[0]

    if not content_type.startswith("image/"):
        on_rejected()
        return False

    def on_decoded(_source, result):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_stream_finish(result)
        except GLib.GError:
            on_rejected()
            return
        on_image_loaded(pixbuf, file)

    def on_opened(_file, result):
        try:
            stream = file.read_finish(result)
        except GLib.GError:
            on_rejected()
            return
        GdkPixbuf.Pixbuf.new_from_stream_async(stream, None, on_decoded)

    file.read_async(GLib.PRIORITY_DEFAULT, None, on_opened)
    return True
