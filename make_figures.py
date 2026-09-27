"""Figures for the supplemental 'Computational evaluation' section. Reads exp*.json, writes PDF."""
import json, statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
C1, C2, C3 = '#1f5fa8', '#d9762b', '#52514e'   # validated pair + neutral
plt.rcParams.update({'font.size': 9, 'font.family': 'serif', 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#e6e6e3', 'grid.linewidth': 0.6, 'axes.edgecolor': '#999', 'lines.linewidth': 1.6})

# ---- Fig S1: prevalence vs filter density (exp1) and vs redundancy (exp1b) ----
e1 = json.load(open('exp1.json')); e1b = json.load(open('exp1b.json'))
fig, ax = plt.subplots(1, 2, figsize=(6.8, 2.6))
for r, col, mk in [(1, C1, 'o'), (2, C2, 's'), (3, C3, '^')]:
    rows = sorted([v for v in e1.values() if v['r'] == r], key=lambda v: v['f'])
    ax[0].plot([v['f'] for v in rows], [100*v['ever_rate'] for v in rows], marker=mk, ms=4, color=col, label=f'{r} holder{"s" if r>1 else ""} per credential')
ax[0].set_xlabel('filter density $f$ (fraction of filtering edges)'); ax[0].set_ylabel('actors ever destructive (%)')
ax[0].legend(frameon=False, fontsize=7.5, loc='upper left'); ax[0].set_title('(a) Prevalence vs. filter density', fontsize=9, loc='left')
for kind, col, mk, lab in [('random', C2, 's', 'copies placed at random'), ('protected', C1, 'o', 'copies outside filtered positions')]:
    rows = sorted([v for v in e1b.values() if v['kind'] == kind], key=lambda v: v['r'])
    ax[1].plot([v['r'] for v in rows], [100*v['pair_rate'] for v in rows], marker=mk, ms=4, color=col, label=lab)
ax[1].set_xlabel('holders per credential $r$ (filter density 0.6)'); ax[1].set_ylabel('pairs $(x,S)$ with $\\Delta_x(S)<0$ (%)')
ax[1].set_xticks([1, 2, 3, 4]); ax[1].legend(frameon=False, fontsize=7.5); ax[1].set_title('(b) Redundancy: where the copy sits', fontsize=9, loc='left')
fig.tight_layout(); fig.savefig('figS1_prevalence.pdf'); plt.close(fig)

# ---- Fig S2: audit time (exp2) and exact detection time vs |C| (exp3b) ----
e2 = json.load(open('exp2.json')); e3b = json.load(open('exp3b.json'))
fig, ax = plt.subplots(1, 2, figsize=(6.8, 2.6))
for m, col, mk in [(20, C1, 'o'), (50, C2, 's'), (100, C3, '^')]:
    rows = sorted([v for v in e2 if v['m'] == m], key=lambda v: v['n'])
    ax[0].plot([v['n'] for v in rows], [1000*v['seconds'] for v in rows], marker=mk, ms=4, color=col, label=f'$|\\mathcal{{C}}|={m}$')
ax[0].set_xscale('log'); ax[0].set_yscale('log'); ax[0].set_xlabel('actors $n$'); ax[0].set_ylabel('one marginal $\\Delta_x(S)$ (ms)')
ax[0].legend(frameon=False, fontsize=7.5); ax[0].set_title('(a) Audit cost (Prop. 6.1)', fontsize=9, loc='left')
ax[1].plot([v['m'] for v in e3b], [v['seconds'] for v in e3b], marker='o', ms=4, color=C1)
ax[1].set_yscale('log'); ax[1].set_xlabel('credentials $|\\mathcal{C}|$ ($n=200$)'); ax[1].set_ylabel('exact detection (s)')
ax[1].set_title('(b) Exact detection (Prop. 6.3)', fontsize=9, loc='left')
fig.tight_layout(); fig.savefig('figS2_scale.pdf'); plt.close(fig)
print('figures written')

# ---- numbers for the text ----
e4 = json.load(open('exp4.json'))
print('exp1 r=1: f=0.1', e1['r=1,f=0.1']['ever_rate'], 'f=0.5', e1['r=1,f=0.5']['ever_rate'], 'f=1.0', e1['r=1,f=1.0']['ever_rate'])
print('exp1b pair_rate protected r=1..4:', [round(e1b[f'protected,r={r}']['pair_rate'],4) for r in [1,2,3,4]])
print('exp1b pair_rate random r=1..4:', [round(e1b[f'random,r={r}']['pair_rate'],4) for r in [1,2,3,4]])
print('exp1b ever random r=1..4:', [round(e1b[f'random,r={r}']['ever_rate'],3) for r in [1,2,3,4]], 'protected:', [round(e1b[f'protected,r={r}']['ever_rate'],3) for r in [1,2,3,4]])
print('exp2 n=1000/m=50:', round(1000*[v for v in e2 if v['n']==1000 and v['m']==50][0]['seconds'],2),'ms; n=100000/m=50:', round(1000*[v for v in e2 if v['n']==100000 and v['m']==50][0]['seconds'],1),'ms')
print('exp3b:', [(v['m'], round(v['seconds'],3)) for v in e3b])
for s in ['100','1000','10000']:
    print('exp4 samples',s,'mean|err|',round(statistics.mean(x['errors'][s]['mean'] for x in e4),4),'max',round(max(x['errors'][s]['max'] for x in e4),4))
print('exp4 mean|phi|', round(statistics.mean(abs(x['exact']) for x in e4),3), 'exact time', round(statistics.mean(x['exact_seconds'] for x in e4),3))
