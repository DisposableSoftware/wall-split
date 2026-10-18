def cut_x_for_left_ratio(W: int, H: int, left_ratio: float) -> int:
    x = round(H * left_ratio)
    return max(0, min(x, W))


def right_ratio_for_cut(W: int, H: int, x: int) -> float:
    if H == 0:
        return 0.0
    remain = W - x
    if remain <= 0:
        return 0.0
    return remain / H


def snap_to_ratio(x: int, W: int, H: int, ratio: float, tolerance: float = 0.02) -> int | None:
    """Check if current cut position x corresponds to *ratio* within tolerance.
       Returns the snapped x-value, or None if it doesn't match."""
    if H == 0:
        return None
    ideal_x = round(H * ratio)
    actual_ratio_at_ideal = ideal_x / H
    # Accept the snap only if the rounded position is close enough to the target ratio
    if abs(actual_ratio_at_ideal - ratio) <= tolerance and abs(x - ideal_x) / max(ideal_x, 1) <= tolerance:
        return ideal_x
    return None


def split_sizes(W: int, H: int, x: int) -> tuple[tuple[int, int], tuple[int, int]]:
    x = max(0, min(x, W))
    return (x, H), (W - x, H)
