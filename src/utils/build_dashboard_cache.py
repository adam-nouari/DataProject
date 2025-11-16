"""
Génération du fichier agrégé pour le dashboard.
Calcule les statistiques par période, limitation et classe de dépassement.
"""
from pathlib import Path
import sqlite3
import pandas as pd


CHEMIN_DB = Path("data/database/vitesses.db")
CHEMIN_SORTIE = Path("data/cleaned/vitesses_agg_2023.csv")

CLASSES_DEPASSEMENT = [
    "≤ 0 km/h (respect)",
    "0–10 km/h",
    "10–20 km/h",
    "20–30 km/h",
    "> 30 km/h",
]


def main():
    """Génère le fichier d'agrégation pour le dashboard."""
    conn = sqlite3.connect(CHEMIN_DB)
    
    requete = """
        SELECT date, position, vitesse_mesuree, limitation, periode, annee
        FROM vitesses
        WHERE annee = 2023
    """
    
    df = pd.read_sql_query(requete, conn)
    conn.close()
    
    # Calcul du dépassement
    df["date"] = pd.to_datetime(df["date"])
    df["depassement"] = df["vitesse_mesuree"] - df["limitation"]
    
    # Classification par tranches
    bornes = [-float("inf"), 0, 10, 20, 30, float("inf")]
    df["classe_depassement"] = pd.cut(
        df["depassement"],
        bins=bornes,
        labels=CLASSES_DEPASSEMENT,
        include_lowest=True,
        right=True,
    )
    
    # Agrégation
    agregation = (
        df.groupby(["periode", "limitation", "classe_depassement"], observed=False)
          .size()
          .reset_index(name="count")
    )
    
    # Sauvegarde
    CHEMIN_SORTIE.parent.mkdir(parents=True, exist_ok=True)
    agregation.to_csv(CHEMIN_SORTIE, index=False)
    print(f"Agrégation: {len(agregation)} lignes")


if __name__ == "__main__":
    main()