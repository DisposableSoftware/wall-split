from wall_split.pairings import viable_pairings, pairing_index_for_cut, COMMON_RATIOS, Pairing


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


def _has(pairings, left, right):
    return any(p.left_label == left and p.right_label == right for p in pairings)


def test_right_side_within_two_percent_matches():
    # Left 16:9 at H=1000 is x=1778; a right side of 1812 px is 1.9% above 16:9.
    assert _has(viable_pairings(1778 + 1812, 1000), "16:9", "16:9")


def test_right_side_beyond_two_percent_does_not_match():
    # 1815 px is 2.1% above 16:9.
    assert not _has(viable_pairings(1778 + 1815, 1000), "16:9", "16:9")


def test_square_source_has_no_pairings():
    assert viable_pairings(1000, 1000) == []


def test_cut_on_a_pairing_selects_it():
    pairings = viable_pairings(5120, 1440)
    assert pairing_index_for_cut(pairings, pairings[1].cut_x) == 1


def test_cut_off_every_pairing_selects_custom():
    pairings = viable_pairings(5120, 1440)
    assert pairing_index_for_cut(pairings, 2561) == len(pairings)
    assert pairing_index_for_cut([], 500) == 0
