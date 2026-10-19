import pytest

from wall_split.crop import (
    DEFAULT_MONITOR,
    MIN_HEIGHT,
    Box,
    box_ratio,
    crop_rects,
    cut_fraction,
    fit_box,
    monitor_sizes,
    move,
    reshape,
    resize_corner,
)

QHD = (2560, 1440)
UW = (3440, 1440)


def inside(box, W, H):
    eps = 1e-9
    return box.x >= -eps and box.y >= -eps and box.x + box.w <= W + eps and box.y + box.h <= H + eps


# CROP-2


def test_ratio_is_the_sum_of_the_monitor_ratios():
    assert box_ratio(QHD, QHD) == pytest.approx(32 / 9)
    assert box_ratio(QHD, UW) == pytest.approx(2560 / 1440 + 3440 / 1440)


def test_cut_sits_at_the_left_monitors_share():
    assert cut_fraction(QHD, QHD) == pytest.approx(0.5)
    assert cut_fraction(QHD, UW) == pytest.approx(2560 / (2560 + 3440))


def test_reshape_keeps_the_centre_and_height():
    W, H = 8000, 3000
    box = Box(1000, 500, 1600 * 32 / 9, 1600)
    out = reshape(box, box_ratio(QHD, UW), W, H)
    assert out.h == pytest.approx(1600)
    assert out.w / out.h == pytest.approx(box_ratio(QHD, UW))
    assert out.x + out.w / 2 == pytest.approx(box.x + box.w / 2)
    assert out.y + out.h / 2 == pytest.approx(box.y + box.h / 2)


def test_reshape_shrinks_and_shifts_to_stay_inside():
    W, H = 5120, 1440
    box = fit_box(W, H, box_ratio(QHD, QHD))
    out = reshape(box, box_ratio(UW, UW), W, H)
    assert out.w / out.h == pytest.approx(box_ratio(UW, UW))
    assert inside(out, W, H)
    assert out.w == pytest.approx(W)


# CROP-3


def test_fit_box_is_the_largest_centred_box_in_a_wide_image():
    box = fit_box(8000, 1440, 32 / 9)
    assert box.h == 1440 and box.w == pytest.approx(5120)
    assert box.x == pytest.approx((8000 - 5120) / 2) and box.y == 0


def test_fit_box_is_the_largest_centred_box_in_a_tall_image():
    box = fit_box(3840, 2160, 32 / 9)
    assert box.w == 3840 and box.h == pytest.approx(1080)
    assert box.x == 0 and box.y == pytest.approx(540)


# CROP-4 (pure parts)


def test_move_is_clamped_to_the_image():
    W, H = 6000, 3000
    box = Box(100, 100, 3200, 900)
    assert move(box, -500, -500, W, H) == Box(0, 0, 3200, 900)
    assert move(box, 10000, 10000, W, H) == Box(W - 3200, H - 900, 3200, 900)
    assert move(box, 50, 20, W, H) == Box(150, 120, 3200, 900)


@pytest.mark.parametrize("corner", ["top-left", "top-right", "bottom-left", "bottom-right"])
def test_corner_resize_keeps_the_opposite_corner_and_ratio(corner):
    W, H, ratio = 6000, 3000, 32 / 9
    box = Box(1000, 1000, 1800 * ratio / 2, 900)
    sign_x = -1 if corner.endswith("left") else 1
    sign_y = -1 if corner.startswith("top") else 1
    out = resize_corner(box, corner, 200 * sign_x, 100 * sign_y, ratio, W, H)
    assert out.w / out.h == pytest.approx(ratio)
    assert out.h > box.h
    opposite = {
        "top-left": (box.x + box.w, box.y + box.h),
        "top-right": (box.x, box.y + box.h),
        "bottom-left": (box.x + box.w, box.y),
        "bottom-right": (box.x, box.y),
    }[corner]
    got = {
        "top-left": (out.x + out.w, out.y + out.h),
        "top-right": (out.x, out.y + out.h),
        "bottom-left": (out.x + out.w, out.y),
        "bottom-right": (out.x, out.y),
    }[corner]
    assert got == pytest.approx(opposite)


def test_corner_resize_stops_at_the_image_edge():
    W, H, ratio = 6000, 3000, 32 / 9
    box = Box(1000, 1000, 1600, 450)
    out = resize_corner(box, "bottom-right", 100000, 100000, ratio, W, H)
    assert inside(out, W, H)
    assert out.w / out.h == pytest.approx(ratio)
    assert out.x == 1000 and out.y == 1000


def test_corner_resize_never_goes_below_the_minimum_height():
    W, H, ratio = 6000, 3000, 32 / 9
    box = Box(1000, 1000, 1600, 450)
    out = resize_corner(box, "bottom-right", -100000, -100000, ratio, W, H)
    assert out.h == pytest.approx(MIN_HEIGHT)
    assert out.x == 1000 and out.y == 1000


# CROP-6 (pure parts)


def test_crop_rects_split_the_box_at_the_cut():
    box = Box(160, 45, 4800, 1350)
    left, right = crop_rects(box, QHD, QHD)
    assert left == (160, 45, 2400, 1350)
    assert right == (2560, 45, 2400, 1350)
    left, right = crop_rects(box, QHD, UW)
    assert left[2] + right[2] == 4800
    assert left[2] == round(4800 * 2560 / 6000)


# CROP-1 (pure parts)


def test_monitor_sizes_are_the_two_leftmost_in_device_pixels():
    monitors = [(2560, 0, 1720, 720, 2.0), (0, 0, 2560, 1440, 1.0), (6000, 0, 1920, 1080, 1.0)]
    assert monitor_sizes(monitors) == ((2560, 1440), (3440, 1440))


def test_monitor_sizes_round_fractional_scales():
    assert monitor_sizes([(0, 0, 2048, 1152, 1.25)])[0] == (2560, 1440)


def test_missing_monitors_get_the_default():
    assert monitor_sizes([(0, 0, 1920, 1080, 2.0)]) == ((3840, 2160), DEFAULT_MONITOR)
    assert monitor_sizes([]) == (DEFAULT_MONITOR, DEFAULT_MONITOR)
