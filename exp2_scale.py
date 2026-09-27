"""Audit cost at scale: time of one marginal contribution Delta_x(S) on random trees."""
import random, time, json
from credalg import *
rng = random.Random(11)
res = []
for n in [1000, 3000, 10000, 30000, 100000]:
    for m in [20, 50, 100]:
        parent, children, sigma, ops, C = random_instance(n, m, 0.5, 2, rng)
        x = rng.randrange(n); S = frozenset(v for v in range(n) if v != x and rng.random() < 0.5)
        reps = 5 if n <= 10000 else 2
        t0 = time.perf_counter()
        for _ in range(reps): marginal(x, S, children, sigma, ops)
        dt = (time.perf_counter() - t0) / reps
        res.append(dict(n=n, m=m, seconds=dt))
        print(f"n={n:>6} |C|={m:>3}  Delta_x(S): {dt*1000:8.1f} ms", flush=True)
json.dump(res, open('exp2.json','w'), indent=1)
