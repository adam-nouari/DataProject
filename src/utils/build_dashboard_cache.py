from pathlib import Path
import sqlite3
import pandas as pd

DB_PATH = Path("data/database/vitesses.db")
OUT_PATH = Path("data/cleaned/vitesses_agg_2023.csv")  # ← CSV au lieu de parquet


def main():
    print("[INFO] Connexion à la base…")
    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            date,
            position,
            vitesse_mesuree,
            limitation,
            periode,
            annee
        FROM vitesses
        WHERE annee = 2023
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    print("[INFO] DF brut :", df.shape)

    df["date"] = pd.to_datetime(df["date"])
    df["depassement"] = df["vitesse_mesuree"] - df["limitation"]

    classes_order = [
        "≤ 0 km/h (respect)",
        "0–10 km/h",
        "10–20 km/h",
        "20–30 km/h",
        "> 30 km/h",
    ]
    bins = [-float("inf"), 0, 10, 20, 30, float("inf")]

    df["classe_depassement"] = pd.cut(
        df["depassement"],
        bins=bins,
        labels=classes_order,
        include_lowest=True,
        right=True,
    )

    agg = (
        df.groupby(["periode", "limitation", "classe_depassement"], observed=False)
          .size()
          .reset_index(name="count")
    )
    print("[INFO] AGG :", agg.shape)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    agg.to_csv(OUT_PATH, index=False)          # ← CSV ici
    print(f"[OK] Fichier agrégé sauvegardé dans {OUT_PATH}")


if __name__ == "__main__":
    main()
