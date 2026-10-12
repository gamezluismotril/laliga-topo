import pandas as pd
import numpy as np
from scipy.stats import poisson
import pickle
from itertools import combinations

with open("datos/modelo_ponderado.pkl", "rb") as f:
    m_goles = pickle.load(f)

stats_cf = pd.read_csv("datos/stats_casa_fuera.csv").set_index("equipo")
arbitros = pd.read_csv("datos/arbitros.csv")
media_liga_amarillas = arbitros["Media_amarillas"].mean()
partidos_jornada = pd.read_csv("datos/proximos_partidos.csv")

CUOTAS_REALES = {
    "1": 1.20, "X": 4.50, "2": 7.50,
    "1X": 1.05, "12": 1.12, "X2": 3.20,
    "O2.5": 1.50, "BTTS": 1.70,
    "C85": 1.35, "A35": 1.20, "A45": 1.45,
}

def factor_arbitro(nombre):
    if not nombre or nombre not in arbitros["Nombre"].values:
        return 1.0
    return arbitros[arbitros["Nombre"] == nombre]["Media_amarillas"].values[0] / media_liga_amarillas

p = m_goles["params"]
n = len(m_goles["eq_idx"])
atq_g = p[:n] - p[:n].mean()
dfs_g = p[n:2*n]
ha_g = p[2*n]
eq_g = m_goles["eq_idx"]

def predecir(home, away, arbitro=None):
    i, j = eq_g[home], eq_g[away]
    lh = np.exp(atq_g[i] + dfs_g[j] + ha_g)
    la = np.exp(atq_g[j] + dfs_g[i])
    m = np.zeros((10, 10))
    for x in range(10):
        for y in range(10):
            m[x, y] = poisson.pmf(x, lh) * poisson.pmf(y, la)
    ph = np.tril(m, -1).sum()
    pd_ = np.trace(m)
    pa = np.triu(m, 1).sum()
    goles = np.add.outer(np.arange(10), np.arange(10))
    over25 = (m * (goles > 2.5)).sum()
    btts = m[1:, 1:].sum()
    doble_1X = ph + pd_
    doble_12 = ph + pa
    doble_X2 = pd_ + pa
    corners = stats_cf.loc[home, "corners_local"] + stats_cf.loc[away, "corners_visit"] if home in stats_cf.index and away in stats_cf.index else 0
    amarillas = stats_cf.loc[home, "amarillas_local"] + stats_cf.loc[away, "amarillas_visit"] if home in stats_cf.index and away in stats_cf.index else 0
    factor = factor_arbitro(arbitro) if arbitro else 1.0
    amarillas *= factor
    return {
        "1": ph, "X": pd_, "2": pa, "1X": doble_1X, "12": doble_12, "X2": doble_X2,
        "O2.5": over25, "BTTS": btts,
        "C85": 1 - poisson.cdf(8, corners),
        "A35": 1 - poisson.cdf(3, amarillas),
        "A45": 1 - poisson.cdf(4, amarillas),
        "corners_esp": corners, "amarillas_esp": amarillas,
    }

def value(prob, cuota):
    return (prob * cuota) - 1

print("=" * 90)
for i, row in partidos_jornada.iterrows():
    print(f"[{i+1}] {row['HomeTeam']} vs {row['AwayTeam']}")
print()
for i, row in arbitros.iterrows():
    print(f"[{i+1:>2}] {row['Nombre']:<40} {row['Media_amarillas']:.2f}")
print()

asignaciones = []
for i, row in partidos_jornada.iterrows():
    num = input(f"Arbitro [{i+1}]: ").strip()
    arb = arbitros.iloc[int(num)-1]["Nombre"] if num and num.isdigit() and 1 <= int(num) <= len(arbitros) else None
    asignaciones.append(arb)

# BLOQUE 1
print("\n" + "=" * 190)
print("BLOQUE 1: PROBABILIDADES")
print("=" * 190)
print(f"\n{'Partido':<26} {'1':>5} {'X':>5} {'2':>5} {'1X':>5} {'12':>5} {'X2':>5} {'O2.5':>6} {'BTTS':>6} {'Corn':>6} {'Amar':>6} {'O3.5A':>6} {'O4.5A':>6}")
print("-" * 190)
for idx, row in partidos_jornada.iterrows():
    r = predecir(row["HomeTeam"], row["AwayTeam"], asignaciones[idx])
    partido = f"{row['HomeTeam']} vs {row['AwayTeam']}"
    print(f"{partido:<26} {r['1']*100:>5.1f} {r['X']*100:>5.1f} {r['2']*100:>5.1f} {r['1X']*100:>5.1f} {r['12']*100:>5.1f} {r['X2']*100:>5.1f} {r['O2.5']*100:>6.1f} {r['BTTS']*100:>6.1f} {r['corners_esp']:>6.1f} {r['amarillas_esp']:>6.1f} {r['A35']*100:>6.1f} {r['A45']*100:>6.1f}")

# BLOQUE 2
print("\n" + "=" * 190)
print("BLOQUE 2: VALUE INDIVIDUAL")
print("=" * 190)
print(f"\n{'Partido':<26} {'1':>7} {'X':>7} {'2':>7} {'1X':>7} {'12':>7} {'X2':>7} {'O2.5':>7} {'BTTS':>7} {'C85':>7} {'A35':>7} {'A45':>7}")
print("-" * 190)

candidatos = []
for idx, row in partidos_jornada.iterrows():
    r = predecir(row["HomeTeam"], row["AwayTeam"], asignaciones[idx])
    partido = f"{row['HomeTeam']} vs {row['AwayTeam']}"
    valores = {}
    for m in ["1", "X", "2", "1X", "12", "X2", "O2.5", "BTTS", "C85", "A35", "A45"]:
        prob = r[m]
        cuota = CUOTAS_REALES[m]
        v = value(prob, cuota)
        valores[m] = v
        # FILTRO: solo mercados con prob razonable y value positivo
        if v > 0.05 and 0.50 < prob < 0.90:
            candidatos.append({"partido": partido, "mercado": m, "prob": prob, "cuota": cuota, "value": v})
    print(f"{partido:<26} {valores['1']*100:>+7.1f} {valores['X']*100:>+7.1f} {valores['2']*100:>+7.1f} {valores['1X']*100:>+7.1f} {valores['12']*100:>+7.1f} {valores['X2']*100:>+7.1f} {valores['O2.5']*100:>+7.1f} {valores['BTTS']*100:>+7.1f} {valores['C85']*100:>+7.1f} {valores['A35']*100:>+7.1f} {valores['A45']*100:>+7.1f}")

# BLOQUE 3 - CORREGIDO
print("\n" + "=" * 190)
print("BLOQUE 3: TOP 5 COMBINADAS CON VALUE (calculo CORRECTO)")
print("=" * 190)

if len(candidatos) < 2:
    print("\nNo hay suficientes mercados con value.")
else:
    combinadas = []
    for n_sel in [2, 3]:
        for combo in combinations(candidatos, n_sel):
            partidos_unicos = set(c["partido"] for c in combo)
            if len(partidos_unicos) < n_sel:
                continue
            prob_c = 1
            for c in combo:
                prob_c *= c["prob"]
            if prob_c < 0.15:
                continue
            cuota_justa = 1 / prob_c
            # CORRECCION: cuota real = cuota justa * (1 - margen combinada)
            # Margen: 5% para 2 sel, 8% para 3 sel
            margen = 0.05 + (0.015 * (n_sel - 2))
            cuota_real_c = cuota_justa * (1 - margen)
            v = (prob_c * cuota_real_c) - 1
            combinadas.append({"sel": combo, "prob": prob_c, "cuota_justa": cuota_justa, "cuota_real": cuota_real_c, "value": v, "margen": margen})
    
    combinadas.sort(key=lambda x: -x["value"])
    for i, c in enumerate(combinadas[:5], 1):
        print(f"\n--- COMBINADA {i} ---")
        print(f"Prob: {c['prob']*100:.1f}% | Cuota justa: {c['cuota_justa']:.2f} | Cuota real: {c['cuota_real']:.2f} | Margen: {c['margen']*100:.1f}% | VALUE: {c['value']*100:+.1f}%")
        for s in c["sel"]:
            print(f"  - {s['partido']:<28} {s['mercado']:<6} ({s['prob']*100:.1f}% @ {s['cuota']:.2f})")
    
    positivas = [c for c in combinadas if c["value"] > 0]
    print(f"\nTotal combinadas: {len(combinadas)} | Con value positivo: {len(positivas)}")
    if positivas:
        print("\n*** TOP 3 CON VALUE POSITIVO ***")
        for c in positivas[:3]:
            print(f"  Prob {c['prob']*100:.1f}% | Cuota real {c['cuota_real']:.2f} | Value {c['value']*100:+.1f}%")
    else:
        print("\n*** NO HAY COMBINADAS CON VALUE POSITIVO ***")
        print("El mercado es eficiente. Esto es lo NORMAL.")
