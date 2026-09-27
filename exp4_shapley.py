"""Shapley sampling (Prop 6.4) vs exact value from the pair-context DP with multiplicities."""
import random, time, json, math
from functools import lru_cache
from fractions import Fraction
from credalg import *
rng = random.Random(17)

def exact_shapley(x, n, children, sigma, ops):
    """Exact phi_x: DP over (context pair) -> {(Ym,Yp,k): count} where k=|S| (members excluding x)."""
    @lru_cache(maxsize=None)
    def A(u, cm, cp):
        res = {}
        if u == x:
            ep = sigma[u] if cp is None else op_apply(ops[u], cp, sigma[u])
            choices = [((frozenset(), ep, 0), (None, ep))]
        else:
            em = sigma[u] if cm is None else op_apply(ops[u], cm, sigma[u])
            ep = sigma[u] if cp is None else op_apply(ops[u], cp, sigma[u])
            choices = [((frozenset(), frozenset(), 0), (None, None)), ((em, ep, 1), (em, ep))]
        for (a, a2, k), (ncm, ncp) in choices:
            acc = {(a, a2, k): 1}
            for c in children[u]:
                sub = A(c, ncm, ncp); nacc = {}
                for (b, b2, kb), cnt in acc.items():
                    for (d, d2, kd), cnt2 in sub.items():
                        key = (b | d, b2 | d2, kb + kd); nacc[key] = nacc.get(key, 0) + cnt * cnt2
                acc = nacc
            for key, cnt in acc.items(): res[key] = res.get(key, 0) + cnt
        return res
    tot = Fraction(0)
    for (ym, yp, k), cnt in A(0, None, None).items():
        w = Fraction(math.factorial(k) * math.factorial(n - k - 1), math.factorial(n))
        tot += w * cnt * (len(yp) - len(ym))
    return float(tot)

def sampled_shapley(x, n, children, sigma, ops, samples):
    acc = 0.0; others = [v for v in range(n) if v != x]
    for _ in range(samples):
        rng.shuffle(others); k = rng.randrange(n)  # position of x in a random permutation
        S = frozenset(others[:k]); acc += marginal(x, S, children, sigma, ops)
    return acc / samples

res = []
n, m = 30, 8
for inst in range(20):
    parent, children, sigma, ops, C = random_instance(n, m, 0.5, 2, rng)
    x = rng.choice([v for v in range(n) if sigma[v]])  # a credential holder
    t0 = time.perf_counter(); ex = exact_shapley(x, n, children, sigma, ops); te = time.perf_counter() - t0
    row = dict(instance=inst, exact=ex, exact_seconds=te, errors={})
    for samples in [100, 1000, 10000]:
        errs = [abs(sampled_shapley(x, n, children, sigma, ops, samples) - ex) for _ in range(10)]
        row['errors'][samples] = dict(mean=sum(errs)/10, max=max(errs))
    res.append(row)
    print(f"inst {inst}: exact phi={ex:+.4f} ({te:.2f}s); mean|err| @100={row['errors'][100]['mean']:.3f} @1000={row['errors'][1000]['mean']:.3f} @10000={row['errors'][10000]['mean']:.3f}", flush=True)
json.dump(res, open('exp4.json','w'), indent=1)
