"""Exact Destructive-Actor via the pair-context DP (Prop 6.3) vs brute force over coalitions."""
import random, time, json, itertools
from credalg import *
rng = random.Random(5)
def brute(x, n, children, sigma, ops):
    others = [v for v in range(n) if v != x]
    for r in range(len(others)+1):
        for S in itertools.combinations(others, r):
            if marginal(x, frozenset(S), children, sigma, ops) < 0: return True
    return False
res = []
# correctness cross-check on small n, then timing of the DP alone
for n, m in [(12,3),(14,4)]:
    for _ in range(30):
        parent, children, sigma, ops, C = random_instance(n, m, 0.5, 2, rng); x = rng.randrange(n)
        assert brute(x,n,children,sigma,ops) == fpt_destructive(x,n,children,sigma,ops)
print("DP == brute force on 60 small instances")
for m in [3, 4, 5, 6]:
    for n in [50, 100, 200, 400]:
        parent, children, sigma, ops, C = random_instance(n, m, 0.5, 2, rng); x = rng.randrange(n)
        t0 = time.perf_counter(); d = fpt_destructive(x, n, children, sigma, ops); dt = time.perf_counter() - t0
        res.append(dict(n=n, m=m, seconds=dt, destructive=d))
        print(f"|C|={m} n={n:>4}  exact DA: {dt:7.3f} s  (2^n coalitions would be 2^{n-1})", flush=True)
json.dump(res, open('exp3.json','w'), indent=1)
