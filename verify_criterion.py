"""Brute-force check of the Destructive Intermediary Criterion (Theorem 4.2 of the main text).

For random rooted trees, operator assignments (all four fundamental operators), credential
assignments, coalitions S and joiners x, whenever the theorem's structural condition holds
(every filtered child of x in S is isolated in F_S or connected downward only through union
edges), we check
  (a) Delta_x(S) = |eff_T(x) \ eff_S| - |L|,          with L, N as defined in the theorem;
  (b) L is exactly eff_S \ eff_T (the destroyed credentials);
  (c) the per-child form |L| = sum_i |U_i \ (eff_T(x) u pi_i)| under its proviso.
It also reports how the accounting behaves when the condition is violated (two-sided bounds).
Run:  python3 verify_criterion.py
"""
import os, sys, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credalg import op_apply, pi_of, random_tree

def effective_sets(S, children, sigma, ops, root=0):
    E = {}; stack = [(root, None)]
    while stack:
        v, ctx = stack.pop()
        if v in S:
            E[v] = sigma[v] if ctx is None else frozenset(op_apply(ops[v], ctx, sigma[v])); nctx = E[v]
        else: nctx = None
        for c in children[v]: stack.append((c, nctx))
    return E

def s_subtree(b, S, children):
    """members of S strictly below b reachable inside F_S, with the edge kinds used"""
    out = []; stack = [b]
    while stack:
        v = stack.pop()
        for c in children[v]:
            if c in S: out.append(c); stack.append(c)
    return out

rng = random.Random(2026)
checked = viol_a = viol_b = viol_c = 0; applicable_c = 0
outside = 0; bound_viol = 0
for trial in range(4000):
    n = rng.choice([4, 5, 6, 7, 8]); m = rng.choice([3, 4, 5]); C = frozenset(range(m))
    parent, children = random_tree(n, rng)
    sigma = {v: frozenset(c for c in C if rng.random() < 0.5) for v in range(n)}
    ops = {v: (rng.choice(['cap', 'cup', 'lj', 'rj']), frozenset(c for c in C if rng.random() < 0.5)) for v in range(1, n)}
    x = rng.randrange(n)
    others = [v for v in range(n) if v != x]
    S = frozenset(v for v in others if rng.random() < 0.6)
    if not S: continue
    T = S | {x}
    ES = effective_sets(S, children, sigma, ops); ET = effective_sets(T, children, sigma, ops)
    effS = frozenset().union(*ES.values()); effT = frozenset().union(*ET.values())
    delta = len(effT) - len(effS)
    kids = [c for c in children[x] if c in S]
    filtered = [c for c in kids if pi_of(ops[c], C) != C]
    # structural condition
    ok = True; D = []
    for b in filtered:
        below = s_subtree(b, S, children)
        if any(ops[d][0] != 'cup' for d in below): ok = False
        D += below
    if not ok:
        outside += 1
        # two-sided bounds of Remark (beyond trees): gains within eff_T(x)\eff_S, losses within filtered subtrees' credentials
        gain = effT - effS; effTx = ET[x]
        if not gain <= (effTx - effS): bound_viol += 1
        continue
    checked += 1
    effTx = ET[x]
    Dset = set(D)
    N = frozenset().union(*[ES[a] for a in S if a not in filtered and a not in Dset] or [frozenset()]) | frozenset().union(*[sigma[d] for d in Dset] or [frozenset()])
    Ub = frozenset().union(*[sigma[b] for b in filtered] or [frozenset()])
    surv = frozenset().union(*[sigma[b] & pi_of(ops[b], C) for b in filtered] or [frozenset()])
    L = Ub - (N | effTx | surv)
    if delta != len(effTx - effS) - len(L): viol_a += 1
    if L != effS - effT: viol_b += 1
    # per-child form
    isolated = all(not s_subtree(b, S, children) for b in filtered)
    if isolated and filtered:
        held_elsewhere = lambda c, b: any(c in ES[a] for a in S if a != b)
        proviso = all(not (c in sigma[b1] and c in sigma[b2] and not any(c in ES[a] for a in S if a not in (b1, b2)))
                      for b1, b2 in itertools.combinations(filtered, 2) for c in C)
        if proviso:
            applicable_c += 1
            tot = 0
            for b in filtered:
                U = sigma[b] - frozenset().union(*[ES[a] for a in S if a != b] or [frozenset()])
                tot += len(U - (effTx | pi_of(ops[b], C)))
            if tot != len(L): viol_c += 1
print(f'condition satisfied: {checked} (x,S) pairs; violations of (a) formula: {viol_a}, (b) L = eff_S \\ eff_T: {viol_b}; '
      f'per-child form applicable: {applicable_c}, violations: {viol_c}')
print(f'condition violated: {outside} pairs; gain-bound eff_T\\eff_S <= eff_T(x)\\eff_S violated: {bound_viol}')
