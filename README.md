# Game of Peers

Reference implementation, experiments, worked-example tests and exhaustive verification scripts for

> Yaroslav Ryabov, **The Game of Peers: Toward a Credential Algebra for Human-AI Actor Networks**, 2026.
> Preprint: https://doi.org/10.5281/zenodo.19644281

The paper treats human and AI actors as structural peers, each carrying a set of credentials that are
combined by set operators (intersection, union, and two joins) on the edges of a directed actor graph.
This repository contains everything needed to recompute every number in the paper and its supplement.

Pure Python 3 (3.9+), standard library only; `matplotlib` is needed solely by `make_figures.py`.
Every script is self-contained and runs from the repository root:

```bash
python3 test_examples.py            # every number of the worked examples 1-4 (8 tests)
python3 verify_criterion.py         # Theorem 4.2 against exhaustive enumeration
python3 verify_protection.py        # Proposition 4.1 (trees, DAGs)
python3 exp1_prevalence.py          # etc. -- rewrites exp1.json
python3 make_figures.py             # figS1_prevalence.pdf, figS2_scale.pdf
```

Numbers quoted in the supplement (Section S11) are the ones stored in the `exp*.json` files; rerunning a
script overwrites its JSON. Timings differ by machine; rates and counts are reproduced up to the fixed seeds.

## Reference implementation

| File | Content |
|---|---|
| `credalg.py` | Tree semantics of the credential algebra: the four operators (`cap`, `cup`, `lj`, `rj`), pass filters, coalition effective sets (shared outcome), marginal contributions, random instances, and the exact pair-context dynamic program for `Destructive-Actor` (Prop. 6.3). |

Operators act as `op(X, Y)` with `X` the parent's effective set and `Y` the child's intrinsic set:
`cap = X & Y`, `cup = X | Y`, `lj(R) = X | (Y & R)`, `rj(R) = Y | (X & R)`.

## Worked examples (unit tests)

| File | Reproduces |
|---|---|
| `test_examples.py` | Every number of Examples 1–4 (supplement S8–S10): effective sets, all coalition values (all 63 of Example 4), marginal contributions, at-target values, Shapley values, the strategic-distortion and relevance-filter variants. Run directly or with `pytest`. |

## Computational evaluation (supplement S11)

| File | Output | Paper |
|---|---|---|
| `exp1_prevalence.py` | `exp1.json` | Fig. S1(a): fraction of ever-destructive actors vs filter density |
| `exp1b_redundancy.py` | `exp1b.json` | Fig. S1(b): random vs protected redundancy |
| `exp2_scale.py` | `exp2.json` | Fig. S2(a): audit time vs number of actors |
| `exp3_fpt.py` | `exp3.json` | DP vs brute-force cross-check; DP timings |
| `exp3b_fpt_growth.py` | `exp3b.json` | Fig. S2(b): exact detection time vs number of credentials |
| `exp4_shapley.py` | `exp4.json` | Shapley sampling error vs exact value |
| `make_figures.py` | `figS1_prevalence.pdf`, `figS2_scale.pdf` | the two figures of S11 |

## Exhaustive verification of the stated results

Each script compares a theorem with exhaustive enumeration over all coalitions of small random instances
and prints the number of checks and violations (all zero).

| File | Result checked |
|---|---|
| `verify_criterion.py` | Thm. 4.2 (destructive-intermediary criterion, loss set `L`, per-child form) |
| `verify_protection.py` | Prop. 4.1 (credential protection) on trees and DAGs |
| `verify_protection_general.py` | Lemma S2 (entry), Prop. S1 (protection beyond trees: exact on DAGs, sufficient on cycles, the three-cycle counterexample), the SAT necklace of Prop. 4.3 |
| `verify_modular_mcact.py` | Prop. 5.3 (pure equilibria under modular preferences, all four operators) and Prop. 6.6 (MCAC-T prefix algorithm) |
| `verify_agg_indep_cycles.py` | Prop. S6 (aggregator independence of the preserving regime) on cyclic graphs |

## Semantics implemented

Rooted tree; an actor that is a component root of the coalition's forest contributes its intrinsic set,
every other member contributes `op(parent_effective_set, own_intrinsic_set)`; the coalition effective set is
the union of the members' effective sets; coalition value is its cardinality unless a script says otherwise.
`verify_protection_general.py` implements the least-solution semantics on arbitrary directed graphs.

## Citing

See `CITATION.cff` (GitHub renders it as a "Cite this repository" button). Please cite the paper for the
results and this repository for the code.

## License

MIT — see `LICENSE`.
