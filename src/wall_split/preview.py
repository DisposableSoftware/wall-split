import cairo
from gi.repository import Gtk, Gdk, GdkPixbuf

from wall_split.crop import Box

HANDLE = 8


class PreviewArea(Gtk.DrawingArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pixbuf = None
        self.cut_x_frac = 0.5
        self.mode = "split"
        self.box: Box | None = None
        self.box_cut_frac = 0.5
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

    def set_crop(self, box: Box | None, cut_frac: float):
        self.box = box
        self.box_cut_frac = cut_frac
        self.queue_draw()

    def _layout(self, width: int, height: int):
        """Scale and offset that fit the image in the area, preserving aspect."""
        src_w = self.pixbuf.get_width()
        src_h = self.pixbuf.get_height()
        scale = min(width / src_w, height / src_h)
        return scale, (width - src_w * scale) / 2, (height - src_h * scale) / 2

    def _draw(self, da: Gtk.DrawingArea, cr: cairo.Context, width: int, height: int):
        if not da.pixbuf or width <= 0 or height <= 0:
            return

        scale, offset_x, offset_y = self._layout(width, height)
        draw_w = da.pixbuf.get_width() * scale
        draw_h = da.pixbuf.get_height() * scale

        cr.save()
        cr.translate(offset_x, offset_y)
        cr.scale(scale, scale)
        Gdk.cairo_set_source_pixbuf(cr, da.pixbuf, 0, 0)
        cr.paint()
        cr.restore()

        if da.mode == "crop":
            if da.box:
                self._draw_box(cr, scale, offset_x, offset_y, draw_w, draw_h)
            return

        cut_screen_x = offset_x + da.cut_x_frac * draw_w
        cr.set_source_rgb(1.0, 0.0, 0.0)
        cr.set_line_width(2)
        cr.move_to(cut_screen_x, offset_y)
        cr.line_to(cut_screen_x, offset_y + draw_h)
        cr.stroke()

    def _draw_box(self, cr, scale, offset_x, offset_y, draw_w, draw_h):
        b = self.box
        x, y = offset_x + b.x * scale, offset_y + b.y * scale
        w, h = b.w * scale, b.h * scale

        cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        cr.rectangle(offset_x, offset_y, draw_w, draw_h)
        cr.rectangle(x, y, w, h)
        cr.set_source_rgba(0, 0, 0, 0.6)
        cr.fill()

        cr.set_source_rgb(1, 1, 1)
        cr.set_line_width(2)
        cr.rectangle(x, y, w, h)
        cr.stroke()

        cut = x + w * self.box_cut_frac
        cr.set_source_rgb(1.0, 0.0, 0.0)
        cr.move_to(cut, y)
        cr.line_to(cut, y + h)
        cr.stroke()

        cr.set_source_rgb(1, 1, 1)
        for cx, cy in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):
            cr.rectangle(cx - HANDLE / 2, cy - HANDLE / 2, HANDLE, HANDLE)
        cr.fill()
