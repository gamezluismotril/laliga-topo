import pandas as pd
import numpy as np

df = pd.read_csv("SP1_historico.csv", encoding="utf-8-sig")
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
df = df.sort_values("Date").reset_index(drop=True)

print("Partidos:", len(df))

# --- 1. Consenso de cuotas de APERTURA ---
casas_H = ["B365H", "BFDH", "BVH", "BWH"]
casas_D = ["B365D", "BFDD", "BVD", "BWD"]
casas_A = ["B365A", "BFDA", "BVA", "BWA"]

casas_H = [c for c in casas_H if c in df.columns]
casas_D = [c for c in casas_D if c in df.columns]
casas_A = [c for c in casas_A if c in df.columns]

# Probabilidades implicitas por casa
for col in casas_H:
    df[f"imp_{col}"] = 1 / df[col]
for col in casas_D:
    df[f"imp_{col}"] = 1 / df[col]
for col in casas_A:
    df[f"imp_{col}"] = 1 / df[col]

# Consenso (media de probabilidades implicitas)
df["cons_H"] = df[[f"imp_{c}" for c in casas_H]].mean(axis=1)
df["cons_D"] = df[[f"imp_{c}" for c in casas_D]].mean(axis=1)
df["cons_A"] = df[[f"imp_{c}" for c in casas_A]].mean(axis=1)

# Normalizar (quitar overround)
overround = df["cons_H"] + df["cons_D"] + df["cons_A"]
df["cons_H_norm"] = df["cons_H"] / overround
df["cons_D_norm"] = df["cons_D"] / overround
df["cons_A_norm"] = df["cons_A"] / overround

# --- 2. Consenso de cuotas de CIERRE ---
casas_CH = ["B365CH", "MaxCH", "AvgCH"]
casas_CD = ["B365CD", "MaxCD", "AvgCD"]
casas_CA = ["B365CA", "MaxCA", "AvgCA"]
casas_CH = [c for c in casas_CH if c in df.columns]
casas_CD = [c for c in casas_CD if c in df.columns]
casas_CA = [c for c in casas_CA if c in df.columns]

for col in casas_CH: df[f"impc_{col}"] = 1 / df[col]
for col in casas_CD: df[f"impc_{col}"] = 1 / df[col]
for col in casas_CA: df[f"impc_{col}"] = 1 / df[col]

df["consC_H"] = df[[f"impc_{c}" for c in casas_CH]].mean(axis=1)
df["consC_D"] = df[[f"impc_{c}" for c in casas_CD]].mean(axis=1)
df["consC_A"] = df[[f"impc_{c}" for c in casas_CA]].mean(axis=1)
overround_c = df["consC_H"] + df["consC_D"] + df["consC_A"]
df["consC_H_norm"] = df["consC_H"] / overround_c
df["consC_D_norm"] = df["consC_D"] / overround_c
df["consC_A_norm"] = df["consC_A"] / overround_c

# --- 3. Betfair Exchange (la casa sharp) ---
if "BFEH" in df.columns:
    df["bfe_imp_H"] = 1 / df["BFEH"]
    df["bfe_imp_D"] = 1 / df["BFED"]
    df["bfe_imp_A"] = 1 / df["BFEA"]
    bfe_ovr = df["bfe_imp_H"] + df["bfe_imp_D"] + df["bfe_imp_A"]
    df["bfe_H_norm"] = df["bfe_imp_H"] / bfe_ovr
    df["bfe_D_norm"] = df["bfe_imp_D"] / bfe_ovr
    df["bfe_A_norm"] = df["bfe_imp_A"] / bfe_ovr

# --- 4. Movimiento de cuotas medio entre casas ---
df["mov_cons_H"] = df["consC_H_norm"] - df["cons_H_norm"]
df["mov_cons_D"] = df["consC_D_norm"] - df["cons_D_norm"]
df["mov_cons_A"] = df["consC_A_norm"] - df["cons_A_norm"]

# --- 5. Divergencia entre casas (apertura) ---
casas_H_std = df[[f"imp_{c}" for c in casas_H]].std(axis=1)
casas_D_std = df[[f"imp_{c}" for c in casas_D]].std(axis=1)
casas_A_std = df[[f"imp_{c}" for c in casas_A]].std(axis=1)
df["div_H"] = casas_H_std
df["div_D"] = casas_D_std
df["div_A"] = casas_A_std

# --- 6. Guardar ---
cols_salvar = [
    "Season", "Date", "HomeTeam", "AwayTeam",
    "FTHG", "FTAG", "FTR", "resultado" if "resultado" in df.columns else "FTR",
    "cons_H_norm", "cons_D_norm", "cons_A_norm",
    "consC_H_norm", "consC_D_norm", "consC_A_norm",
    "bfe_H_norm", "bfe_D_norm", "bfe_A_norm",
    "mov_cons_H", "mov_cons_D", "mov_cons_A",
    "div_H", "div_D", "div_A",
    "B365H", "B365D", "B365A",
    "B365CH", "B365CD", "B365CA",
    "MaxH", "MaxD", "MaxA",
    "MaxCH", "MaxCD", "MaxCA",
    "AvgH", "AvgD", "AvgA",
    "AvgCH", "AvgCD", "AvgCA",
]
cols_salvar = [c for c in cols_salvar if c in df.columns]

df[cols_salvar].to_csv("SP1_consenso.csv", index=False)

print("\nOK -> SP1_consenso.csv")
print("\nColumnas consenso apertura:")
print(df[["cons_H_norm","cons_D_norm","cons_A_norm"]].describe().round(3))
print("\nColumnas consenso cierre:")
print(df[["consC_H_norm","consC_D_norm","consC_A_norm"]].describe().round(3))
if "bfe_H_norm" in df.columns:
    print("\nBetfair Exchange:")
    print(df[["bfe_H_norm","bfe_D_norm","bfe_A_norm"]].describe().round(3))

# --- Validacion ---
# Comparar precision de B365 solo vs consenso
from sklearn.metrics import log_loss

if "resultado" not in df.columns:
    df["resultado"] = df["FTR"].map({"H":0,"D":1,"A":2})

y = df["resultado"].dropna()
idx = y.index

# B365 cierre
p_b365 = df.loc[idx, ["B365CH","B365CD","B365CA"]].copy()
p_b365 = p_b365.div(p_b365.sum(axis=1), axis=0).values
ll_b365 = log_loss(y, p_b365, labels=[0,1,2])

# Consenso cierre
p_cons = df.loc[idx, ["consC_H_norm","consC_D_norm","consC_A_norm"]].values
ll_cons = log_loss(y, p_cons, labels=[0,1,2])

print("\n" + "=" * 50)
print("COMPARATIVA LOG-LOSS")
print("=" * 50)
print(f"B365 solo       -> Log-loss: {ll_b365:.4f}")
print(f"Consenso 15 casas -> Log-loss: {ll_cons:.4f}")
