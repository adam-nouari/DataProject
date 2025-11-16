# main.py — Lance le dashboard avec initialisation automatique
import sys
from pathlib import Path

def check_and_init():
    """Vérifie et initialise les données si nécessaire"""
    
    print("\n" + "="*60)
    print("🚀 INITIALISATION DU PROJET RADAR")
    print("="*60 + "\n")
    
    # Chemins à vérifier
    DB_PATH = Path("data/database/vitesses.db")
    AGG_PATH = Path("data/cleaned/vitesses_agg_2023.csv")
    DEPT_PATH = Path("data/cleaned/infractions_par_dept_agg.csv")
    RAW_PATH = Path("data/raw/vitesse_2023.csv")
    CLEANED_PATH = Path("data/cleaned/vitesse_2023_cleaned.csv")
    
    # Étape 1 : Téléchargement des données brutes
    if not RAW_PATH.exists():
        print("📥 [1/5] Téléchargement des données brutes...")
        try:
            from src.utils.get_data import main as download_data
            download_data()
            print("✅ Téléchargement terminé\n")
        except Exception as e:
            print(f"❌ Erreur lors du téléchargement : {e}")
            sys.exit(1)
    else:
        print("✅ [1/5] Données brutes déjà présentes\n")
    
    # Étape 2 : Nettoyage des données
    if not CLEANED_PATH.exists():
        print("🧹 [2/5] Nettoyage des données...")
        try:
            from src.utils.clean_data import main as clean_data
            clean_data()
            print("✅ Nettoyage terminé\n")
        except Exception as e:
            print(f"❌ Erreur lors du nettoyage : {e}")
            sys.exit(1)
    else:
        print("✅ [2/5] Données nettoyées déjà présentes\n")
    
    # Étape 3 : Création de la base SQLite
    if not DB_PATH.exists():
        print("🗄️  [3/5] Création de la base de données SQLite...")
        print("⏱️  Cela peut prendre 5-10 minutes...")
        try:
            from src.utils.load_to_sqlite import main as load_to_db
            load_to_db()
            print("✅ Base de données créée\n")
        except Exception as e:
            print(f"❌ Erreur lors de la création de la base : {e}")
            sys.exit(1)
    else:
        print("✅ [3/5] Base de données déjà présente\n")
    
    # Étape 4 : Agrégation pour le dashboard
    if not AGG_PATH.exists():
        print("📊 [4/5] Génération des données agrégées pour le dashboard...")
        try:
            from src.utils.build_dashboard_cache import main as build_cache
            build_cache()
            print("✅ Données agrégées créées\n")
        except Exception as e:
            print(f"❌ Erreur lors de l'agrégation : {e}")
            sys.exit(1)
    else:
        print("✅ [4/5] Données agrégées déjà présentes\n")
    
    # Étape 5 : Agrégation par département pour la géolocalisation
    if not DEPT_PATH.exists():
        print("🗺️  [5/5] Génération de la carte par département...")
        print("⏱️  Cela peut prendre 5-10 minutes (jointure spatiale)...")
        try:
            from src.utils.build_radars_departements import main as build_geo
            build_geo()
            print("✅ Carte des départements créée\n")
        except Exception as e:
            print(f"⚠️  Avertissement : {e}")
            print("⚠️  La carte de géolocalisation ne sera pas disponible")
            print("⚠️  Le dashboard fonctionnera quand même\n")
    else:
        print("✅ [5/5] Carte des départements déjà présente\n")
    
    print("="*60)
    print("✅ INITIALISATION TERMINÉE")
    print("="*60 + "\n")

def main():
    """Point d'entrée principal"""
    
    # Vérifier et initialiser les données
    check_and_init()
    
    # Lancer le dashboard
    print("🌐 Lancement du dashboard...\n")
    
    from src.pages.home import create_app
    app = create_app()
    
    print("\n" + "="*60)
    print("🎉 DASHBOARD PRÊT !")
    print("="*60)
    print("\n📍 Accédez au dashboard ici : http://127.0.0.1:8050/")
    print("\n📂 Pages disponibles :")
    print("   • Accueil : http://127.0.0.1:8050/")
    print("   • Dashboard : http://127.0.0.1:8050/simple")
    print("   • Géolocalisation : http://127.0.0.1:8050/complex")
    print("   • À propos : http://127.0.0.1:8050/about")
    print("\n⚠️  Pour arrêter : Ctrl+C\n")
    print("="*60 + "\n")
    
    app.run(debug=False, host="127.0.0.1", port=8050)

if __name__ == "__main__":
    main()