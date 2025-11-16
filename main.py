"""
Point d'entrée principal du dashboard.
Vérifie l'existence des fichiers de données et les génère si nécessaire.
"""
import sys
from pathlib import Path


def verifier_donnees():
    """
    Vérifie la présence des fichiers nécessaires et les génère au besoin.
    
    Returns:
        bool: True si toutes les données sont prêtes, False sinon
    """
    db_path = Path("data/database/vitesses.db")
    agg_path = Path("data/cleaned/vitesses_agg_2023.csv")
    dept_path = Path("data/cleaned/infractions_par_dept_agg.csv")
    raw_path = Path("data/raw/vitesse_2023.csv")
    cleaned_path = Path("data/cleaned/vitesse_2023_cleaned.csv")
    
    # Téléchargement si nécessaire
    if not raw_path.exists():
        print("Téléchargement des données...")
        try:
            from src.utils.get_data import main as telecharger
            telecharger()
        except Exception as e:
            print(f"Erreur téléchargement: {e}")
            return False
    
    # Nettoyage
    if not cleaned_path.exists():
        print("Nettoyage des données...")
        try:
            from src.utils.clean_data import main as nettoyer
            nettoyer()
        except Exception as e:
            print(f"Erreur nettoyage: {e}")
            return False
    
    # Base de données
    if not db_path.exists():
        print("Création base de données (ceci peut prendre quelques minutes)...")
        try:
            from src.utils.load_to_sqlite import main as creer_db
            creer_db()
        except Exception as e:
            print(f"Erreur création BDD: {e}")
            return False
    
    # Agrégations
    if not agg_path.exists():
        print("Génération des agrégations...")
        try:
            from src.utils.build_dashboard_cache import main as agreger
            agreger()
        except Exception as e:
            print(f"Erreur agrégation: {e}")
            return False
    
    # Carte départements
    if not dept_path.exists():
        print("Calcul des statistiques par département...")
        try:
            from src.utils.build_radars_departements import main as calculer_geo
            calculer_geo()
        except Exception as e:
            print(f"Attention: carte non disponible ({e})")
    
    return True


if __name__ == "__main__":
    # Vérification et préparation des données
    if not verifier_donnees():
        sys.exit(1)
    
    # Lancement du serveur
    from src.pages.home import create_app
    
    app = create_app()
    print("\nDashboard accessible sur http://127.0.0.1:8050/")
    print("Ctrl+C pour arrêter\n")
    
    app.run(debug=False, host="127.0.0.1", port=8050)