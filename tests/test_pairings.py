from wall_split.pairings import viable_pairings, COMMON_RATIOS, Pairing


def test_32_over_9_gets_169_plus_169():
    W, H = 5120, 1440
    pairings = viable_pairings(W, H)
    assert len(pairings) >= 1
    first = pairings[0]
    assert first.left_label == "16:9" and first.right_label == "16:9"


def test_narrow_image_returns_empty_or_partial():
    W, H = 1920, 1080
    pairings = viable_pairings(W, H)
    for p in pairings:
        assert isinstance(p.cut_x, int)
        assert 0 < p.cut_x < W


def test_pairing_contains_cut_x():
    W, H = 5120, 1440
    pairings = viable_pairings(W, H)
    for p in pairings:
        assert isinstance(p.cut_x, int)
        assert 0 < p.cut_x < W


def test_common_ratios():
    assert ("16:9", 16 / 9) in COMMON_RATIOS
    assert ("4:3", 4 / 3) in COMMON_RATIOS
    assert len(COMMON_RATIOS) >= 5


def test_prefers_169_at_top():
    W, H = 7680, 1440
    pairings = viable_pairings(W, H)
    has_169 = any(p.left_label == "16:9" and p.right_label == "16:9" for p in pairings)
    if has_169:
        assert pairings[0].left_label == "16:9" and pairings[0].right_label == "16:9"
