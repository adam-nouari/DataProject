"""
Module de téléchargement des données depuis Data.gouv.fr.
"""
from pathlib import Path
import requests
from tqdm import tqdm


RESSOURCES = {
    "2023": "52200d61-5e80-4a4e-999f-6e1c184fa122",
}

URL_BASE = "https://www.data.gouv.fr/api/1/datasets/r/"
REPERTOIRE_SORTIE = Path("data/raw")


def telecharger_fichier(id_ressource: str, chemin_sortie: Path) -> None:
    """
    Télécharge un fichier depuis l'API Data.gouv.fr.
    
    Args:
        id_ressource: Identifiant de la ressource sur Data.gouv.fr
        chemin_sortie: Chemin où sauvegarder le fichier
    """
    url = f"{URL_BASE}{id_ressource}"
    REPERTOIRE_SORTIE.mkdir(parents=True, exist_ok=True)
    
    with requests.get(url, stream=True, timeout=600) as reponse:
        reponse.raise_for_status()
        taille_totale = int(reponse.headers.get("Content-Length", 0))
        
        with open(chemin_sortie, "wb") as f, tqdm(
            total=taille_totale,
            unit="B",
            unit_scale=True,
            desc=chemin_sortie.name
        ) as barre_progression:
            for chunk in reponse.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    barre_progression.update(len(chunk))


def main():
    """Télécharge tous les fichiers définis dans RESSOURCES."""
    for annee, id_ressource in RESSOURCES.items():
        nom_fichier = f"vitesse_{annee}.csv"
        chemin = REPERTOIRE_SORTIE / nom_fichier
        telecharger_fichier(id_ressource, chemin)


if __name__ == "__main__":
    main()