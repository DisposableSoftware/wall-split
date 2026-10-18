from dataclasses import dataclass

COMMON_RATIOS: list[tuple[str, float]] = [
    ("16:9", 16 / 9),
    ("21:9", 21 / 9),
    ("16:10", 16 / 10),
    ("4:3", 4 / 3),
    ("5:4", 5 / 4),
    ("32:9", 32 / 9),
    ("1:1", 1.0),
]


@dataclass
class Pairing:
    left_label: str
    right_label: str
    cut_x: int


def _ratio_matches(actual: float, ratio: float, tolerance: float) -> bool:
    return abs(actual - ratio) / ratio <= tolerance


def viable_pairings(W: int, H: int, tolerance: float = 0.02) -> list[Pairing]:
    from wall_split.split import cut_x_for_left_ratio, right_ratio_for_cut

    if H == 0:
        return []

    pairings: list[Pairing] = []

    for left_label, left_ratio in COMMON_RATIOS:
        x = cut_x_for_left_ratio(W, H, left_ratio)
        right_ratio = right_ratio_for_cut(W, H, x)

        for right_label, right_ref in COMMON_RATIOS:
            if _ratio_matches(right_ratio, right_ref, tolerance):
                pairings.append(Pairing(left_label, right_label, x))
                break

    # Prefer 16:9+16:9 at the top when viable
    for i, p in enumerate(pairings):
        if p.left_label == "16:9" and p.right_label == "16:9":
            pairings.pop(i)
            pairings.insert(0, p)
            break

    return pairings


def pairing_index_for_cut(pairings: list[Pairing], cut_x: int) -> int:
    """Index of the pairing at *cut_x*, or len(pairings) for the "Custom" entry after them."""
    for i, p in enumerate(pairings):
        if p.cut_x == cut_x:
            return i
    return len(pairings)
