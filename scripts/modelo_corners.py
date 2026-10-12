import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import poisson
from scipy.special import gammaln

df = pd.read_csv("datos/SP1_2026.csv", encoding="utf-8-sig")
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")

# Modelo Poisson para CORNERS
def fit_corners(data):
    equipos = sorted(set(data["HomeTeam"]) | set(data["AwayTeam"]))
    eq_idx = {e: i for i, e in enumerate(equipos)}
    n = len(equipos)
    h_idx = data["HomeTeam"].map(eq_idx).values
    a_idx = data["AwayTeam"].map(eq_idx).values
    h_c = data["HC"].values
    a_c = data["AC"].values
    lfx = gammaln(h_c + 1)
    lfy = gammaln(a_c + 1)
    
    def nll(params):
        atq = params[:n] - params[:n].mean()
        dfs = params[n:2*n]
        ha = params[2*n]
        lh = np.exp(atq[h_idx] + dfs[a_idx] + ha)
        la = np.exp(atq[a_idx] + dfs[h_idx])
        log_px = h_c * np.log(lh+1e-10) - lh - lfx
        log_py = a_c * np.log(la+1e-10) - la - lfy
        return -np.sum(log_px + log_py)
    
    x0 = np.concatenate([np.zeros(n), np.zeros(n), [0.2]])
    res = minimize(nll, x0, method="L-BFGS-B", options={"maxiter":100})
    return res.x, eq_idx

params_c, eq_idx_c = fit_corners(df)
n = len(eq_idx_c)
atq_c = params_c[:n] - params_c[:n].mean()
dfs_c = params_c[n:2*n]
ha_c = params_c[2*n]

print("=" * 70)
print("MODELO POISSON CORNERS - La Liga 2026/27")
print("=" * 70)
print(f"Equipos: {n}")
print(f"Ventaja local (corners): {ha_c:.3f}")

# Ranking de corners
ranking = pd.DataFrame({
    "equipo": list(eq_idx_c.keys()),
    "ataque_c": atq_c,
    "defensa_c": dfs_c,
    "poder_c": atq_c - dfs_c,
}).sort_values("poder_c", ascending=False)

print("\nTOP 10 - Equipos que MAS corners generan:")
print(ranking.head(10).to_string(index=False))

print("\nBOTTOM 5 - Equipos que MENOS corners generan:")
print(ranking.tail(5).to_string(index=False))

# Predicciones para un partido hipotetico
def predecir_corners(home, away):
    i = eq_idx_c[home]
    j = eq_idx_c[away]
    lh = np.exp(atq_c[i] + dfs_c[j] + ha_c)
    la = np.exp(atq_c[j] + dfs_c[i])
    total = lh + la
    print(f"\n{home} vs {away}:")
    print(f"  Corners esperados: {home} {lh:.2f} - {away} {la:.2f}")
    print(f"  Total esperado: {total:.2f}")
    for linea in [7.5, 8.5, 9.5, 10.5]:
        p_over = 1 - poisson.cdf(int(linea), total)
        print(f"  P(Over {linea}): {p_over*100:.1f}%")

print("\n" + "=" * 70)
print("PREDICCIONES EJEMPLO")
print("=" * 70)
predecir_corners("Barcelona", "Getafe")
predecir_corners("Espanol", "Ath Madrid")
predecir_corners("Sevilla", "Real Madrid")

# Guardar modelo
import pickle
with open("datos/modelo_corners.pkl", "wb") as f:
    pickle.dump({"params": params_c, "eq_idx": eq_idx_c}, f)

print("\nOK -> datos/modelo_corners.pkl")
