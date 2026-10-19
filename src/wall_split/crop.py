from dataclasses import dataclass

MIN_HEIGHT = 64
DEFAULT_MONITOR = (2560, 1440)
MAX_MONITOR_SIDE = 16384


@dataclass
class Box:
    x: float
    y: float
    w: float
    h: float


def box_ratio(left: tuple[int, int], right: tuple[int, int]) -> float:
    return left[0] / left[1] + right[0] / right[1]


def cut_fraction(left: tuple[int, int], right: tuple[int, int]) -> float:
    a = left[0] / left[1]
    return a / (a + right[0] / right[1])


def fit_box(W: int, H: int, ratio: float) -> Box:
    if W / H > ratio:
        h = H
        w = H * ratio
    else:
        w = W
        h = W / ratio
    return Box((W - w) / 2, (H - h) / 2, w, h)


def _min_height(W: int, H: int, ratio: float) -> float:
    return min(MIN_HEIGHT, fit_box(W, H, ratio).h)


def _clamp_position(box: Box, W: int, H: int) -> Box:
    x = min(max(box.x, 0), W - box.w)
    y = min(max(box.y, 0), H - box.h)
    return Box(x, y, box.w, box.h)


def reshape(box: Box, ratio: float, W: int, H: int) -> Box:
    cx, cy = box.x + box.w / 2, box.y + box.h / 2
    biggest = fit_box(W, H, ratio)
    h = min(max(box.h, _min_height(W, H, ratio)), biggest.h)
    w = h * ratio
    return _clamp_position(Box(cx - w / 2, cy - h / 2, w, h), W, H)


def move(box: Box, dx: float, dy: float, W: int, H: int) -> Box:
    return _clamp_position(Box(box.x + dx, box.y + dy, box.w, box.h), W, H)


CORNERS = ("top-left", "top-right", "bottom-left", "bottom-right")


def resize_corner(box: Box, corner: str, dx: float, dy: float, ratio: float, W: int, H: int) -> Box:
    """Moves *corner* of *box* by (dx, dy), keeping the opposite corner fixed and the ratio."""
    left = corner.endswith("left")
    top = corner.startswith("top")
    ax = box.x + box.w if left else box.x
    ay = box.y + box.h if top else box.y
    px = (box.x if left else box.x + box.w) + dx
    py = (box.y if top else box.y + box.h) + dy

    # Follow whichever axis the pointer moved further, measured away from the anchor, so a
    # pointer dragged past the anchor shrinks the box to its minimum instead of flipping it.
    reach_x = ax - px if left else px - ax
    reach_y = ay - py if top else py - ay
    h = max(reach_x / ratio, reach_y)
    room_w = ax if left else W - ax
    room_h = ay if top else H - ay
    h = min(h, room_h, room_w / ratio)
    h = max(h, min(_min_height(W, H, ratio), room_h, room_w / ratio))
    w = h * ratio
    return Box(ax - w if left else ax, ay - h if top else ay, w, h)


def crop_rects(box: Box, left: tuple[int, int], right: tuple[int, int]):
    """Integer source rectangles (x, y, w, h) for the left and right halves of *box*."""
    x, y = round(box.x), round(box.y)
    w, h = round(box.w), round(box.h)
    cut = round(w * cut_fraction(left, right))
    return (x, y, cut, h), (x + cut, y, w - cut, h)


def monitor_sizes(monitors) -> tuple[tuple[int, int], tuple[int, int]]:
    """Left and right monitor sizes in device pixels from (x, y, width, height, scale) in logical
    pixels, taking the two leftmost; missing ones get DEFAULT_MONITOR."""
    ordered = sorted(monitors, key=lambda m: (m[0], m[1]))
    sizes = [(round(w * s), round(h * s)) for _x, _y, w, h, s in ordered[:2]]
    while len(sizes) < 2:
        sizes.append(DEFAULT_MONITOR)
    return sizes[0], sizes[1]
