import math
import random
from typing import List, Optional
from .history import compute_frequencies

def build_stratified_pool(v: int, pool_size: int, bins: int, seed: int,
                          draws: Optional[List[List[int]]] = None,
                          reweight_bias: bool = False) -> List[int]:
    random.seed(seed)
    all_nums = list(range(1, v + 1))
    if pool_size >= v:
        return all_nums

    width = math.ceil(v / bins)
    per_bin = [pool_size // bins] * bins
    for i in range(pool_size % bins):
        per_bin[i] += 1

    weights = {n: 1.0 for n in all_nums}
    if reweight_bias and draws:
        freq = compute_frequencies(draws, v)
        total_draws = len(draws)
        if total_draws > 0:
            k_guess = len(draws[0])
            expected = total_draws * k_guess / v
            sd = math.sqrt(max(expected, 1e-9))
            for n in all_nums:
                z = (freq[n] - expected) / (sd if sd else 1.0)
                w = 1.0 + max(-0.15, min(0.15, 0.03 * z))
                weights[n] = max(0.1, w)

    pool: List[int] = []
    for b in range(bins):
        start = b * width + 1
        end = min((b + 1) * width, v)
        bucket = list(range(start, end + 1))
        if any(weights[n] != 1.0 for n in bucket):
            chosen: List[int] = []
            candidates = bucket.copy()
            for _ in range(min(per_bin[b], len(candidates))):
                tot = sum(weights[n] for n in candidates)
                r = random.random() * tot
                acc = 0.0
                pick = candidates[-1]
                for n in candidates:
                    acc += weights[n]
                    if acc >= r:
                        pick = n
                        break
                chosen.append(pick)
                candidates.remove(pick)
            pool.extend(chosen)
        else:
            random.shuffle(bucket)
            pool.extend(bucket[:per_bin[b]])

    pool = sorted(set(pool))
    while len(pool) < pool_size:
        pool.append(random.randint(1, v))
        pool = sorted(set(pool))
    return sorted(pool)[:pool_size]