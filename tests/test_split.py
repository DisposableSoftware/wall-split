from wall_split.split import cut_x_for_left_ratio, right_ratio_for_cut, snap_to_ratio, split_sizes


def test_cut_x_basic():
    W, H = 5120, 1440
    x = cut_x_for_left_ratio(W, H, 16 / 9)
    assert x == round(H * 16 / 9), f"Expected {round(1440*16/9)}, got {x}"


def test_cut_x_clamps():
    W, H = 1920, 1080
    x = cut_x_for_left_ratio(W, H, 5.0)
    assert x == W


def test_cut_zero_height():
    x = cut_x_for_left_ratio(1920, 0, 16 / 9)
    assert x == 0


def test_right_ratio():
    W, H = 5120, 1440
    x = round(H * 16 / 9)
    r = right_ratio_for_cut(W, H, x)
    expected = (W - x) / H
    assert abs(r - expected) < 1e-9


def test_right_ratio_zero_height():
    r = right_ratio_for_cut(100, 0, 50)
    assert r == 0.0


def test_snap_to_ratio_exact():
    W, H = 5120, 1440
    x = round(H * 16 / 9)
    snapped = snap_to_ratio(x, W, H, 16 / 9)
    assert snapped == x


def test_snap_to_ratio_outside_tolerance():
    W, H = 5120, 1440
    x = round(H * 2.0)
    snapped = snap_to_ratio(x, W, H, 16 / 9, tolerance=0.02)
    assert snapped is None


def test_split_sizes():
    W, H = 5120, 1440
    x = round(H * 16 / 9)
    left_size, right_size = split_sizes(W, H, x)
    assert left_size == (x, H)
    assert right_size == (W - x, H)


def test_split_sizes_clamp():
    left_size, right_size = split_sizes(100, 200, 150)
    assert left_size == (100, 200)
    assert right_size == (0, 200)


def test_every_pixel_accounted():
    W, H = 3840, 1080
    for x in range(W + 1):
        left_size, right_size = split_sizes(W, H, x)
        assert left_size[0] + right_size[0] == W
        assert left_size[1] == right_size[1] == H
