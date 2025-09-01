import itertools
import math
from typing import List, Set, Tuple

def t_subsets(combo: Tuple[int, ...], t: int) -> Set[Tuple[int, ...]]:
    return set(itertools.combinations(combo, t))

def overlap_with_set(combo: Tuple[int, ...], tickets: List[Tuple[int, ...]]) -> int:
    s = 0
    set_c = set(combo)
    for t in tickets:
        s += len(set_c & set(t))
    return s

def popularity_cost(combo: Tuple[int, ...], v: int) -> float:
    k = len(combo)
    arr = sorted(combo)

    # datas (<=31) — só se v>31
    date_pen = 0.0
    if v > 31:
        date_count = sum(1 for x in arr if x <= 31)
        date_pen = max(0.0, (date_count - k / 2) / (k / 2))

    # sequências
    longest_run, cur = 1, 1
    for i in range(1, k):
        if arr[i] == arr[i-1] + 1:
            cur += 1
            longest_run = max(longest_run, cur)
        else:
            cur = 1
    seq_pen = max(0.0, (longest_run - 2) / (k / 3))

    # soma central
    s = sum(arr)
    mu = k * (v + 1) / 2.0
    pop_var = (v**2 - 1) / 12.0
    fpc = (1 - k / v) if v > 1 else 1.0
    var_sum = k * pop_var * fpc
    sd_sum = math.sqrt(max(var_sum, 1e-9))
    z = abs(s - mu) / sd_sum
    sum_pen = 1.0 - math.tanh(z)

    return 1.0 * date_pen + 1.0 * seq_pen + 0.7 * sum_pen

def objective(tickets: List[Tuple[int, ...]], pool: List[int], t: int,
              lam_overlap: float, lam_pop: float, max_number: int) -> float:
    covered = set()
    for c in tickets:
        covered |= t_subsets(c, t)
    ov = 0
    for i in range(len(tickets)):
        for j in range(i + 1, len(tickets)):
            ov += len(set(tickets[i]) & set(tickets[j]))
    pop = sum(popularity_cost(c, max_number) for c in tickets)
    return len(covered) - lam_overlap * ov - lam_pop * pop