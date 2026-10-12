import pandas as pd
import os

os.makedirs("data", exist_ok=True)

temporadas = ["2122", "2223", "2324", "2425", "2526"]
liga = "SP1"

dfs = []
for temp in temporadas:
    url = f"https://www.football-data.co.uk/mmz4281/{temp}/{liga}.csv"
    try:
        d = pd.read_csv(url, encoding="utf-8-sig")
        d["Season"] = temp
        dfs.append(d)
        print(f"OK {liga} {temp}: {len(d)} partidos")
    except Exception as e:
        print(f"ERROR {liga} {temp}: {e}")

if dfs:
    df_all = pd.concat(dfs, ignore_index=True)
    df_all.to_csv("SP1_historico.csv", index=False)
    print(f"\nTotal: {len(df_all)} partidos")
