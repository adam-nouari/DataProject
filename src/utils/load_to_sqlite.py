"""
Module de chargement des données nettoyées vers SQLite.
Calcule également les périodes jour/nuit basées sur les éphémérides.
"""
from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
from astral import LocationInfo
from astral.sun import sun
import pytz


REPERTOIRE_NETTOYE = Path("data/cleaned")
CHEMIN_DB = Path("data/database/vitesses.db")
FUSEAU_HORAIRE = pytz.timezone("Europe/Paris")
PRECISION_GRILLE = 1  # Arrondi à 0.1° pour optimisation
TAILLE_BLOC = 400_000


def verifier_colonne_existe(conn: sqlite3.Connection, table: str, colonne: str) -> bool:
    """Vérifie si une colonne existe dans une table."""
    info = pd.read_sql_query(f"PRAGMA table_info({table});", conn)
    return colonne in info["name"].tolist()


def localiser_paris(series_naive: pd.Series) -> pd.Series:
    """
    Convertit une série datetime naive en datetime avec fuseau Europe/Paris.
    
    Args:
        series_naive: Série pandas de timestamps naifs
        
    Returns:
        Série avec fuseau horaire appliqué
    """
    dt = pd.to_datetime(series_naive, errors="coerce")
    try:
        return dt.dt.tz_localize(FUSEAU_HORAIRE, ambiguous="infer", 
                                  nonexistent="shift_forward")
    except Exception:
        return dt.dt.tz_localize(FUSEAU_HORAIRE, ambiguous=False, 
                                  nonexistent="shift_forward")


def calculer_ephemerides(dates_positions: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les heures de lever et coucher du soleil pour chaque position.
    
    Args:
        dates_positions: DataFrame avec colonnes date_only, lat_round, lon_round
        
    Returns:
        DataFrame enrichi avec sunrise_local et sunset_local
    """
    resultats = []
    
    for date, lat, lon in dates_positions.itertuples(index=False, name=None):
        try:
            lieu = LocationInfo(latitude=lat, longitude=lon, 
                              timezone=FUSEAU_HORAIRE.zone)
            ephemerides = sun(lieu.observer, date=date, tzinfo=FUSEAU_HORAIRE)
            resultats.append((date, lat, lon, 
                            ephemerides["sunrise"], 
                            ephemerides["sunset"]))
        except Exception:
            resultats.append((date, lat, lon, pd.NaT, pd.NaT))
    
    return pd.DataFrame(
        resultats, 
        columns=["date_only", "lat_round", "lon_round", 
                "sunrise_local", "sunset_local"]
    )


def calculer_periode_bloc(bloc: pd.DataFrame) -> pd.DataFrame:
    """
    Détermine la période (jour/nuit) pour un bloc de données.
    
    Args:
        bloc: DataFrame avec colonnes rid, date, position
        
    Returns:
        DataFrame avec rid et periode
    """
    bloc = bloc.copy()
    bloc["datetime"] = pd.to_datetime(bloc["date"], errors="coerce")
    bloc = bloc.dropna(subset=["datetime", "position"]).copy()
    bloc["datetime"] = localiser_paris(bloc["datetime"])
    bloc["date_only"] = bloc["datetime"].dt.date
    
    # Extraction lat/lon
    coords = bloc["position"].str.split(expand=True)
    coords.columns = ["lat", "lon"]
    bloc = pd.concat([bloc, coords], axis=1)
    bloc["lat"] = pd.to_numeric(bloc["lat"], errors="coerce")
    bloc["lon"] = pd.to_numeric(bloc["lon"], errors="coerce")
    bloc = bloc.dropna(subset=["lat", "lon"]).copy()
    
    # Arrondi pour optimisation
    bloc["lat_round"] = bloc["lat"].round(PRECISION_GRILLE)
    bloc["lon_round"] = bloc["lon"].round(PRECISION_GRILLE)
    
    # Calcul des éphémérides pour les clés uniques
    cles_uniques = bloc[["date_only", "lat_round", "lon_round"]].drop_duplicates()
    ephemerides = calculer_ephemerides(cles_uniques)
    
    # Jointure et détermination période
    bloc_enrichi = bloc.merge(
        ephemerides, 
        on=["date_only", "lat_round", "lon_round"], 
        how="left"
    )
    
    bloc_enrichi["periode"] = np.where(
        (bloc_enrichi["datetime"] >= bloc_enrichi["sunrise_local"]) & 
        (bloc_enrichi["datetime"] <= bloc_enrichi["sunset_local"]),
        "jour", 
        "nuit"
    )
    
    return bloc_enrichi[["rid", "periode"]]


def main():
    """Charge les données CSV dans SQLite et calcule les périodes."""
    fichiers = {"vitesse_2023_cleaned.csv": 2023}
    
    CHEMIN_DB.parent.mkdir(parents=True, exist_ok=True)
    
    # Import CSV vers SQLite
    donnees_completes = []
    for nom_fichier, annee in fichiers.items():
        chemin_csv = REPERTOIRE_NETTOYE / nom_fichier
        if not chemin_csv.exists():
            raise FileNotFoundError(f"CSV introuvable: {chemin_csv}")
        
        df = pd.read_csv(chemin_csv, sep=";", dtype={"date": "string"})
        df["annee"] = annee
        df["date"] = (pd.to_datetime(df["date"], errors="coerce")
                        .dt.strftime("%Y-%m-%d %H:%M:%S"))
        donnees_completes.append(df)
    
    df_final = pd.concat(donnees_completes, ignore_index=True)
    df_final["date"] = df_final["date"].astype(str)
    
    with sqlite3.connect(CHEMIN_DB) as conn:
        df_final.to_sql("vitesses", conn, if_exists="replace", index=False)
        print(f"Table créée: {len(df_final):,} lignes")
        
        # Ajout colonne periode si nécessaire
        if not verifier_colonne_existe(conn, "vitesses", "periode"):
            conn.execute("ALTER TABLE vitesses ADD COLUMN periode TEXT;")
            conn.commit()
        
        # Calcul des périodes par blocs
        requete = "SELECT rowid AS rid, date, position FROM vitesses;"
        total_mis_a_jour = 0
        
        for i, bloc in enumerate(pd.read_sql_query(requete, conn, 
                                                   chunksize=TAILLE_BLOC)):
            resultats = calculer_periode_bloc(bloc)
            
            conn.executemany(
                "UPDATE vitesses SET periode=? WHERE rowid=?;",
                [(p, rid) for rid, p in resultats.itertuples(index=False, name=None)]
            )
            conn.commit()
            total_mis_a_jour += len(resultats)
        
        print(f"Périodes calculées: {total_mis_a_jour:,} lignes")
        
        # Création d'index pour performances
        conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON vitesses(date);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_position ON vitesses(position);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_periode ON vitesses(periode);")
        conn.commit()


if __name__ == "__main__":
    main()