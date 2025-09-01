import math
from typing import List, Tuple

def even_odd_ok(combo: Tuple[int, ...], min_even: int, max_even: int) -> bool:
    evens = sum(1 for x in combo if x % 2 == 0)
    return min_even <= evens <= max_even

def range_spread_ok(combo: Tuple[int, ...], bins: int, max_number: int, min_bins_hit: int) -> bool:
    if bins <= 0:
        return True
    width = math.ceil(max_number / bins)
    hit = set((x - 1) // width for x in combo)
    return len(hit) >= min_bins_hit

def modular_diversity_ok(combo: Tuple[int, ...], mod_constraints: List[Tuple[int, int]]) -> bool:
    for m, min_classes in mod_constraints:
        classes = {x % m for x in combo}
        if len(classes) < min_classes:
            return False
    return True

def valid_combo(combo: Tuple[int, ...], *, min_even: int, max_even: int,
                bins: int, max_number: int, min_bins_hit: int,
                mod_constraints: List[Tuple[int, int]]) -> bool:
    return (even_odd_ok(combo, min_even, max_even)
            and range_spread_ok(combo, bins, max_number, min_bins_hit)
            and modular_diversity_ok(combo, mod_constraints))