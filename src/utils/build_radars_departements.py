from pathlib import Path
import sqlite3
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from tqdm import tqdm

DB_PATH = Path("data/database/vitesses.db")
GEO_PATH = Path("data/geo/departements.geojson")
OUT_PATH = Path("data/cleaned/infractions_par_dept_agg.csv")

def main():
    print("🚀 Agrégation des infractions par département (VRAIES DONNÉES)")
    print("⏱️  Cela peut prendre 5-10 minutes selon la taille de la base...\n")
    
    # 1. Charger les limites des départements
    print("[1/5] Chargement du GeoJSON des départements...")
    if not GEO_PATH.exists():
        raise FileNotFoundError(f"❌ Fichier manquant : {GEO_PATH}")
    
    gdf_dept = gpd.read_file(GEO_PATH)
    
    # Vérifier les colonnes disponibles
    print(f"   Colonnes trouvées : {list(gdf_dept.columns)}")
    
    # Identifier la colonne du code département (peut varier)
    code_col = None
    for col in ['code', 'code_dept', 'CODE_DEPT', 'nom', 'INSEE_DEP']:
        if col in gdf_dept.columns:
            code_col = col
            break
    
    if code_col is None:
        print("⚠️  Colonnes disponibles:", list(gdf_dept.columns))
        code_col = input("Entre le nom de la colonne pour le code département : ")
    
    print(f"✅ {len(gdf_dept)} départements chargés (colonne: {code_col})")
    gdf_dept = gdf_dept.to_crs("EPSG:4326")  # WGS84
    
    # 2. Extraire les infractions depuis la base
    print("\n[2/5] Extraction des infractions depuis la base...")
    conn = sqlite3.connect(DB_PATH)
    
    # On prend TOUTES les infractions (enlève LIMIT pour production)
    query = """
        SELECT 
            position,
            (vitesse_mesuree - limitation) as depassement
        FROM vitesses
        WHERE annee = 2023 
          AND (vitesse_mesuree - limitation) > 0
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    print(f"✅ {len(df):,} infractions extraites")
    
    # 3. Convertir les positions en géométries
    print("\n[3/5] Conversion des coordonnées GPS en points...")
    
    # Les positions sont séparées par un ESPACE (pas une virgule)
    coords = df["position"].str.split(expand=True, n=1)
    coords.columns = ["lat", "lon"]
    coords = coords.apply(pd.to_numeric, errors="coerce")
    
    df = pd.concat([df, coords], axis=1)
    df = df.dropna(subset=["lat", "lon"])
    
    print(f"✅ {len(df):,} positions valides")
    
    # Créer les géométries Point
    geometry = [Point(lon, lat) for lon, lat in zip(df["lon"], df["lat"])]
    gdf_infractions = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    
    # 4. Jointure spatiale (la partie qui prend du temps)
    print("\n[4/5] Jointure spatiale (mapping GPS → département)...")
    print("   ⏳ Patience, cette étape peut prendre 5-10 minutes...")
    
    joined = gpd.sjoin(
        gdf_infractions, 
        gdf_dept[[code_col, "geometry"]], 
        how="left", 
        predicate="within"
    )
    
    print(f"✅ Jointure terminée")
    
    # 5. Agrégation par département
    print("\n[5/5] Agrégation des statistiques par département...")
    
    agg = (
        joined.groupby(code_col)
        .agg({
            "depassement": ["count", "mean", "median", "max"]
        })
        .reset_index()
    )
    
    # Renommer les colonnes
    agg.columns = [
        "code_dept", 
        "nb_infractions", 
        "depassement_moyen",
        "depassement_median",
        "depassement_max"
    ]
    
    # Arrondir les valeurs
    agg["depassement_moyen"] = agg["depassement_moyen"].round(2)
    agg["depassement_median"] = agg["depassement_median"].round(2)
    
    # Trier par nombre d'infractions
    agg = agg.sort_values("nb_infractions", ascending=False)
    
    print(f"✅ {len(agg)} départements avec infractions")
    
    # 6. Sauvegarder
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    agg.to_csv(OUT_PATH, index=False)
    
    print(f"\n✅ Fichier sauvegardé : {OUT_PATH}")
    print("\n📊 Top 5 départements avec le plus d'infractions :")
    print(agg.head(5).to_string(index=False))
    
    print("\n🎯 Lance maintenant : python main.py")
    print("   Et va sur la page Géolocalisation !")

if __name__ == "__main__":
    main()