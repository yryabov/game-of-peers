"""Brute-force checks of Proposition 5.3 (modular preferences) and Proposition 6.6 (MCAC-T on trees).
 (3) Prop 5.3: modular V_i, D_i => pure NE exists for each of the four operators (incl. joins).
 (4) Prop 6.6: MCAC-T optimum on a tree with a mixture of all four operators equals the best
     'target + contiguous prefix of ancestors' coalition (no credential reaches t from below/aside)."""
import sys, os, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credalg import op_apply, random_tree

rng = random.Random(42)

# ---------- (3) ----------
def pure_ne_exists(sa, sb, op, wa, wb, da, db):
    Sa = [frozenset(x) for k in range(len(sa)+1) for x in itertools.combinations(sorted(sa), k)]
    Sb = [frozenset(x) for k in range(len(sb)+1) for x in itertools.combinations(sorted(sb), k)]
    def ua(x, y): eff = op_apply(op, x, y); return sum(wa[c] for c in eff) - sum(da[c] for c in x)
    def ub(x, y): eff = op_apply(op, x, y); return sum(wb[c] for c in eff) - sum(db[c] for c in y)
    for x in Sa:
        for y in Sb:
            if all(ua(x, y) >= ua(x2, y) for x2 in Sa) and all(ub(x, y) >= ub(x, y2) for y2 in Sb):
                return True
    return False

fails = tested = 0
for _ in range(3000):
    m = rng.choice([1, 2, 3, 4]); C = list(range(m))
    sa = frozenset(c for c in C if rng.random() < 0.6); sb = frozenset(c for c in C if rng.random() < 0.6)
    kind = rng.choice(['cap', 'cup', 'lj', 'rj']); R = frozenset(c for c in C if rng.random() < 0.5)
    wa = {c: rng.randint(0, 3) for c in C}; wb = {c: rng.randint(0, 3) for c in C}
    da = {c: rng.randint(0, 3) for c in C}; db = {c: rng.randint(0, 3) for c in C}
    tested += 1
    if not pure_ne_exists(sa, sb, (kind, R), wa, wb, da, db):
        fails += 1; print('NO PURE NE', kind, R, sa, sb, wa, wb, da, db)
print(f'(3) modular preferences, four operators: {tested} random games, pure NE missing in {fails}')

# ---------- (4) ----------
def eff_at(S, t, parent, sigma, ops):
    # effective set of t in coalition S on a tree: chain of ancestors inside S
    chain = [t]; p = parent[t]
    while p is not None and p in S: chain.append(p); p = parent[p]
    E = sigma[chain[-1]]
    for v in reversed(chain[:-1]): E = op_apply(ops[v], E, sigma[v])
    return E

def eff_at_full(S, t, children, sigma, ops, root=0):
    # independent implementation: full downward pass over the coalition
    E = {}
    stack = [(root, None)]
    while stack:
        v, ctx = stack.pop()
        if v in S:
            E[v] = sigma[v] if ctx is None else op_apply(ops[v], ctx, sigma[v]); nctx = E[v]
        else: nctx = None
        for c in children[v]: stack.append((c, nctx))
    return E[t]

bad = tested = 0
for _ in range(600):
    n = rng.choice([4, 5, 6, 7]); m = rng.choice([2, 3, 4]); C = frozenset(range(m))
    parent, children = random_tree(n, rng)
    sigma = {v: frozenset(c for c in C if rng.random() < 0.5) for v in range(n)}
    ops = {v: (rng.choice(['cap', 'cup', 'lj', 'rj']), frozenset(c for c in C if rng.random() < 0.5)) for v in range(1, n)}
    cost = {v: rng.randint(1, 5) for v in range(n)}
    t = rng.randrange(n); Q = frozenset(c for c in C if rng.random() < 0.5)
    others = [v for v in range(n) if v != t]
    best_all = None
    for k in range(len(others) + 1):
        for S in itertools.combinations(others, k):
            S = frozenset(S) | {t}
            if eff_at_full(S, t, children, sigma, ops) >= Q:
                c = sum(cost[v] for v in S)
                best_all = c if best_all is None else min(best_all, c)
    # prefix algorithm
    anc = []; p = parent[t]
    while p is not None: anc.append(p); p = parent[p]
    best_pref = None
    for k in range(len(anc) + 1):
        S = frozenset(anc[:k]) | {t}
        if eff_at(S, t, parent, sigma, ops) >= Q:
            c = sum(cost[v] for v in S)
            best_pref = c if best_pref is None else min(best_pref, c)
    tested += 1
    if best_all != best_pref:
        bad += 1; print('MISMATCH', best_all, best_pref)
print(f'(4) MCAC-T: {tested} random mixed-operator trees, prefix optimum != brute-force optimum in {bad}')
