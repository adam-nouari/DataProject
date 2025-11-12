import sqlite3
import pandas as pd
from pathlib import Path

def main():
    cleaned_dir = Path("data/cleaned")
    db_dir = Path("data/database")
    db_dir.mkdir(parents=True, exist_ok=True)

    db_path = db_dir / "vitesses.db"

    files = {
        "vitesse_2021_cleaned.csv": 2021,
        "vitesse_2023_cleaned.csv": 2023
    }

    all_data = []

    for file_name, annee in files.items():
        csv_path = cleaned_dir / file_name
        if csv_path.exists():
            print(f"[INFO] Lecture de {file_name}")
            # 1) Empêcher la conversion auto en datetime
            df = pd.read_csv(csv_path, sep=";", dtype={"date": "string"})
            df["annee"] = annee
            # 2) Normaliser la date (en string) et supprimer les 'T' s'il en reste
            df["date"] = (
                pd.to_datetime(df["date"], errors="coerce")
                  .dt.strftime("%Y-%m-%d %H:%M:%S")
            )
            # Si certaines valeurs ne sont pas parsables, retomber sur la chaîne brute sans T
            mask_na = df["date"].isna()
            if mask_na.any():
                df.loc[mask_na, "date"] = (
                    df.loc[mask_na, "date"].astype("string")
                )
            df["date"] = df["date"].str.replace("T", " ", regex=False)
            all_data.append(df)
        else:
            print(f"[WARN] Fichier manquant : {csv_path}")

    if not all_data:
        print("[ERREUR] Aucun fichier trouvé à charger.")
        return

    merged = pd.concat(all_data, ignore_index=True)
    print(f"[INFO] Total lignes combinées : {len(merged)}")

    # 3) S’assurer que la colonne reste du texte au moment du dump SQL
    merged["date"] = merged["date"].astype(str)

    conn = sqlite3.connect(db_path)
    merged.to_sql("vitesses", conn, if_exists="replace", index=False)
    conn.close()
    print(f"[OK] Base '{db_path.name}' créée avec la table 'vitesses' ({len(merged)} lignes)")
    
if __name__ == "__main__":
    main()
