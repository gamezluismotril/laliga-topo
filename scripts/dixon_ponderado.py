import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import poisson
from scipy.special import gammaln

df = pd.read_csv("datos/SP1_unificado.csv", encoding="utf-8-sig")
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date").reset_index(drop=True)

# Calcular peso por antiguedad
fecha_max = df["Date"].max()
df["dias_atras"] = (fecha_max - df["Date"]).dt.days

# Factor de decaimiento: 0.005 -> partidos de hace 1000 dias pesan exp(-5)=0.007
# 0.01 -> partidos de hace 100 dias pesan exp(-1)=0.37
XI = 0.008  # ajustable
df["peso"] = np.exp(-XI * df["dias_atras"])

print(f"Factor XI: {XI}")
print(f"Partido mas reciente: peso = {df['peso'].max():.3f}")
print(f"Partido mas antiguo: peso = {df['peso'].min():.5f}")
print(f"\nPeso medio por temporada:")
print(df.groupby("temporada")["peso"].mean())

# Dixon-Coles ponderado
def dixon_fit_weighted(data, xi=0.008):
    fecha_max = data["Date"].max()
    pesos = np.exp(-xi * (fecha_max - data["Date"]).dt.days).values
    
    equipos = sorted(set(data["HomeTeam"]) | set(data["AwayTeam"]))
    eq_idx = {e: i for i, e in enumerate(equipos)}
    n = len(equipos)
    h_idx = data["HomeTeam"].map(eq_idx).values
    a_idx = data["AwayTeam"].map(eq_idx).values
    x_g = data["FTHG"].values; y_g = data["FTAG"].values
    lfx = gammaln(x_g + 1); lfy = gammaln(y_g + 1)
    
    def nll(params):
        atq = params[:n] - params[:n].mean()
        dfs = params[n:2*n]
        ha = params[2*n]; rho = params[2*n+1]
        lh = np.exp(atq[h_idx] + dfs[a_idx] + ha)
        la = np.exp(atq[a_idx] + dfs[h_idx])
        log_px = x_g * np.log(lh+1e-10) - lh - lfx
        log_py = y_g * np.log(la+1e-10) - la - lfy
        tau = np.ones(len(x_g))
        m00=(x_g==0)&(y_g==0); m01=(x_g==0)&(y_g==1)
        m10=(x_g==1)&(y_g==0); m11=(x_g==1)&(y_g==1)
        tau[m00] = 1 - lh[m00]*la[m00]*rho
        tau[m01] = 1 + lh[m01]*rho
        tau[m10] = 1 + la[m10]*rho
        tau[m11] = 1 - rho
        tau = np.clip(tau, 1e-10, None)
        return -np.sum(pesos * (np.log(tau) + log_px + log_py))
    
    x0 = np.concatenate([np.zeros(n), np.zeros(n), [0.3], [-0.1]])
    res = minimize(nll, x0, method="L-BFGS-B", options={"maxiter":100})
    return res.x, eq_idx

print("\nEntrenando Dixon-Coles ponderado...")
params, eq_idx = dixon_fit_weighted(df, xi=XI)

n = len(eq_idx)
ataque = params[:n] - params[:n].mean()
defensa = params[n:2*n]
home_adv = params[2*n]
rho = params[2*n + 1]

print(f"\nConvergencia: OK")
print(f"Ventaja local: {home_adv:.3f}")
print(f"Rho: {rho:.3f}")

# Ranking
ranking = pd.DataFrame({
    "equipo": list(eq_idx.keys()),
    "ataque": ataque,
    "defensa": defensa,
    "poder": ataque - defensa,
}).sort_values("poder", ascending=False)

print("\n" + "=" * 60)
print("RANKING PONDERADO (mas peso a 2026/27)")
print("=" * 60)
print(ranking.to_string(index=False))

ranking.to_csv("datos/ranking_ponderado.csv", index=False)

# Guardar modelo
import pickle
with open("datos/modelo_ponderado.pkl", "wb") as f:
    pickle.dump({"params": params, "eq_idx": eq_idx}, f)

print("\nOK -> datos/modelo_ponderado.pkl")
print("OK -> datos/ranking_ponderado.csv")
