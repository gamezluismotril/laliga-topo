import pandas as pd

urls = [
    "https://www.football-data.co.uk/mmz4281/2627/SP1.csv",
    "https://www.football-data.co.uk/mmz4281/2627/SP2.csv",
]

for url in urls:
    try:
        df = pd.read_csv(url, encoding="utf-8-sig")
        nombre = url.split("/")[-1].replace(".csv", "")
        df.to_csv(f"datos/{nombre}_2026.csv", index=False)
        print(f"OK {nombre}: {len(df)} partidos")
        print(df.head())
    except Exception as e:
        print(f"ERROR {url}: {e}")
