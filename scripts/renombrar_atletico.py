import pandas as pd
import os

# Actualizar stats_casa_fuera.csv
if os.path.exists("datos/stats_casa_fuera.csv"):
    df = pd.read_csv("datos/stats_casa_fuera.csv")
    df["equipo"] = df["equipo"].replace("Ath Madrid", "At Madrid")
    df.to_csv("datos/stats_casa_fuera.csv", index=False)
    print("OK -> stats_casa_fuera.csv")

# Actualizar proximos_partidos.csv
if os.path.exists("datos/proximos_partidos.csv"):
    df = pd.read_csv("datos/proximos_partidos.csv")
    df["HomeTeam"] = df["HomeTeam"].replace("Ath Madrid", "At Madrid")
    df["AwayTeam"] = df["AwayTeam"].replace("Ath Madrid", "At Madrid")
    df.to_csv("datos/proximos_partidos.csv", index=False)
    print("OK -> proximos_partidos.csv")

# Actualizar SP1_historico.csv
if os.path.exists("datos/SP1_historico.csv"):
    df = pd.read_csv("datos/SP1_historico.csv", encoding="utf-8-sig")
    df["HomeTeam"] = df["HomeTeam"].replace("Ath Madrid", "At Madrid")
    df["AwayTeam"] = df["AwayTeam"].replace("Ath Madrid", "At Madrid")
    df.to_csv("datos/SP1_historico.csv", index=False, encoding="utf-8-sig")
    print("OK -> SP1_historico.csv")

# Actualizar SP1_2026.csv
if os.path.exists("datos/SP1_2026.csv"):
    df = pd.read_csv("datos/SP1_2026.csv", encoding="utf-8-sig")
    df["HomeTeam"] = df["HomeTeam"].replace("Ath Madrid", "At Madrid")
    df["AwayTeam"] = df["AwayTeam"].replace("Ath Madrid", "At Madrid")
    df.to_csv("datos/SP1_2026.csv", index=False, encoding="utf-8-sig")
    print("OK -> SP1_2026.csv")

# Actualizar SP1_features_full.csv
if os.path.exists("datos/SP1_features_full.csv"):
    df = pd.read_csv("datos/SP1_features_full.csv", encoding="utf-8-sig")
    df["HomeTeam"] = df["HomeTeam"].replace("Ath Madrid", "At Madrid")
    df["AwayTeam"] = df["AwayTeam"].replace("Ath Madrid", "At Madrid")
    df.to_csv("datos/SP1_features_full.csv", index=False, encoding="utf-8-sig")
    print("OK -> SP1_features_full.csv")

print("\nTodos los CSV actualizados")
