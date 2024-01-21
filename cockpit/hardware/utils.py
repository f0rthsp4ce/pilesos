def value_map(value: float, min1: float, max1: float, min2: int, max2: float) -> float:
    """Map one value range to another. Equivalent to Arduino Framework map() function.

    Example:
        # 0..255 -> -10..10
        value_map(98, 0, 255, -10, 10)
    """
    left_span = max1 - min1
    right_span = max2 - min2
    value_scaled = float(value - min1) / float(left_span)
    return min2 + (value_scaled * right_span)
