import random, json, time, sys
from credalg import *
rng = random.Random(2026)
n, m = 30, 6
densities = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]
redundancies = [1, 2, 3]
TREES, COAL = 60, 40
res = {}
t0 = time.time()
for r in redundancies:
    for f in densities:
        pairs = 0; neg = 0; actors = 0; ever = 0
        for _ in range(TREES):
            parent, children, sigma, ops, C = random_instance(n, m, f, r, rng)
            for x in range(n):
                others = [v for v in range(n) if v != x]
                for _ in range(COAL):
                    S = frozenset(v for v in others if rng.random() < 0.5)
                    pairs += 1; neg += (marginal(x, S, children, sigma, ops) < 0)
            # exact "ever destructive" for a sample of actors
            for x in rng.sample(range(n), 8):
                actors += 1; ever += fpt_destructive(x, n, children, sigma, ops)
        res[f"r={r},f={f}"] = dict(r=r, f=f, pair_rate=neg/pairs, ever_rate=ever/actors)
        print(f"r={r} f={f:.1f}  P[Delta<0]={neg/pairs:.4f}  P[ever destructive]={ever/actors:.3f}  ({time.time()-t0:.0f}s)", flush=True)
json.dump(res, open('exp1.json','w'), indent=1)
