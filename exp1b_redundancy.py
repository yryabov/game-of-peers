"""Redundancy vs destructiveness: random copies vs copies placed outside filtered children."""
import random, json, time
from credalg import *
rng = random.Random(7)
n, m, f = 30, 6, 0.6
TREES, COAL = 80, 40

def instance_with_redundancy(kind, r):
    parent, children, sigma, ops, C = random_instance(n, m, f, 1, rng)
    filtered_kids = {v for v in range(1, n) if pi_of(ops[v], C) != C}
    sigma = {v: set(s) for v, s in sigma.items()}
    for c in range(m):
        holders = [v for v in range(n) if c in sigma[v]]
        need = r - len(holders)
        if kind == 'random':
            pool = [v for v in range(n) if c not in sigma[v]]
        else:  # 'protected': copies only at actors that are not filtered children
            pool = [v for v in range(n) if c not in sigma[v] and v not in filtered_kids]
        for v in rng.sample(pool, min(need, len(pool))): sigma[v].add(c)
    sigma = {v: frozenset(s) for v, s in sigma.items()}
    return parent, children, sigma, ops, C

res = {}
t0 = time.time()
for kind in ['random', 'protected']:
    for r in [1, 2, 3, 4]:
        pairs = neg = actors = ever = 0
        for _ in range(TREES):
            parent, children, sigma, ops, C = instance_with_redundancy(kind, r)
            for x in range(n):
                others = [v for v in range(n) if v != x]
                for _ in range(COAL):
                    S = frozenset(v for v in others if rng.random() < 0.5)
                    pairs += 1; neg += (marginal(x, S, children, sigma, ops) < 0)
            for x in rng.sample(range(n), 8):
                actors += 1; ever += fpt_destructive(x, n, children, sigma, ops)
        res[f"{kind},r={r}"] = dict(kind=kind, r=r, pair_rate=neg/pairs, ever_rate=ever/actors)
        print(f"{kind:9s} r={r}  P[Delta<0]={neg/pairs:.4f}  P[ever]={ever/actors:.3f}  ({time.time()-t0:.0f}s)", flush=True)
json.dump(res, open('exp1b.json','w'), indent=1)
