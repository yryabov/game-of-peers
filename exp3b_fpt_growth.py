"""FPT growth in |C| at fixed n: shows where the 2^{O(|C|)} factor bites."""
import random, time, json
from credalg import *
rng = random.Random(13)
res = []
n = 200
for m in [4, 6, 8, 10, 12]:
    ts = []
    for _ in range(3):
        parent, children, sigma, ops, C = random_instance(n, m, 0.5, 2, rng); x = rng.randrange(n)
        t0 = time.perf_counter(); fpt_destructive(x, n, children, sigma, ops); ts.append(time.perf_counter() - t0)
    res.append(dict(n=n, m=m, seconds=sum(ts)/len(ts)))
    print(f"n={n} |C|={m:>2}  exact DA: {sum(ts)/len(ts):8.3f} s", flush=True)
json.dump(res, open('exp3b.json','w'), indent=1)
