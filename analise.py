"""Marco 3 - MCEQ 12576. Analise: Q21 (Sim x Nao) vs contagem Q11 (0-8).
Uso: python analise.py dados/brutos/SurveyResponse.csv resultados
Dados: Peruma et al. (2024), Zenodo 10.5281/zenodo.13731929 (v8), CC BY 4.0."""
import sys
import json

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

csv = sys.argv[1]
out = sys.argv[2]
rng = np.random.default_rng(2026)
d = pd.read_csv(csv)
assert d.shape == (137, 32) and d["Response ID"].is_unique
C11 = [c for c in d.columns if c.startswith("What are the security features") and c.endswith("Selected Choice")][0]
C21 = [c for c in d.columns if c.startswith("Thinking back to when you were learning")][0]
C4 = "How many years of general programming experience do you have?"
C5 = "How many years of mobile app development experience do you have?"
assert d[[C11, C21, C4, C5]].notna().all().any() and d[[C11, C21, C4, C5]].notna().all(axis=1).all()

OPTS = ["Secure communications", "Two-factor authentication", "Data encryption",
        "Secure storage of information", "App hardening/obfuscation", "Permissions",
        "Authentication", "Biometric Authentication"]


def count(s):
    items = [x.strip() for x in s.split(",")]
    return sum(o in items for o in OPTS)
d["n_rec"] = d[C11].apply(count)
d["grp"] = d[C21].map({"Yes": "Sim", "No": "Não", "Maybe": "Talvez"})
assert d["n_rec"].between(0, 8).all()
R = {"n_total": len(d), "media_geral": round(d.n_rec.mean(), 4), "min": int(d.n_rec.min()), "max": int(d.n_rec.max())}
R["n_grupos"] = d.grp.value_counts().to_dict()

desc = d.groupby("grp").n_rec.agg(n="count", media="mean", dp="std", mediana="median", min="min", max="max")
desc["q1"] = d.groupby("grp").n_rec.quantile(.25)
desc["q3"] = d.groupby("grp").n_rec.quantile(.75)
print(desc.round(3))
R["desc"] = desc.round(4).to_dict("index")

a = d.loc[d.grp == "Sim", "n_rec"].to_numpy(float)
b = d.loc[d.grp == "Não", "n_rec"].to_numpy(float)
na, nb = len(a), len(b)
ma, mb = a.mean(), b.mean()
va, vb = a.var(ddof=1), b.var(ddof=1)
R["n_confirmatorio"] = na + nb
R["n_excluidos_talvez"] = int((d.grp == "Talvez").sum())

# Verificação dos pressupostos
R["shapiro_sim"] = stats.shapiro(a)._asdict() if hasattr(stats.shapiro(a), "_asdict") else list(stats.shapiro(a))
sh_a, sh_b = stats.shapiro(a), stats.shapiro(b)
lev = stats.levene(a, b, center="median")
R["shapiro"] = {"Sim": [float(sh_a.statistic), float(sh_a.pvalue)], "Não": [float(sh_b.statistic), float(sh_b.pvalue)]}
R["levene"] = [float(lev.statistic), float(lev.pvalue)]
del R["shapiro_sim"]

# Teste t de Welch unilateral (H1: média do grupo Sim > média do grupo Não)
w = stats.ttest_ind(a, b, equal_var=False, alternative="greater")
w2 = stats.ttest_ind(a, b, equal_var=False)  # teste bilateral, usado apenas para o IC
se = np.sqrt(va / na + vb / nb)
df = se**4 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
diff = ma - mb
tcrit = stats.t.ppf(.975, df)
ci = (diff - tcrit * se, diff + tcrit * se)
lb90 = diff - stats.t.ppf(.95, df) * se  # limite inferior do intervalo de confiança unilateral de 95%
sp = np.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
dcohen = diff / sp
J = 1 - 3 / (4 * (na + nb - 2) - 1)
g = dcohen * J
def dd(x, y):
    s = np.sqrt(
        ((len(x) - 1) * x.var(ddof=1) + (len(y) - 1) * y.var(ddof=1))
        / (len(x) + len(y) - 2)
    )
    return (x.mean() - y.mean()) / s


bs = np.array([dd(rng.choice(a, na), rng.choice(b, nb)) for _ in range(10000)])
bsd = np.percentile(bs, [2.5, 97.5])
# Intervalo de confiança aproximado de d (Hedges & Olkin)
se_d = np.sqrt((na + nb) / (na * nb) + dcohen**2 / (2 * (na + nb)))
R["welch"] = dict(
    t=float(w.statistic),
    df=float(df),
    p_unilateral=float(w.pvalue),
    p_bilateral=float(w2.pvalue),
    diff=float(diff),
    se=float(se),
    ic95_bilateral=[float(ci[0]), float(ci[1])],
    lim_inf_ic_unilateral95=float(lb90),
    d=float(dcohen),
    g=float(g),
    d_ic_boot=[float(bsd[0]), float(bsd[1])],
    d_ic_normal=[float(dcohen - 1.96 * se_d), float(dcohen + 1.96 * se_d)],
    media_sim=float(ma),
    media_nao=float(mb),
    dp_sim=float(np.sqrt(va)),
    dp_nao=float(np.sqrt(vb)),
    dp_pooled=float(sp),
)

# Teste alternativo: Mann-Whitney
mw = stats.mannwhitneyu(a, b, alternative="greater", method="asymptotic")
mw_b = stats.mannwhitneyu(a, b, alternative="two-sided", method="asymptotic")
U = float(mw.statistic)
cles = U / (na * nb)
rbc = 2 * cles - 1
R["mw"] = dict(
    U=U,
    p_unilateral=float(mw.pvalue),
    p_bilateral=float(mw_b.pvalue),
    prob_superioridade=float(cles),
    rank_biserial=float(rbc),
    mediana_sim=float(np.median(a)),
    mediana_nao=float(np.median(b)),
)
# Poder estatístico: efeito mínimo detectável (80%), com n=17 vs. 81 e alfa unilateral de 0,05 (aproximação normal)
za, zb = stats.norm.ppf(.95), stats.norm.ppf(.80)
R["d_minimo_detectavel_80pct"] = float((za + zb) * np.sqrt(1 / na + 1 / nb))

# Análise exploratória: Kruskal-Wallis para os 3 grupos e testes Mann-Whitney com correção de Holm
ga, gn, gt = a, b, d.loc[d.grp == "Talvez", "n_rec"].to_numpy(float)
kw = stats.kruskal(ga, gn, gt)
R["kw"] = [float(kw.statistic), float(kw.pvalue)]
pairs = {"Sim×Não": (ga, gn), "Sim×Talvez": (ga, gt), "Não×Talvez": (gn, gt)}
raw = {k: float(stats.mannwhitneyu(x, y, alternative="two-sided", method="asymptotic").pvalue) for k, (x, y) in pairs.items()}
order = sorted(raw, key=raw.get)
holm = {}
prev = 0
for i, k in enumerate(order):
    prev = max(prev, min(1, raw[k] * (3 - i)))
    holm[k] = prev
R["pares_exploratorios"] = {k: {"p_bruto": raw[k], "p_holm": holm[k]} for k in raw}
R["media_talvez"] = float(gt.mean())
R["dp_talvez"] = float(gt.std(ddof=1))

# Contexto das questões Q4 e Q5 por grupo (análise descritiva)
ctx = {}
for col, nm in [(C4, "Q4"), (C5, "Q5")]:
    ct = pd.crosstab(d.grp, d[col])
    ctx[nm] = ct.to_dict("index")
R["contexto"] = ctx
# Frequência de cada recurso de segurança
freq = {}
for g in ["Sim", "Não"]:
    s = d.loc[d.grp == g, C11]
    freq[g] = {o: int(s.apply(lambda x: o in [y.strip() for y in x.split(",")]).sum()) for o in OPTS}
R["freq_recursos"] = freq
json.dump(R, open(f"{out}/resultados.json", "w"), ensure_ascii=False, indent=1)

# Gráfico: boxplot, pontos com dispersão, média e IC de 95%; eixo Y de 0 a 8
fig, ax = plt.subplots(figsize=(3.3, 2.7), dpi=300)
cols = {"Não": "#7a8794", "Sim": "#1f5fa8"}
for i, (nm, v) in enumerate([("Não", b), ("Sim", a)]):
    jit = rng.uniform(-.14, .14, len(v))
    ax.scatter(np.full(len(v), i) + jit, v + rng.uniform(-.08, .08, len(v)), s=7, alpha=.45, color=cols[nm], lw=0, zorder=2)
    m = v.mean()
    h = stats.t.ppf(.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v))
    ax.errorbar(i + .27, m, yerr=h, fmt="D", color="#c0392b", ms=4, capsize=3, lw=1.1, zorder=3)
    ax.hlines(np.median(v), i - .2, i + .2, color="k", lw=1.6, zorder=4)
ax.set_xticks([0, 1])
ax.set_xticklabels([f"Não\n(n = {nb})", f"Sim\n(n = {na})"], fontsize=7)
ax.set_ylim(-0.3, 9.6)
ax.set_yticks(range(0, 9))
ax.tick_params(labelsize=7)
ax.set_ylabel("Recursos de segurança relatados (Q11, 0–8)", fontsize=6.5)
ax.set_xlabel("Materiais de aprendizagem suficientes? (Q21)", fontsize=6.5)
ax.plot([], [], "k-", lw=1.6, label="Mediana")
ax.errorbar([], [], yerr=[], fmt="D", color="#c0392b", ms=4, label="Média e IC 95%")
ax.legend(fontsize=6, loc="upper center", frameon=False, ncol=2)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
plt.tight_layout()
plt.savefig(f"{out}/figura_q21_q11.png")
plt.savefig(f"{out}/figura_q21_q11.pdf")
print(json.dumps(R["welch"], indent=1))
print(R["mw"])
print(R["shapiro"], R["levene"])
print(R["kw"], R["pares_exploratorios"], R["d_minimo_detectavel_80pct"])
print(R["contexto"])
print(R["freq_recursos"])
