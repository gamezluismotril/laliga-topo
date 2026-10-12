import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import poisson
from scipy.special import gammaln

df = pd.read_csv("datos/SP1_2026.csv", encoding="utf-8-sig")
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")

def fit_amarillas(data):
    equipos = sorted(set(data["HomeTeam"]) | set(data["AwayTeam"]))
    eq_idx = {e: i for i, e in enumerate(equipos)}
    n = len(equipos)
    h_idx = data["HomeTeam"].map(eq_idx).values
    a_idx = data["AwayTeam"].map(eq_idx).values
    h_c = data["HY"].values
    a_c = data["AY"].values
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
    
    x0 = np.concatenate([np.zeros(n), np.zeros(n), [0.0]])
    res = minimize(nll, x0, method="L-BFGS-B", options={"maxiter":100})
    return res.x, eq_idx

params_a, eq_idx_a = fit_amarillas(df)
n = len(eq_idx_a)
atq_a = params_a[:n] - params_a[:n].mean()
dfs_a = params_a[n:2*n]
ha_a = params_a[2*n]

print("=" * 70)
print("MODELO POISSON AMARILLAS - La Liga 2026/27")
print("=" * 70)
print(f"Ventaja local (amarillas): {ha_a:.3f}")

# Ranking
ranking = pd.DataFrame({
    "equipo": list(eq_idx_a.keys()),
    "ataque_a": atq_a,
    "defensa_a": dfs_a,
    "poder_a": atq_a - dfs_a,
}).sort_values("poder_a", ascending=False)

print("\nTOP 10 - Equipos MAS indisciplinados:")
print(ranking.head(10).to_string(index=False))

print("\nBOTTOM 5 - Equipos MENOS indisciplinados:")
print(ranking.tail(5).to_string(index=False))

# Predicciones
def predecir_amarillas(home, away):
    i = eq_idx_a[home]
    j = eq_idx_a[away]
    lh = np.exp(atq_a[i] + dfs_a[j] + ha_a)
    la = np.exp(atq_a[j] + dfs_a[i])
    total = lh + la
    print(f"\n{home} vs {away}:")
    print(f"  Amarillas esperadas: {home} {lh:.2f} - {away} {la:.2f}")
    print(f"  Total esperado: {total:.2f}")
    for linea in [3.5, 4.5, 5.5]:
        p_over = 1 - poisson.cdf(int(linea), total)
        print(f"  P(Over {linea}): {p_over*100:.1f}%")

print("\n" + "=" * 70)
print("PREDICCIONES EJEMPLO")
print("=" * 70)
predecir_amarillas("Espanol", "Getafe")
predecir_amarillas("Ath Madrid", "Sevilla")
predecir_amarillas("Barcelona", "Real Madrid")

# Guardar
import pickle
with open("datos/modelo_amarillas.pkl", "wb") as f:
    pickle.dump({"params": params_a, "eq_idx": eq_idx_a}, f)

print("\nOK -> datos/modelo_amarillas.pkl")
