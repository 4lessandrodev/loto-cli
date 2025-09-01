import csv
from collections import Counter
from typing import List

def _parse_row(row: dict) -> List[int]:
    nums: List[int] = []
    if "numbers" in row and row["numbers"]:
        parts = row["numbers"].replace(",", " ").split()
        for p in parts:
            p = p.strip()
            if p.isdigit():
                nums.append(int(p))
    else:
        for key in sorted(row.keys()):
            val = row[key]
            if val is None or f"{val}".strip() == "":
                continue
            try:
                nums.append(int(val))
            except Exception:
                pass
    return sorted(set(nums))

def load_history_csv(path: str) -> List[List[int]]:
    draws: List[List[int]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        seen = set()
        for row in reader:
            nums = _parse_row(row)
            if not nums:
                continue
            t = tuple(nums)
            if t in seen:
                continue
            seen.add(t)
            draws.append(nums)
    return draws

def compute_frequencies(draws: List[List[int]], max_number: int) -> Counter:
    c = Counter()
    for d in draws:
        c.update(d)
    for n in range(1, max_number + 1):
        _ = c[n]
    return c