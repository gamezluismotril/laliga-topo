import pandas as pd

# Cargar histórico
hist = pd.read_csv("datos/SP1_historico.csv", encoding="utf-8-sig")
hist["Date"] = pd.to_datetime(hist["Date"], format="%d/%m/%Y", errors="coerce")
hist = hist[["Date","HomeTeam","AwayTeam","FTHG","FTAG","FTR","B365H","B365D","B365A","B365CH","B365CD","B365CA"]].copy()
hist["temporada"] = "historico"

# Cargar 2026/27
new = pd.read_csv("datos/SP1_2026.csv", encoding="utf-8-sig")
new["Date"] = pd.to_datetime(new["Date"], format="%d/%m/%Y", errors="coerce")
new = new[["Date","HomeTeam","AwayTeam","FTHG","FTAG","FTR","B365H","B365D","B365A","B365CH","B365CD","B365CA"]].copy()
new["temporada"] = "2026_27"

# Unir
df = pd.concat([hist, new], ignore_index=True)
df = df.dropna(subset=["Date","FTHG","FTAG"]).sort_values("Date").reset_index(drop=True)

print(f"Total partidos: {len(df)}")
print(f"  Historico: {(df['temporada']=='historico').sum()}")
print(f"  2026/27:   {(df['temporada']=='2026_27').sum()}")
print(f"Rango: {df['Date'].min()} -> {df['Date'].max()}")

df.to_csv("datos/SP1_unificado.csv", index=False)
print("\nOK -> datos/SP1_unificado.csv")

# Ver equipos unicos
equipos_2026 = set(new["HomeTeam"]) | set(new["AwayTeam"])
equipos_hist = set(hist["HomeTeam"]) | set(hist["AwayTeam"])
print(f"\nEquipos 2026/27: {len(equipos_2026)}")
print(f"Equipos historico: {len(equipos_hist)}")
print(f"Equipos en ambos: {len(equipos_2026 & equipos_hist)}")
print(f"Nuevos en 2026/27: {sorted(equipos_2026 - equipos_hist)}")
