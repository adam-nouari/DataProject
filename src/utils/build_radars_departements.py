"""
Calcul des statistiques d'infractions par département.
Utilise une jointure spatiale entre les positions GPS et les départements.
"""
from pathlib import Path
import sqlite3
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


CHEMIN_DB = Path("data/database/vitesses.db")
CHEMIN_GEOJSON = Path("data/geo/departements.geojson")
CHEMIN_SORTIE = Path("data/cleaned/infractions_par_dept_agg.csv")
LIMITE_ECHANTILLON = 200_000


def detecter_colonne_code(gdf: gpd.GeoDataFrame) -> str:
    """
    Détecte automatiquement la colonne contenant le code département.
    
    Args:
        gdf: GeoDataFrame des départements
        
    Returns:
        Nom de la colonne contenant les codes
    """
    candidats = ["code", "code_dept", "CODE_DEPT", "nom", "INSEE_DEP"]
    
    for candidat in candidats:
        if candidat in gdf.columns:
            return candidat
    
    raise ValueError(f"Colonne code non trouvée. Colonnes: {list(gdf.columns)}")


def extraire_infractions(conn: sqlite3.Connection, limite: int = None) -> pd.DataFrame:
    """
    Extrait les infractions de la base de données.
    
    Args:
        conn: Connexion SQLite
        limite: Nombre maximum de lignes (None = tout)
        
    Returns:
        DataFrame avec position et dépassement
    """
    requete = """
        SELECT position, (vitesse_mesuree - limitation) as depassement
        FROM vitesses
        WHERE annee = 2023 AND (vitesse_mesuree - limitation) > 0
    """
    
    if limite:
        requete += f" LIMIT {limite}"
    
    return pd.read_sql_query(requete, conn)


def convertir_en_geodataframe(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """
    Convertit un DataFrame avec colonne 'position' en GeoDataFrame.
    
    Args:
        df: DataFrame avec colonne position (format "lat lon")
        
    Returns:
        GeoDataFrame avec géométries Point
    """
    coords = df["position"].str.split(expand=True, n=1)
    coords.columns = ["lat", "lon"]
    coords = coords.apply(pd.to_numeric, errors="coerce")
    
    df = pd.concat([df, coords], axis=1)
    df = df.dropna(subset=["lat", "lon"])
    
    geometries = [Point(lon, lat) for lon, lat in zip(df["lon"], df["lat"])]
    
    return gpd.GeoDataFrame(df, geometry=geometries, crs="EPSG:4326")


def calculer_statistiques(df_joint: pd.DataFrame, col_code: str) -> pd.DataFrame:
    """
    Calcule les statistiques d'infractions par département.
    
    Args:
        df_joint: DataFrame après jointure spatiale
        col_code: Nom de la colonne contenant le code département
        
    Returns:
        DataFrame agrégé par département
    """
    agg = (
        df_joint.groupby(col_code)
        .agg({"depassement": ["count", "mean", "median", "max"]})
        .reset_index()
    )
    
    agg.columns = [
        "code_dept", 
        "nb_infractions", 
        "depassement_moyen",
        "depassement_median",
        "depassement_max"
    ]
    
    agg["depassement_moyen"] = agg["depassement_moyen"].round(2)
    agg["depassement_median"] = agg["depassement_median"].round(2)
    
    return agg.sort_values("nb_infractions", ascending=False)


def main():
    """Génère le fichier d'agrégation par département."""
    # Chargement GeoJSON
    if not CHEMIN_GEOJSON.exists():
        raise FileNotFoundError(f"GeoJSON manquant: {CHEMIN_GEOJSON}")
    
    gdf_dept = gpd.read_file(CHEMIN_GEOJSON)
    col_code = detecter_colonne_code(gdf_dept)
    gdf_dept = gdf_dept.to_crs("EPSG:4326")
    
    # Extraction infractions
    conn = sqlite3.connect(CHEMIN_DB)
    df_infractions = extraire_infractions(conn, limite=LIMITE_ECHANTILLON)
    conn.close()
    
    print(f"Traitement de {len(df_infractions):,} infractions")
    
    # Conversion en GeoDataFrame
    gdf_infractions = convertir_en_geodataframe(df_infractions)
    
    # Jointure spatiale
    print("Jointure spatiale en cours...")
    df_joint = gpd.sjoin(
        gdf_infractions, 
        gdf_dept[[col_code, "geometry"]], 
        how="left", 
        predicate="within"
    )
    
    # Calcul statistiques
    resultats = calculer_statistiques(df_joint, col_code)
    
    # Sauvegarde
    CHEMIN_SORTIE.parent.mkdir(parents=True, exist_ok=True)
    resultats.to_csv(CHEMIN_SORTIE, index=False)
    
    print(f"Résultats: {len(resultats)} départements")


if __name__ == "__main__":
    main()