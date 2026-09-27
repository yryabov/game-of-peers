"""Minimal reference implementation: tree semantics, marginal contributions, FPT exact DA."""
import random
from functools import lru_cache

def op_apply(op, X, Y):
    k, R = op
    if k == 'cap': return X & Y
    if k == 'cup': return X | Y
    if k == 'lj':  return X | (Y & R)
    if k == 'rj':  return Y | (X & R)

def pi_of(op, C):
    k, R = op
    return {'cap': frozenset(), 'cup': C, 'lj': R, 'rj': C}[k]

def random_tree(n, rng):
    parent = {0: None}
    for v in range(1, n): parent[v] = rng.randrange(v)
    children = {v: [] for v in range(n)}
    for v in range(1, n): children[parent[v]].append(v)
    return parent, children

def random_instance(n, m, filter_density, redundancy, rng, filter_kinds=('cap', 'lj')):
    """redundancy r: each credential is given to round(r) distinct random actors (r>=1)."""
    parent, children = random_tree(n, rng)
    C = frozenset(range(m))
    sigma = {v: set() for v in range(n)}
    holders = max(1, int(round(redundancy)))
    for c in range(m):
        for v in rng.sample(range(n), min(holders, n)): sigma[v].add(c)
    sigma = {v: frozenset(s) for v, s in sigma.items()}
    ops = {}
    for v in range(1, n):
        if rng.random() < filter_density:
            k = rng.choice(filter_kinds)
        else:
            k = rng.choice(('cup', 'rj'))
        R = frozenset(c for c in range(m) if rng.random() < 0.5)
        ops[v] = (k, R)
    return parent, children, sigma, ops, C

def coalition_union(S, children, sigma, ops, root=0):
    """Shared-outcome coalition effective set on a tree (component roots contribute sigma)."""
    out = set()
    stack = [(root, None)]
    while stack:
        v, ctx = stack.pop()
        if v in S:
            e = sigma[v] if ctx is None else op_apply(ops[v], ctx, sigma[v])
            out |= e; nctx = e
        else:
            nctx = None
        for c in children[v]: stack.append((c, nctx))
    return out

def marginal(x, S, children, sigma, ops):
    return len(coalition_union(S | {x}, children, sigma, ops)) - len(coalition_union(S, children, sigma, ops))

def fpt_destructive(x, n, children, sigma, ops):
    """Exact: does there exist S with Delta_x(S) < 0? (pair-context DP, Prop 6.3)"""
    @lru_cache(maxsize=None)
    def A(u, cm, cp):
        res = set()
        if u == x:
            ep = sigma[u] if cp is None else op_apply(ops[u], cp, sigma[u])
            choices = [((frozenset(), ep), (None, ep))]
        else:
            em = sigma[u] if cm is None else op_apply(ops[u], cm, sigma[u])
            ep = sigma[u] if cp is None else op_apply(ops[u], cp, sigma[u])
            choices = [((frozenset(), frozenset()), (None, None)), ((em, ep), (em, ep))]
        for contrib, (ncm, ncp) in choices:
            acc = {contrib}
            for c in children[u]:
                sub = A(c, ncm, ncp)
                acc = {(a | b, a2 | b2) for (a, a2) in acc for (b, b2) in sub}
            res |= acc
        return frozenset(res)
    return any(len(p) < len(mn) for (mn, p) in A(0, None, None))
