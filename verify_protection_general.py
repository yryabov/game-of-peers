"""Re-examination of the protection criterion beyond trees.

Facts checked here (lfp semantics of Def. dag-eff, shared outcome, union aggregation):
 (K) 'kill characterization': c NOT in ecred_T  <=>  every holder u of c in T satisfies
       u not in O, par_T(u) nonempty, and every parent p in par_T(u) has c not in pi(p,u).
 (D) on DAGs: set map monotone <=> every holder protected, where
       prot(h) = h in O  or  h has no parents  or  for every parent p: c in pi(p,h) or (c in sigma(p) and prot(p)).
 (S) on general graphs: every holder protected (least fixed point) => monotone  (sufficiency only).
 (X) explicit 3-cycle where all holders are unprotected yet the set map is monotone (necessity fails on cycles).
 (G) SAT gadget on a cyclic graph with |C|=1: killing coalition exists <=> formula satisfiable.
"""
import sys, random, itertools
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from credalg import op_apply, pi_of

def lfp_union(S, edges, ops, sigma, O):
    src = {a for a in S if not any((p, a) in edges for p in S)}
    OS = (O & S) | src
    E = {a: frozenset() for a in S}
    while True:
        E2 = {}
        for a in S:
            acc = set(sigma[a]) if a in OS else set()
            for p in S:
                if (p, a) in edges: acc |= op_apply(ops[(p, a)], E[p], sigma[a])
            E2[a] = frozenset(acc)
        if E2 == E: return E
        E = E2

def eff_union(S, edges, ops, sigma, O):
    return frozenset().union(*lfp_union(S, edges, ops, sigma, O).values()) if S else frozenset()

def killed_all(T, c, edges, ops, sigma, O, C):
    for u in T:
        if c not in sigma[u]: continue
        if u in O: return False
        par = [p for p in T if (p, u) in edges]
        if not par: return False
        if any(c in pi_of(ops[(p, u)], C) for p in par): return False
    return True

def protected_lfp(parents, sigma, ops, C, O, actors):
    prot = {(h, c): False for h in actors for c in C}
    while True:
        new = {}
        for h in actors:
            for c in C:
                if h in O: v = True
                else:
                    v = all((c in pi_of(ops[(p, h)], C)) or (c in sigma[p] and prot[(p, c)]) for p in parents[h])
                new[(h, c)] = v
        if new == prot: return prot
        prot = new

def random_graph(rng, n, m, dag, p_edge=0.5, p_origin=0.3):
    C = frozenset(range(m)); actors = list(range(n))
    if dag: edges = {(i, j) for i in actors for j in actors if i < j and rng.random() < p_edge}
    else:   edges = {(i, j) for i in actors for j in actors if i != j and rng.random() < p_edge}
    parents = {a: [p for p in actors if (p, a) in edges] for a in actors}
    ops = {e: (rng.choice(['cap', 'lj', 'rj', 'cup']), frozenset(c for c in C if rng.random() < 0.5)) for e in edges}
    sigma = {a: frozenset(c for c in C if rng.random() < 0.5) for a in actors}
    O = frozenset(a for a in actors if rng.random() < p_origin)
    return C, actors, edges, parents, ops, sigma, O

# ---- (K) kill characterization, general graphs ----
rng = random.Random(7); viol = tested = 0
for _ in range(600):
    C, actors, edges, parents, ops, sigma, O = random_graph(rng, rng.choice([2, 3, 4, 5]), rng.choice([1, 2, 3]), dag=False)
    for k in range(1, len(actors) + 1):
        for T in itertools.combinations(actors, k):
            T = frozenset(T); e = eff_union(T, edges, ops, sigma, O)
            for c in C:
                tested += 1
                if (c not in e) != killed_all(T, c, edges, ops, sigma, O, C):
                    viol += 1; print('K-VIOL', T, c, edges, ops, sigma, O)
print(f'(K) kill characterization: {tested} checks, violations {viol}')

# ---- (D) DAGs: monotone <=> all holders protected ----
rng = random.Random(8); viol = tested = mono_cnt = 0
for _ in range(1500):
    n = rng.choice([3, 4, 5, 6, 7]); m = rng.choice([1, 2, 3])
    C, actors, edges, parents, ops, sigma, O = random_graph(rng, n, m, dag=True, p_edge=rng.choice([0.3, 0.5, 0.8]))
    subsets = [frozenset(s) for k in range(n + 1) for s in itertools.combinations(actors, k)]
    eff = {S: eff_union(S, edges, ops, sigma, O) for S in subsets}
    prot = protected_lfp(parents, sigma, ops, C, O, actors)
    for c in C:
        holders = [h for h in actors if c in sigma[h]]
        all_prot = all(prot[(h, c)] for h in holders)
        never_lost = all((c not in eff[S]) or (c in eff[S | {x}]) for S in subsets for x in actors if x not in S)
        tested += 1
        if all_prot != never_lost: viol += 1; print('D-VIOL', c, edges, ops, sigma, O)
    mono_cnt += all(eff[S] <= eff[S | {x}] for S in subsets for x in actors if x not in S)
print(f'(D) DAGs: {tested} credential checks over 1500 instances ({mono_cnt} monotone), violations {viol}')

# ---- (S) general graphs: protected => never lost; count how often the converse fails ----
rng = random.Random(9); viol = tested = conv_fail = 0
for _ in range(2000):
    n = rng.choice([2, 3, 4, 5]); m = rng.choice([1, 2])
    C, actors, edges, parents, ops, sigma, O = random_graph(rng, n, m, dag=False, p_edge=rng.choice([0.4, 0.6, 0.9]), p_origin=rng.choice([0.0, 0.3]))
    subsets = [frozenset(s) for k in range(n + 1) for s in itertools.combinations(actors, k)]
    eff = {S: eff_union(S, edges, ops, sigma, O) for S in subsets}
    prot = protected_lfp(parents, sigma, ops, C, O, actors)
    for c in C:
        holders = [h for h in actors if c in sigma[h]]
        if not holders: continue
        all_prot = all(prot[(h, c)] for h in holders)
        never_lost = all((c not in eff[S]) or (c in eff[S | {x}]) for S in subsets for x in actors if x not in S)
        tested += 1
        if all_prot and not never_lost: viol += 1; print('S-VIOL', c, edges, ops, sigma, O)
        if never_lost and not all_prot: conv_fail += 1
print(f'(S) general graphs: {tested} checks; sufficiency violations {viol}; converse fails in {conv_fail} cases')

# ---- (X) explicit 3-cycle ----
C = frozenset({0}); actors = [1, 2, 3]
edges = {(2, 1), (3, 2), (1, 3), (1, 2)}
ops = {(2, 1): ('cap', frozenset()), (3, 2): ('cap', frozenset()), (1, 3): ('cap', frozenset()), (1, 2): ('cup', frozenset())}
sigma = {a: frozenset({0}) for a in actors}; O = frozenset()
parents = {a: [p for p in actors if (p, a) in edges] for a in actors}
subsets = [frozenset(s) for k in range(4) for s in itertools.combinations(actors, k)]
eff = {S: eff_union(S, edges, ops, sigma, O) for S in subsets}
mono = all(eff[S] <= eff[S | {x}] for S in subsets for x in actors if x not in S)
prot = protected_lfp(parents, sigma, ops, C, O, actors)
print(f'(X) 3-cycle: monotone={mono}, protected={[prot[(a,0)] for a in actors]}  (expected: True, all False)')

# ---- (G) SAT gadget, cyclic, |C| = 1 ----
def gadget(clauses):
    """clauses: list of lists of (var, sign). Builds necklace u_1 -> copies_1 -> u_2 -> ... -> u_m -> copies_m -> u_1."""
    m = len(clauses); nodes = []; edges = {}; sigma = {}
    u = [f'u{j}' for j in range(m)]
    copies = [[f'l{j}_{k}' for k in range(len(cl))] for j, cl in enumerate(clauses)]
    for j in range(m):
        for k, (var, sign) in enumerate(clauses[j]):
            edges[(copies[j][k], u[j])] = ('cap', frozenset())          # copy -> clause node (dangerous)
            edges[(u[(j + 1) % m], copies[j][k])] = ('cap', frozenset())  # next clause node -> copy (dangerous)
    # exclusion: for complementary copies, one good edge (parent = copy in later clause, or any fixed order)
    allc = [(j, k, clauses[j][k]) for j in range(m) for k in range(len(clauses[j]))]
    for (j, k, (v, s)) in allc:
        for (j2, k2, (v2, s2)) in allc:
            if v == v2 and s != s2 and (j2, k2) > (j, k):
                edges[(copies[j2][k2], copies[j][k])] = ('cup', frozenset())
    nodes = u + [c for row in copies for c in row]
    sigma = {a: frozenset({0}) for a in nodes}
    return nodes, set(edges.keys()), edges, sigma

def satisfiable(clauses, nvars):
    for bits in itertools.product([0, 1], repeat=nvars):
        if all(any(bits[v] == s for (v, s) in cl) for cl in clauses): return True
    return False

rng = random.Random(3); agree = total = 0
for _ in range(60):
    nvars = rng.choice([1, 2, 3]); m = rng.choice([1, 2, 3])
    clauses = []
    for _ in range(m):
        vs = rng.sample(range(nvars), min(nvars, rng.choice([1, 2])))
        clauses.append([(v, rng.choice([0, 1])) for v in vs])
    nodes, edges, ops, sigma = gadget(clauses)
    if len(nodes) > 11: continue
    C = frozenset({0}); O = frozenset()
    losable = False
    for k in range(1, len(nodes) + 1):
        for T in itertools.combinations(nodes, k):
            T = frozenset(T)
            if 0 not in eff_union(T, edges, ops, sigma, O):   # T holds only holders, so any T with c absent is a loss
                losable = True; break
        if losable: break
    total += 1; agree += (losable == satisfiable(clauses, nvars))
    if losable != satisfiable(clauses, nvars): print('G-MISMATCH', clauses, losable)
print(f'(G) SAT gadget: {agree}/{total} instances where (credential losable) == (formula satisfiable)')
