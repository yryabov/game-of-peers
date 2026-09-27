"""Unit tests: every number of the worked examples (Examples 1-4 of the supplement) recomputed
from the credential algebra.  Run:  python3 test_examples.py   (or: pytest test_examples.py)

Semantics: rooted tree, shared-outcome evaluation (coalition_union of credalg.py), zero
disclosure cost, W = cardinality unless stated.  Operators: ('cap',R) ('cup',R) ('lj',R) ('rj',R),
with lj(X,Y) = X | (Y & R) and rj(X,Y) = Y | (X & R).
"""
import os, sys, itertools
from fractions import Fraction
from math import factorial
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from credalg import op_apply, coalition_union

def effective_sets(S, children, sigma, ops, root):
    """Per-actor effective sets on a tree for coalition S (component roots contribute sigma)."""
    E = {}
    stack = [(root, None)]
    while stack:
        v, ctx = stack.pop()
        if v in S:
            E[v] = sigma[v] if ctx is None else frozenset(op_apply(ops[v], ctx, sigma[v]))
            nctx = E[v]
        else:
            nctx = None
        for c in children[v]:
            stack.append((c, nctx))
    return E

def value(S, children, sigma, ops, root):
    return len(coalition_union(frozenset(S), children, sigma, ops, root=root))

def shapley(actors, v):
    n = len(actors); phi = {}
    for a in actors:
        others = [b for b in actors if b != a]; tot = Fraction(0)
        for k in range(n):
            for S in itertools.combinations(others, k):
                w = Fraction(factorial(k) * factorial(n - k - 1), factorial(n))
                tot += w * (v(set(S) | {a}) - v(set(S)))
        phi[a] = tot
    return phi

def C(*xs): return frozenset(xs)

# ----------------------------------------------------------------------------------------
# Example 1: trade execution chain  h -> a1 -> a2, both edges intersection
# ----------------------------------------------------------------------------------------
def test_example1():
    sigma = {'h': C(1, 2, 6), 'a1': C(2, 3, 4, 6), 'a2': C(2, 5, 6)}
    children = {'h': ['a1'], 'a1': ['a2'], 'a2': []}
    ops = {'a1': ('cap', C()), 'a2': ('cap', C())}
    E = effective_sets({'h', 'a1', 'a2'}, children, sigma, ops, 'h')
    assert E['h'] == C(1, 2, 6) and E['a1'] == C(2, 6) and E['a2'] == C(2, 6)
    # complementarity valuation W_comp = |S| + 2 if {c1,c2,c6} subset of S
    W_comp = lambda X: len(X) + (2 if C(1, 2, 6) <= X else 0)
    assert [len(E[a]) for a in ('h', 'a1', 'a2')] == [3, 2, 2]
    assert [W_comp(E[a]) for a in ('h', 'a1', 'a2')] == [5, 2, 2]
    # sequential disclosure by backward induction: a non-root actor under intersection discloses
    # exactly ecred(parent) & sigma(self) whenever the per-credential value exceeds the cost
    alpha, beta = 1.0, 0.5
    def best(parent_eff, own):
        cands = [frozenset(d) for k in range(len(own) + 1) for d in itertools.combinations(sorted(own), k)]
        return max(cands, key=lambda d: (alpha * len(parent_eff & d) - beta * len(d), -len(d)))
    assert best(E['a1'], sigma['a2']) == C(2, 6)
    assert best(E['h'], sigma['a1']) == C(2, 6)

# ----------------------------------------------------------------------------------------
# Example 2: portfolio analysis coalition  h -> a1 (union), h -> a2 (intersection)
# ----------------------------------------------------------------------------------------
def ex2():
    sigma = {'h': C(1, 2, 3, 4, 6), 'a1': C(3, 6, 7), 'a2': C(2, 5, 8, 9)}
    children = {'h': ['a1', 'a2'], 'a1': [], 'a2': []}
    ops = {'a1': ('cup', C()), 'a2': ('cap', C())}
    return sigma, children, ops

def test_example2_propagation_and_coalitions():
    sigma, children, ops = ex2()
    E = effective_sets({'h', 'a1', 'a2'}, children, sigma, ops, 'h')
    assert E['a1'] == C(1, 2, 3, 4, 6, 7) and E['a2'] == C(2)
    v = lambda S: value(S, children, sigma, ops, 'h')
    table = {('h',): 5, ('a1',): 3, ('a2',): 4, ('h', 'a1'): 6, ('h', 'a2'): 5,
             ('a1', 'a2'): 7, ('h', 'a1', 'a2'): 6}
    for S, val in table.items():
        assert v(set(S)) == val, (S, v(set(S)), val)
    assert v({'a1', 'a2'}) == 7 > 6 == v({'h', 'a1', 'a2'})          # grand coalition not optimal
    assert v({'h', 'a1', 'a2'}) - v({'a1', 'a2'}) == -1                # Delta_h({a1,a2}) = -1
    assert v({'h', 'a2'}) - v({'h'}) == 0 and v({'h', 'a1', 'a2'}) - v({'h', 'a1'}) == 0
    assert v({'a1', 'a2'}) - v({'a2'}) == 3 and v({'h', 'a1'}) - v({'h'}) == 1
    # at-target evaluation at a2: Delta_h({a2}) = |{c2}| - |sigma(a2)| = -3
    Et = effective_sets({'h', 'a2'}, children, sigma, ops, 'h')['a2']
    assert len(Et) - len(sigma['a2']) == -3

def test_example2_shapley():
    sigma, children, ops = ex2()
    v = lambda S: value(S, children, sigma, ops, 'h')
    phi = shapley(['h', 'a1', 'a2'], v)
    assert all(phi[a] == Fraction(2) for a in phi), phi                 # all 2.00
    assert sum(phi.values()) == v({'h', 'a1', 'a2'})

def test_example2_strategic_distortion():
    # a1 withholds its unique c7: v({h,a1}) and v({h,a1,a2}) fall to 5
    sigma, children, ops = ex2()
    sigma = dict(sigma); sigma['a1'] = sigma['a1'] - {7}
    v = lambda S: value(S, children, sigma, ops, 'h')
    assert v({'h', 'a1'}) == 5 and v({'h', 'a1', 'a2'}) == 5

# ----------------------------------------------------------------------------------------
# Example 3: cross-organizational fraud investigation  a0 -> a1 (lj R1), a0 -> a2 (rj R2)
# ----------------------------------------------------------------------------------------
def test_example3():
    sigma = {'a0': C(1, 2, 4, 9), 'a1': C(3, 4, 5, 6, 9), 'a2': C(4, 7, 8, 9, 10)}
    children = {'a0': ['a1', 'a2'], 'a1': [], 'a2': []}
    R1, R2 = C(3, 5, 6), C(1, 4, 9)
    ops = {'a1': ('lj', R1), 'a2': ('rj', R2)}
    E = effective_sets({'a0', 'a1', 'a2'}, children, sigma, ops, 'a0')
    assert E['a1'] == C(1, 2, 3, 4, 5, 6, 9) and E['a2'] == C(1, 4, 7, 8, 9, 10)
    for R2v, size in [(C(9), 5), (C(1, 4, 9), 6), (C(1, 2, 4, 9), 7)]:
        ops2 = dict(ops); ops2['a2'] = ('rj', R2v)
        assert len(effective_sets({'a0', 'a1', 'a2'}, children, sigma, ops2, 'a0')['a2']) == size

# ----------------------------------------------------------------------------------------
# Example 4: cross-border regulatory stress test (six actors, all four operators)
# ----------------------------------------------------------------------------------------
def ex4():
    sigma = {'a0': C(1, 2, 3, 4, 9), 'h1': C(2, 3, 4, 5), 'h2': C(2, 4, 9, 11),
             'a1': C(3, 5, 6), 'a3': C(5, 7, 8), 'a2': C(10, 11, 12)}
    children = {'a0': ['h1', 'h2'], 'h1': ['a1', 'a3'], 'h2': ['a2'], 'a1': [], 'a2': [], 'a3': []}
    R1, R2, R3 = C(2, 4, 11), C(9), C(3, 5)
    ops = {'h1': ('cup', C()), 'h2': ('lj', R1), 'a1': ('cap', C()), 'a3': ('rj', R3), 'a2': ('rj', R2)}
    return sigma, children, ops

EX4_TABLE = {  # all 63 coalition values of Section S10
    'a0': 5, 'h1': 4, 'h2': 4, 'a1': 3, 'a3': 3, 'a2': 3,
    'a0 a3': 8, 'a0 a2': 8, 'a0 a1': 7, 'h1 a2': 7, 'a1 h2': 7, 'a3 h2': 7, 'a0 h1': 6, 'a0 h2': 6,
    'h1 a3': 6, 'h1 h2': 6, 'a1 a2': 6, 'a3 a2': 6, 'h2 a2': 6, 'a1 a3': 5, 'h1 a1': 4,
    'a0 a3 a2': 11, 'a0 a1 a2': 10, 'a0 h1 a2': 9, 'a0 a1 a3': 9, 'a0 a3 h2': 9, 'h1 a3 a2': 9,
    'a1 a3 h2': 9, 'a1 h2 a2': 9, 'a3 h2 a2': 9, 'a0 h1 a3': 8, 'a0 a1 h2': 8, 'a0 h2 a2': 8,
    'h1 a3 h2': 8, 'h1 h2 a2': 8, 'a1 a3 a2': 8, 'a0 h1 h2': 7, 'h1 a1 a2': 7, 'a0 h1 a1': 6,
    'h1 a1 a3': 6, 'h1 a1 h2': 6,
    'a0 a1 a3 a2': 12, 'a0 h1 a3 a2': 11, 'a0 a3 h2 a2': 11, 'a1 a3 h2 a2': 11, 'a0 a1 a3 h2': 10,
    'a0 a1 h2 a2': 10, 'h1 a3 h2 a2': 10, 'a0 h1 a1 a2': 9, 'a0 h1 a3 h2': 9, 'a0 h1 h2 a2': 9,
    'h1 a1 a3 a2': 9, 'a0 h1 a1 a3': 8, 'h1 a1 a3 h2': 8, 'h1 a1 h2 a2': 8, 'a0 h1 a1 h2': 7,
    'a0 a1 a3 h2 a2': 12, 'a0 h1 a1 a3 a2': 11, 'a0 h1 a1 a3 h2': 9, 'a0 h1 a1 h2 a2': 9,
    'a0 h1 a3 h2 a2': 11, 'h1 a1 a3 h2 a2': 10,
    'a0 h1 a1 a3 h2 a2': 11,
}

def test_example4_all_63_coalitions():
    sigma, children, ops = ex4()
    assert len(EX4_TABLE) == 63
    for key, val in EX4_TABLE.items():
        S = set(key.split())
        assert value(S, children, sigma, ops, 'a0') == val, (key, value(S, children, sigma, ops, 'a0'), val)

def test_example4_headline_numbers():
    sigma, children, ops = ex4()
    v = lambda S: value(S, children, sigma, ops, 'a0')
    N = set(sigma)
    assert v(N) == 11 and v(N - {'h1'}) == 12                          # grand coalition not optimal
    assert v({'a0', 'a1', 'a2', 'a3'}) == 12                            # the all-agent coalition
    assert v(N) - v(N - {'h1'}) == -1 and v({'h1', 'a1'}) - v({'a1'}) == 1   # Corollary ex4 (i), (ii)
    # h1 has negative marginal contribution in 12 of the 16 coalitions that contain its filtered child a1
    others = ['a0', 'a3', 'h2', 'a2']
    neg = sum(1 for k in range(5) for S in itertools.combinations(others, k)
              if v(set(S) | {'a1', 'h1'}) - v(set(S) | {'a1'}) < 0)
    assert neg == 12
    # at-target evaluation at a1 for S = N \ {h1}: -1 under intersection, +4 under a left join with c6 in R
    E_S = effective_sets(N - {'h1'}, children, sigma, ops, 'a0')['a1']
    E_T = effective_sets(N, children, sigma, ops, 'a0')['a1']
    assert E_T == C(3, 5) and len(E_T) - len(E_S) == -1
    ops2 = dict(ops); ops2['a1'] = ('lj', C(6))
    E_T2 = effective_sets(N, children, sigma, ops2, 'a0')['a1']
    assert len(E_T2) - len(E_S) == 4

def test_example4_shapley():
    sigma, children, ops = ex4()
    v = lambda S: value(S, children, sigma, ops, 'a0')
    phi = shapley(['a0', 'h1', 'a1', 'a3', 'h2', 'a2'], v)
    expected = {'a0': Fraction(5, 2), 'h1': Fraction(5, 6), 'a1': Fraction(7, 6),
                'a3': Fraction(7, 3), 'h2': Fraction(5, 3), 'a2': Fraction(5, 2)}
    assert phi == expected, phi
    assert sum(phi.values()) == 11

if __name__ == '__main__':
    tests = [f for n, f in sorted(globals().items()) if n.startswith('test_')]
    for t in tests:
        t(); print('ok ', t.__name__)
    print(f'{len(tests)} tests passed')
