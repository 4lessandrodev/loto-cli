from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class LotoSpec:
    name: str
    max_number: int
    k_min: int
    k_max: int
    pool_size: int
    t_cover: int
    min_even: int
    max_even: int
    bins: int
    min_bins_hit: int
    mod_constraints: List[Tuple[int, int]]  # (modulo, min_classes_distintas)

LOTTERIES: Dict[str, LotoSpec] = {
    "megasena": LotoSpec(
        name="megasena", max_number=60, k_min=6, k_max=20,
        pool_size=17, t_cover=3, min_even=2, max_even=4,
        bins=6, min_bins_hit=3, mod_constraints=[(3, 2)]
    ),
    "lotofacil": LotoSpec(
        name="lotofacil", max_number=25, k_min=15, k_max=20,
        pool_size=22, t_cover=4, min_even=6, max_even=9,
        bins=5, min_bins_hit=4, mod_constraints=[(3, 2)]
    ),
    "quina": LotoSpec(
        name="quina", max_number=80, k_min=5, k_max=15,
        pool_size=18, t_cover=3, min_even=2, max_even=3,
        bins=8, min_bins_hit=4, mod_constraints=[(3, 2)]
    ),
}