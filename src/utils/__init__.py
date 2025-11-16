"""
Package utilitaire pour le pipeline de données.

Il regroupe :
- Téléchargement des données brutes
- Nettoyage des CSV
- Import dans SQLite + ajout de la colonne 'periode'
- Génération des tables agrégées pour le dashboard
"""

# --- Téléchargement des données ---
from .get_data import main as download_raw

# --- Nettoyage des données ---
from .clean_data import main as clean_raw
from .clean_data import clean_file

# --- Construction de la base SQLite + colonne 'periode' ---
from .load_to_sqlite import main as load_database
from .load_to_sqlite import (
    import_csvs_to_sqlite,
    tag_periode_inplace,
    ensure_periode_column,
)

# --- Construction des fichiers agrégés pour le dashboard ---
from .build_dashboard_cache import main as build_cache
from .build_radars_departements import main as build_geo

__all__ = [
    # Téléchargement
    "download_raw",
    # Nettoyage
    "clean_raw", "clean_file",
    # Base SQLite
    "load_database", "import_csvs_to_sqlite",
    "tag_periode_inplace", "ensure_periode_column",
    # Fichiers agrégés
    "build_cache", "build_geo",
]
