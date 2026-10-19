import cairo
from gi.repository import Gtk, Gdk, GdkPixbuf


class PreviewArea(Gtk.DrawingArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pixbuf = None
        self.cut_x_frac = 0.5
        self.mode = "split"
        self.set_draw_func(self._draw)

    def set_mode(self, mode: str):
        self.mode = mode
        self.queue_draw()

    def set_image(self, pixbuf: GdkPixbuf.Pixbuf, cut_x: int, source_w: int):
        self.pixbuf = pixbuf
        if source_w > 0:
            self.cut_x_frac = cut_x / source_w
        else:
            self.cut_x_frac = 0.5
        self.queue_draw()

    def set_cut_fraction(self, frac: float):
        self.cut_x_frac = max(0.0, min(1.0, frac))
        self.queue_draw()

    def clear(self):
        self.pixbuf = None
        self.cut_x_frac = 0.5
        self.queue_draw()

    def _draw(self, da: Gtk.DrawingArea, cr: cairo.Context, width: int, height: int):
        if not da.pixbuf or width <= 0 or height <= 0:
            return

        src_w = da.pixbuf.get_width()
        src_h = da.pixbuf.get_height()

        scale_x = width / src_w
        scale_y = height / src_h
        scale = min(scale_x, scale_y)

        draw_w = int(src_w * scale)
        draw_h = int(src_h * scale)
        offset_x = (width - draw_w) / 2
        offset_y = (height - draw_h) / 2

        cr.save()
        cr.translate(offset_x, offset_y)
        cr.scale(scale, scale)
        Gdk.cairo_set_source_pixbuf(cr, da.pixbuf, 0, 0)
        cr.paint()
        cr.restore()

        if da.mode != "split":
            return

        cut_screen_x = offset_x + da.cut_x_frac * draw_w
        cr.set_source_rgb(1.0, 0.0, 0.0)
        cr.set_line_width(2)
        cr.move_to(cut_screen_x, offset_y)
        cr.line_to(cut_screen_x, offset_y + draw_h)
        cr.stroke()
