import csv
from typing import List, Tuple

def export_tickets_csv_k(tickets: List[Tuple[int, ...]], path: str, k: int):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([f"n{i+1}" for i in range(k)])
        for t in tickets:
            if len(t) != k:
                raise ValueError(f"Ticket com {len(t)} números; esperado {k}: {t}")
            w.writerow(list(t))