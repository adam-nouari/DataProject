"""
Module de nettoyage des données brutes.
Renomme les colonnes et supprime les valeurs manquantes.
"""
from pathlib import Path
import pandas as pd


def nettoyer_fichier(chemin_entree: Path, chemin_sortie: Path) -> None:
    """
    Nettoie un fichier CSV de données radar.
    
    Args:
        chemin_entree: Chemin du fichier CSV brut
        chemin_sortie: Chemin du fichier CSV nettoyé
    """
    df = pd.read_csv(chemin_entree, sep=";", engine="python")
    
    # Renommage des colonnes pour cohérence
    df = df.rename(columns={
        "mesure": "vitesse_mesuree",
        "limite": "limitation",
    })
    
    # Conversion en numérique
    colonnes_numeriques = ["vitesse_mesuree", "limitation"]
    for col in colonnes_numeriques:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Suppression des valeurs manquantes
    nb_lignes_avant = len(df)
    df = df.dropna()
    nb_lignes_apres = len(df)
    
    print(f"  Lignes supprimées: {nb_lignes_avant - nb_lignes_apres}")
    
    # Sauvegarde
    df.to_csv(chemin_sortie, index=False, sep=";")


def main():
    """Nettoie tous les fichiers définis."""
    rep_brut = Path("data/raw")
    rep_nettoye = Path("data/cleaned")
    rep_nettoye.mkdir(parents=True, exist_ok=True)
    
    fichiers = {
        "vitesse_2023.csv": "vitesse_2023_cleaned.csv"
    }
    
    for nom_brut, nom_nettoye in fichiers.items():
        chemin_entree = rep_brut / nom_brut
        chemin_sortie = rep_nettoye / nom_nettoye
        
        if not chemin_entree.exists():
            print(f"Fichier manquant: {nom_brut}")
            continue
        
        nettoyer_fichier(chemin_entree, chemin_sortie)


if __name__ == "__main__":
    main()