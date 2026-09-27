"""Prop agg-indep on CYCLIC graphs with a monotone interpolating Phi = intersection over parents.
Claim: with every non-origin-headed edge preserving, lfp satisfies E(a) ⊇ σ(a) and Ê_S = ∪σ."""
import random, itertools
random.seed(3)
def op_apply(op,X,Y):
    k,R=op
    return {'cap':X&Y,'cup':X|Y,'lj':X|(Y&R),'rj':Y|(X&R)}[k]
def lfp_phi(S,edges,ops,sigma,O,C,phi):
    src={a for a in S if not any((p,a) in edges for p in S)}
    OS=(O&S)|src
    E={a:frozenset() for a in S}
    while True:
        E2={}
        for a in S:
            base=sigma[a] if a in OS else frozenset()
            terms=[op_apply(ops[(p,a)],E[p],sigma[a]) for p in S if (p,a) in edges]
            agg = phi(terms) if terms else frozenset()
            E2[a]=frozenset(base|agg)
        if E2==E: return E
        E=E2
inter=lambda ts: frozenset.intersection(*ts)
union=lambda ts: frozenset.union(*ts)
C=frozenset({0,1,2}); bad=0; tested=0; cyclic=0
for _ in range(3000):
    n=random.choice([2,3,4]); A=list(range(n))
    edges={(i,j) for i in A for j in A if i!=j and random.random()<0.6}
    if not edges: continue
    # preserving operators only (cup / rj)
    ops={e:(random.choice(['cup','rj']),frozenset(c for c in C if random.random()<0.5)) for e in edges}
    O=frozenset(a for a in A if random.random()<0.4)
    sigma={a:frozenset(c for c in C if random.random()<0.5) for a in A}
    # detect a cycle
    def has_cycle():
        for k in range(2,n+1):
            for perm in itertools.permutations(A,k):
                if all((perm[i],perm[(i+1)%k]) in edges for i in range(k)): return True
        return False
    hc=has_cycle(); cyclic+=hc
    S=frozenset(A)
    for phi in (inter,union):
        E=lfp_phi(S,edges,ops,sigma,O,C,phi); tested+=1
        ok = all(E[a]>=sigma[a] for a in S) and frozenset.union(*E.values())==frozenset.union(*sigma.values())
        if not ok: bad+=1; print('COUNTEREXAMPLE',edges,ops,sigma,O,phi.__name__)
print('tested',tested,'(cyclic graphs:',cyclic,') violations',bad)
