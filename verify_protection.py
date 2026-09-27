"""Brute-force check of the 'credential protection' criterion (holdings-level dichotomy).

Tree, shared-outcome semantics (coalition_union of credalg.py).
Def. Holder h of c is c-PROTECTED iff h is the root, or c in pi(par(h),h), or
     (c in sigma(par(h)) and par(h) is c-protected).
Claims:
 (A) the set map S -> sigma_hat_S is monotone (no credential ever lost) iff every holder
     of every credential is protected;
 (B) per credential: c is never lost iff every holder of c is protected;
 (C) sufficient, per coalition: if S contains a protected holder of c then c in sigma_hat_S.
DAG version (lfp with union aggregation over parents, origins = all actors that are sources
in the induced subgraph, O = empty):
 (A') monotone iff every holder h of c, for EVERY parent p of h: c in pi(p,h) or
      (c in sigma(p) and p is c-protected).
"""
import sys, random, itertools
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from credalg import op_apply, pi_of, random_instance, coalition_union

def protected_tree(h, c, parent, sigma, ops, C, memo):
    key = (h, c)
    if key in memo: return memo[key]
    p = parent[h]
    if p is None: r = True
    elif c in pi_of(ops[h], C): r = True
    elif c in sigma[p]: r = protected_tree(p, c, parent, sigma, ops, C, memo)
    else: r = False
    memo[key] = r
    return r

rng = random.Random(11)
tested = viol = 0; mono_cnt = 0
for trial in range(400):
    n = rng.choice([4, 5, 6, 7]); m = rng.choice([2, 3, 4])
    f = rng.choice([0.0, 0.3, 0.6, 1.0]); r = rng.choice([1, 2, 3])
    parent, children, sigma, ops, C = random_instance(n, m, f, r, rng, filter_kinds=('cap', 'lj', 'rj', 'cup'))
    actors = list(range(n))
    subsets = [frozenset(s) for k in range(n + 1) for s in itertools.combinations(actors, k)]
    eff = {S: frozenset(coalition_union(S, children, sigma, ops)) for S in subsets}
    memo = {}
    # per-credential loss
    for c in C:
        holders = [h for h in actors if c in sigma[h]]
        all_prot = all(protected_tree(h, c, parent, sigma, ops, C, memo) for h in holders)
        never_lost = all((c not in eff[S]) or (c in eff[S | {x}]) for S in subsets for x in actors if x not in S)
        tested += 1
        if all_prot != never_lost:
            viol += 1; print('B-VIOLATION', c, parent, sigma, ops)
        # sufficient condition (C)
        prot_holders = [h for h in holders if protected_tree(h, c, parent, sigma, ops, C, memo)]
        for S in subsets:
            if any(h in S for h in prot_holders) and c not in eff[S]:
                viol += 1; print('C-VIOLATION', c, S, parent, sigma, ops)
    # global monotonicity (A)
    mono = all(eff[S] <= eff[S | {x}] for S in subsets for x in actors if x not in S)
    all_prot = all(protected_tree(h, c, parent, sigma, ops, C, memo) for c in C for h in actors if c in sigma[h])
    mono_cnt += mono
    if mono != all_prot:
        viol += 1; print('A-VIOLATION', parent, sigma, ops)
print(f'TREES: {tested} credential checks over 400 instances ({mono_cnt} monotone), violations {viol}')

# ---------------- DAG version (lfp, union aggregation) ----------------
def lfp_union(S, edges, ops, sigma, C):
    src = {a for a in S if not any((p, a) in edges for p in S)}
    E = {a: frozenset() for a in S}
    while True:
        E2 = {}
        for a in S:
            base = sigma[a] if a in src else frozenset()
            acc = set(base)
            for p in S:
                if (p, a) in edges: acc |= op_apply(ops[(p, a)], E[p], sigma[a])
            E2[a] = frozenset(acc)
        if E2 == E: return E
        E = E2

def protected_dag(h, c, parents, sigma, ops, C, memo, stack=()):
    key = (h, c)
    if key in memo: return memo[key]
    if not parents[h]: r = True
    else:
        r = True
        for p in parents[h]:
            if c in pi_of(ops[(p, h)], C): continue
            if c in sigma[p] and protected_dag(p, c, parents, sigma, ops, C, memo): continue
            r = False; break
    memo[key] = r
    return r

rng = random.Random(5)
tested = viol = 0; mono_cnt = 0
for trial in range(400):
    n = rng.choice([3, 4, 5, 6]); m = rng.choice([2, 3])
    C = frozenset(range(m)); actors = list(range(n))
    # random DAG: edges i->j only for i<j
    edges = {(i, j) for i in actors for j in actors if i < j and rng.random() < 0.5}
    parents = {a: [p for p in actors if (p, a) in edges] for a in actors}
    ops = {e: (rng.choice(['cap', 'lj', 'rj', 'cup']), frozenset(c for c in C if rng.random() < 0.5)) for e in edges}
    sigma = {a: frozenset(c for c in C if rng.random() < 0.5) for a in actors}
    subsets = [frozenset(s) for k in range(n + 1) for s in itertools.combinations(actors, k)]
    eff = {}
    for S in subsets:
        E = lfp_union(S, edges, ops, sigma, C)
        eff[S] = frozenset().union(*E.values()) if S else frozenset()
    memo = {}
    for c in C:
        holders = [h for h in actors if c in sigma[h]]
        all_prot = all(protected_dag(h, c, parents, sigma, ops, C, memo) for h in holders)
        never_lost = all((c not in eff[S]) or (c in eff[S | {x}]) for S in subsets for x in actors if x not in S)
        tested += 1
        if all_prot != never_lost:
            viol += 1; print('DAG-B-VIOLATION', c, edges, sigma, ops)
        prot_holders = [h for h in holders if protected_dag(h, c, parents, sigma, ops, C, memo)]
        for S in subsets:
            if any(h in S for h in prot_holders) and c not in eff[S]:
                viol += 1; print('DAG-C-VIOLATION', c, S, edges, sigma, ops)
    mono = all(eff[S] <= eff[S | {x}] for S in subsets for x in actors if x not in S)
    mono_cnt += mono
    all_prot = all(protected_dag(h, c, parents, sigma, ops, C, memo) for c in C for h in actors if c in sigma[h])
    if mono != all_prot:
        viol += 1; print('DAG-A-VIOLATION', edges, sigma, ops)
print(f'DAGS: {tested} credential checks over 400 instances ({mono_cnt} monotone), violations {viol}')
