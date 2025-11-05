from pathlib import Path
import pandas as pd

def clean_file(input_path: Path, output_path: Path):
    """Nettoie un seul fichier CSV et enregistre le résultat."""
    print(f"[INFO] Lecture de {input_path.name}")
    df = pd.read_csv(input_path, sep=";", engine="python")

    # Renommer les colonnes
    df = df.rename(columns={
        "mesure": "vitesse_mesuree",
        "limite": "limitation",
        # on laisse 'date' et 'position' inchangées
    })

    if "2021" in input_path.name:
        # Supprime le "T" entre la date et l'heure
        df["date"] = df["date"].str.replace("T", " ", regex=False)

    # Convertir en numérique
    if "vitesse_mesuree" in df.columns:
        df["vitesse_mesuree"] = pd.to_numeric(df["vitesse_mesuree"], errors="coerce")
    if "limitation" in df.columns:
        df["limitation"] = pd.to_numeric(df["limitation"], errors="coerce")

    # Supprimer les lignes contenant une valeur manquante (NaN)
    avant = len(df)
    df = df.dropna()
    apres = len(df)
    print(f"[INFO] {avant - apres} lignes supprimées (valeurs manquantes)")

    # Sauvegarder dans le dossier cleaned
    df.to_csv(output_path, index=False, sep=";")
    print(f"[OK] Fichier nettoyé enregistré : {output_path.name}\n")

def main():
    raw_dir = Path("data/raw")
    cleaned_dir = Path("data/cleaned")
    cleaned_dir.mkdir(parents=True, exist_ok=True)

    # Fichiers d'entrée et de sortie
    files = {
        "vitesse_2021.csv": "vitesse_2021_cleaned.csv",
        "vitesse_2023.csv": "vitesse_2023_cleaned.csv"
    }

    for raw_name, clean_name in files.items():
        input_path = raw_dir / raw_name
        output_path = cleaned_dir / clean_name
        if not input_path.exists():
            print(f"[WARN] Fichier manquant : {input_path}")
            continue
        clean_file(input_path, output_path)

if __name__ == "__main__":
    main()