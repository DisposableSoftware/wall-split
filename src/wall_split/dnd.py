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
    content_type = Gio.content_type_guess(file.get_basename(), None)[0]

    if not content_type.startswith("image/"):
        on_rejected()
        return False

    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(file.get_path())
    except GLib.GError:
        on_rejected()
        return False

    on_image_loaded(pixbuf, file)
    return True
