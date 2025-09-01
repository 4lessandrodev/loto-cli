import random
import itertools
from dataclasses import dataclass
from typing import List, Set, Tuple
from .rules import valid_combo
from .metrics import t_subsets, overlap_with_set, popularity_cost, objective

@dataclass
class GraspParams:
    sample_candidates: int = 600
    rcl_fraction: float = 0.2
    local_search_iters: int = 300
    swap_trials_per_iter: int = 40

def build_initial_solution(pool: List[int], k: int, *,
                           max_number: int, t: int, qtd_jogos: int, seed: int,
                           min_even: int, max_even: int, bins: int, min_bins_hit: int,
                           mod_constraints,
                           lam_overlap: float, lam_pop: float,
                           grasp: GraspParams) -> Tuple[List[Tuple[int, ...]], Set[Tuple[int, ...]]]:
    random.seed(seed)
    tickets: List[Tuple[int, ...]] = []
    uncovered: Set[Tuple[int, ...]] = set(itertools.combinations(sorted(pool), t))

    while len(tickets) < qtd_jogos and uncovered:
        candidates: List[Tuple[int, ...]] = []
        tries = 0
        while len(candidates) < grasp.sample_candidates and tries < grasp.sample_candidates * 20:
            tries += 1
            c = tuple(sorted(random.sample(pool, k)))
            if not valid_combo(c, min_even=min_even, max_even=max_even,
                               bins=bins, max_number=max_number, min_bins_hit=min_bins_hit,
                               mod_constraints=mod_constraints):
                continue
            candidates.append(c)

        if not candidates:
            # relaxa modularidade
            while len(candidates) < max(50, grasp.sample_candidates // 2) and tries < grasp.sample_candidates * 50:
                tries += 1
                c = tuple(sorted(random.sample(pool, k)))
                from .rules import even_odd_ok, range_spread_ok
                if even_odd_ok(c, min_even, max_even) and range_spread_ok(c, bins, max_number, min_bins_hit):
                    candidates.append(c)
            if not candidates:
                break

        scored = []
        for c in candidates:
            cov_gain = len(t_subsets(c, t) & uncovered)
            ov = overlap_with_set(c, tickets)
            pop = popularity_cost(c, max_number)
            score = cov_gain - lam_overlap * ov - lam_pop * pop
            scored.append((score, c))

        scored.sort(reverse=True, key=lambda x: x[0])
        rcl_size = max(1, int(len(scored) * grasp.rcl_fraction))
        chosen = random.choice(scored[:rcl_size])[1]

        tickets.append(chosen)
        uncovered -= t_subsets(chosen, t)

    return tickets, uncovered

def local_search(tickets: List[Tuple[int, ...]], pool: List[int], k: int, *,
                 t: int, lam_overlap: float, lam_pop: float, max_number: int,
                 seed: int, grasp: GraspParams,
                 min_even: int, max_even: int, bins: int, min_bins_hit: int, mod_constraints) -> List[Tuple[int, ...]]:
    random.seed(seed + 1)
    best = tickets[:]
    best_val = objective(best, pool, t, lam_overlap, lam_pop, max_number)
    pool_set = set(pool)

    for _ in range(grasp.local_search_iters):
        improved = False
        for _ in range(grasp.swap_trials_per_iter):
            if not best:
                break
            idx = random.randrange(len(best))
            cur = set(best[idx])
            not_in = list(pool_set - cur)
            if not not_in:
                continue
            out = random.choice(list(cur))
            inn = random.choice(not_in)
            new = tuple(sorted((cur - {out}) | {inn}))
            if not valid_combo(new, min_even=min_even, max_even=max_even,
                               bins=bins, max_number=max_number, min_bins_hit=min_bins_hit,
                               mod_constraints=mod_constraints):
                continue
            cand = best[:]
            cand[idx] = new
            val = objective(cand, pool, t, lam_overlap, lam_pop, max_number)
            if val > best_val:
                best, best_val = cand, val
                improved = True
                break
        if not improved:
            # shaking leve
            if not best:
                break
            idx = random.randrange(len(best))
            tries = 0
            while tries < 2000:
                tries += 1
                c = tuple(sorted(random.sample(pool, k)))
                if valid_combo(c, min_even=min_even, max_even=max_even,
                               bins=bins, max_number=max_number, min_bins_hit=min_bins_hit,
                               mod_constraints=mod_constraints):
                    cand = best[:]
                    cand[idx] = c
                    val = objective(cand, pool, t, lam_overlap, lam_pop, max_number)
                    if val > best_val:
                        best, best_val = cand, val
                        break
    return best