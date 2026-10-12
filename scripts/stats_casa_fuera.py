import pandas as pd
import numpy as np

hist = pd.read_csv("datos/SP1_historico.csv", encoding="utf-8-sig")
new = pd.read_csv("datos/SP1_2026.csv", encoding="utf-8-sig")

cols = ["Date","HomeTeam","AwayTeam","FTHG","FTAG","FTR","HTHG","HTAG","HS","AS","HST","AST","HC","AC","HY","AY","HF","AF"]
hist = hist[[c for c in cols if c in hist.columns]].copy()
new = new[[c for c in cols if c in new.columns]].copy()

df = pd.concat([hist, new], ignore_index=True)
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")

# Solo 2026/27
df_2026 = df[df["Date"] >= "2026-08-01"].copy()
print(f"Partidos 2026/27: {len(df_2026)}")

# --- LOCAL ---
local = df_2026.groupby("HomeTeam").agg(
    pj=("FTHG", "count"),
    gf=("FTHG", "mean"),
    gc=("FTAG", "mean"),
    remates=("HS", "mean"),
    sot=("HST", "mean"),
    corners=("HC", "mean"),
    amarillas=("HY", "mean"),
    faltas=("HF", "mean"),
).reset_index()
local.columns = ["equipo", "pj_local", "gf_local", "gc_local", "remates_local", "sot_local", "corners_local", "amarillas_local", "faltas_local"]

# --- VISITANTE ---
visit = df_2026.groupby("AwayTeam").agg(
    pj=("FTAG", "count"),
    gf=("FTAG", "mean"),
    gc=("FTHG", "mean"),
    remates=("AS", "mean"),
    sot=("AST", "mean"),
    corners=("AC", "mean"),
    amarillas=("AY", "mean"),
    faltas=("AF", "mean"),
).reset_index()
visit.columns = ["equipo", "pj_visit", "gf_visit", "gc_visit", "remates_visit", "sot_visit", "corners_visit", "amarillas_visit", "faltas_visit"]

stats = local.merge(visit, on="equipo", how="outer").fillna(0)

stats["dif_gf"] = stats["gf_local"] - stats["gf_visit"]
stats["dif_gc"] = stats["gc_local"] - stats["gc_visit"]
stats["dif_amarillas"] = stats["amarillas_local"] - stats["amarillas_visit"]

stats = stats.sort_values("dif_gf", ascending=False)

print("=" * 130)
print("STATS CASA/FUERA - LA LIGA 2026/27")
print("=" * 130)
print(f"\n{'Equipo':<15} {'PJ C':>5} {'PJ F':>5} {'GF C':>6} {'GF F':>6} {'Dif':>7} {'GC C':>6} {'GC F':>6} {'Dif':>7} {'Amar C':>7} {'Amar F':>7}")
print("-" * 130)
for _, r in stats.iterrows():
    print(f"{r['equipo']:<15} {r['pj_local']:>5.0f} {r['pj_visit']:>5.0f} {r['gf_local']:>6.2f} {r['gf_visit']:>6.2f} {r['dif_gf']:>+7.2f} {r['gc_local']:>6.2f} {r['gc_visit']:>6.2f} {r['dif_gc']:>+7.2f} {r['amarillas_local']:>7.2f} {r['amarillas_visit']:>7.2f}")

stats.to_csv("datos/stats_casa_fuera.csv", index=False)
print("\nOK -> datos/stats_casa_fuera.csv")
