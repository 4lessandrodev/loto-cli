import argparse
import os
from typing import Optional, List
from .specs import LOTTERIES
from .history import load_history_csv
from .pool import build_stratified_pool
from .grasp import GraspParams, build_initial_solution, local_search
from .export import export_tickets_csv_k

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="loto-cli",
        description="Gerador de jogos com GRASP (cobertura t, baixa sobreposição e anti-popularidade)."
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gerar", help="Gerar jogos")
    g.add_argument("qtd_jogos", type=int, help="Quantidade de jogos a gerar")
    g.add_argument("qtd_numeros", type=int, help="Quantidade de números por jogo (k)")
    g.add_argument("loteria", type=str, choices=list(LOTTERIES.keys()),
                   help="loteria: megasena | lotofacil | quina")

    # entradas
    g.add_argument("--historico", type=str, default=None, help="CSV de histórico (opcional)")
    g.add_argument("--reweight-bias", action="store_true",
                   help="(Opcional) aplicar leve reweight se houver viés no histórico")

    # pool/diversidade
    g.add_argument("--pool-size", type=int, default=None, help="Tamanho do pool (default do preset)")
    g.add_argument("--bins", type=int, default=None, help="Qtde de faixas 1..N para estratificar")
    g.add_argument("--min-bins-hit", type=int, default=None, help="Mínimo de faixas ocupadas por bilhete")

    # regras de combinação
    g.add_argument("--min-even", type=int, default=None, help="Mínimo de pares por bilhete")
    g.add_argument("--max-even", type=int, default=None, help="Máximo de pares por bilhete")

    # cobertura t
    g.add_argument("--t-cover", type=int, default=None, help="Tamanho do subconjunto para cobertura (t)")

    # pesos do objetivo
    g.add_argument("--lam-overlap", type=float, default=0.6, help="Peso da penalização por sobreposição")
    g.add_argument("--lam-pop", type=float, default=0.8, help="Peso do custo de popularidade")

    # GRASP
    g.add_argument("--sample-candidates", type=int, default=600, help="Candidatos amostrados por iteração")
    g.add_argument("--rcl-frac", type=float, default=0.2, help="Fração da lista restrita (0<frac<=1)")
    g.add_argument("--local-iters", type=int, default=300, help="Iterações de busca local")
    g.add_argument("--swap-trials", type=int, default=40, help="Tentativas de troca por iteração")

    # saída
    g.add_argument("--out", type=str, default=None, help="Arquivo CSV de saída (opcional)")
    g.add_argument("--stdout", action="store_true", help="Imprimir jogos no console")

    return p

def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "gerar":
        spec = LOTTERIES[args.loteria]

        # aplica overrides
        pool_size = args.pool_size if args.pool_size is not None else spec.pool_size
        bins = args.bins if args.bins is not None else spec.bins
        min_bins_hit = args.min_bins_hit if args.min_bins_hit is not None else spec.min_bins_hit
        min_even = args.min_even if args.min_even is not None else spec.min_even
        max_even = args.max_even if args.max_even is not None else spec.max_even
        t_cover = args.t_cover if args.t_cover is not None else spec.t_cover

        # validações
        if not (spec.k_min <= args.qtd_numeros <= spec.k_max):
            parser.error(f"k (qtd_numeros) deve estar entre {spec.k_min} e {spec.k_max} para {spec.name}.")
        if pool_size < args.qtd_numeros:
            parser.error("pool-size não pode ser menor que qtd_numeros.")
        if not (0 < args.rcl_frac <= 1.0):
            parser.error("rcl-frac deve estar em (0, 1].")

        # histórico (opcional)
        draws = None
        if args.historico:
            if not os.path.exists(args.historico):
                parser.error(f"Histórico não encontrado: {args.historico}")
            draws = load_history_csv(args.historico)

        # pool
        pool = build_stratified_pool(
            v=spec.max_number, pool_size=pool_size, bins=bins, seed=123,
            draws=draws, reweight_bias=args.reweight_bias
        )

        # GRASP params
        grasp = GraspParams(
            sample_candidates=args.sample_candidates,
            rcl_fraction=args.rcl_frac,
            local_search_iters=args.local_iters,
            swap_trials_per_iter=args.swap_trials
        )

        # construção
        tickets, _uncovered = build_initial_solution(
            pool=pool, k=args.qtd_numeros, max_number=spec.max_number, t=t_cover,
            qtd_jogos=args.qtd_jogos, seed=123,
            min_even=min_even, max_even=max_even, bins=bins, min_bins_hit=min_bins_hit,
            mod_constraints=spec.mod_constraints,
            lam_overlap=args.lam_overlap, lam_pop=args.lam_pop, grasp=grasp
        )

        # complementa se faltou
        seen = set(tickets)
        tries = 0
        while len(tickets) < args.qtd_jogos and tries < 200000:
            tries += 1
            import random
            c = tuple(sorted(random.sample(pool, args.qtd_numeros)))
            if c in seen:
                continue
            from .rules import valid_combo
            if valid_combo(c, min_even=min_even, max_even=max_even, bins=bins,
                           max_number=spec.max_number, min_bins_hit=min_bins_hit,
                           mod_constraints=spec.mod_constraints):
                tickets.append(c)
                seen.add(c)

        # busca local
        tickets = local_search(
            tickets=tickets, pool=pool, k=args.qtd_numeros, t=t_cover,
            lam_overlap=args.lam_overlap, lam_pop=args.lam_pop, max_number=spec.max_number,
            seed=123, grasp=grasp,
            min_even=min_even, max_even=max_even, bins=bins, min_bins_hit=min_bins_hit,
            mod_constraints=spec.mod_constraints
        )

        # saída
        header = (f"# {spec.name} | jogos={len(tickets)} | k={args.qtd_numeros} | "
                  f"pool={len(pool)} | t={t_cover} | lam_overlap={args.lam_overlap} | lam_pop={args.lam_pop}")
        if args.stdout or not args.out:
            print(header)
            print(f"# pool: {pool}")
            for i, t in enumerate(tickets, 1):
                print(f"Jogo {i:02d}: " + " ".join(f"{n:02d}" for n in t))

        if args.out:
            export_tickets_csv_k(tickets, args.out, k=args.qtd_numeros)
            print(f"\n[OK] {len(tickets)} jogos salvos em: {args.out}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())