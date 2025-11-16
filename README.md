# Radar Dashboard — Analyse des vitesses relevées par les radars automatiques

> Tableau de bord interactif d'analyse des excès de vitesse détectés par les radars automatiques en France (2023)

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Dash](https://img.shields.io/badge/Dash-3.3.0-blue)
![SQLite](https://img.shields.io/badge/SQLite-Database-blueviolet)
![Plotly](https://img.shields.io/badge/Plotly-Visualisation-orange)
![Tests](https://img.shields.io/badge/Tests-21%20passed-success)
![License](https://img.shields.io/badge/License-ESIEE--Student-lightgrey)

---

## Description

Application web interactive permettant l'analyse approfondie des infractions routières détectées par les radars automatiques en France. Le projet combine :

- **Visualisations statistiques** : Distribution des dépassements par classe et limitation
- **Cartographie interactive** : Géolocalisation des infractions par département
- **Enrichissement des données** : Calcul automatique des périodes jour/nuit via éphémérides astronomiques
- **Pipeline automatisé** : Téléchargement, nettoyage, agrégation et visualisation

**Technologies :** Dash/Plotly (frontend), SQLite (backend), Pandas/GeoPandas (traitement), Astral (API astronomique)

---

## User Guide

### Prérequis

- Python 3.10 ou supérieur
- Connexion internet (téléchargement initial ~670 Mo)
- 2 Go d'espace disque disponible

### Installation rapide

```bash
# 1. Cloner le dépôt
git clone https://github.com/adam-nouari/DataProject.git
cd DataProject

# 2. Créer l'environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Windows :
venv\Scripts\activate
# Linux/macOS :
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Lancer l'application
python main.py
```

### Premier lancement

**Durée estimée : 15-20 minutes**

Le script effectue automatiquement :
1. Téléchargement des données depuis Data.gouv.fr (~670 Mo)
2. Nettoyage et normalisation des données
3. Création de la base SQLite (~12 millions de lignes)
4. Calcul des périodes jour/nuit (éphémérides astronomiques)
5. Génération des agrégations pour le dashboard
6. Lancement du serveur web

**Lancements suivants : < 5 secondes** (données déjà préparées)

### Accès au Dashboard

Une fois lancé, ouvrez votre navigateur à l'adresse :

**http://127.0.0.1:8050/**

**Pages disponibles :**
- `/` — Accueil
- `/simple` — Dashboard statistique
- `/complex` — Carte de géolocalisation
- `/about` — À propos du projet

Arrêt : `Ctrl+C`

---

## Données

### Source

**Jeu de données officiel :**  
[Data.gouv.fr - Vitesses relevées par les radars automatiques (2023)](https://www.data.gouv.fr/fr/datasets/jeux-de-donnees-des-vitesses-relevees-par-les-voitures-radars-a-conduite-externalisee/)

**Fichier utilisé :**  
`opendata-vitesses-pratiquees-voitures-radars-2023-01-01-2023-12-31.csv`

**Caractéristiques :**
- Taille : 667 Mo (CSV brut)
- Volume : ~12,8 millions de mesures
- Période : Année 2023 complète
- Couverture : France métropolitaine

**Colonnes exploitées :**
| Colonne | Description | Type |
|---------|-------------|------|
| `date` | Date et heure de la mesure | datetime |
| `position` | Coordonnées GPS (lat, lon) | string |
| `mesure` | Vitesse mesurée (km/h) | int |
| `limite` | Limitation en vigueur (km/h) | int |

**Colonne calculée :**
- `periode` : Période jour/nuit (calculée via API Astral)

### Pipeline de traitement

```
Données brutes (CSV)
    ↓ get_data.py — Téléchargement
Données brutes locales
    ↓ clean_data.py — Nettoyage (suppression NaN, normalisation)
Données nettoyées
    ↓ load_to_sqlite.py — Import + calcul périodes (Astral)
Base SQLite enrichie
    ↓ build_dashboard_cache.py — Agrégations statistiques
    ↓ build_radars_departements.py — Jointure spatiale (GeoPandas)
Fichiers prêts pour le dashboard
    ↓ main.py — Lancement Dash
Dashboard interactif
```

### API externe — Calcul astronomique

**Bibliothèque utilisée :** [Astral](https://astral.readthedocs.io/)

Permet de calculer les heures de lever/coucher du soleil pour chaque position GPS et date, afin de déterminer automatiquement si une mesure a été prise de **jour** ou de **nuit**.

**Avantages :**
- Précision géographique (lat/lon)
- Prise en compte du fuseau horaire (Europe/Paris)
- Optimisation par grille (arrondi à 0,1°)

---

## Tests Unitaires

Le projet inclut **21 tests unitaires** couvrant les modules critiques du pipeline de données.

### Couverture des tests

| Module | Tests | Description |
|--------|-------|-------------|
| `test_clean_data.py` | 3 | Nettoyage, renommage colonnes, suppression NaN |
| `test_load_to_sqlite.py` | 4 | Vérification colonnes, localisation fuseau horaire |
| `test_build_cache.py` | 2 | Classification dépassements, agrégation |
| `test_build_radars_departements.py` | 3 | Détection colonnes, conversion GeoDataFrame |
| `test_get_data.py` | 3 | Validation ressources, format URL |
| `test_home.py` | 6 | Création app Dash, imports composants UI |

### Lancer les tests

```bash
# Avec pytest (recommandé)
pytest tests/ -v

# Avec unittest
python -m unittest discover tests

# Avec couverture de code
pytest tests/ --cov=src --cov-report=html
```

**Résultat attendu :**
```
21 passed in 6.50s
```

---

## Architecture du projet

```
DataProject/
├── main.py                          # Point d'entrée (auto-init + serveur)
├── requirements.txt                 # Dépendances Python
├── pytest.ini                       # Configuration tests
├── README.md                        # Documentation du projet
│
├── data/                            # Données du projet
│   ├── raw/                         # Données brutes (auto-téléchargées)
│   │   └── vitesse_2023.csv        # CSV brut Data.gouv.fr (667 Mo)
│   │
│   ├── cleaned/                     # Données nettoyées
│   │   ├── vitesse_2023_cleaned.csv           # CSV nettoyé
│   │   ├── vitesses_agg_2023.csv              # Agrégations dashboard
│   │   └── infractions_par_dept_agg.csv       # Agrégations géographiques
│   │
│   ├── database/                    # Base de données
│   │   └── vitesses.db             # SQLite (12M+ lignes)
│   │
│   └── geo/                         # Données géospatiales
│       └── departements.geojson    # Contours départements français
│
├── images/                          # Captures d'écran pour README
│   ├── dashboard.png               # Vue générale dashboard
│   ├── 70kmh_jour.png              # Analyse 70 km/h jour
│   ├── 70kmh_nuit.png              # Analyse 70 km/h nuit
│   ├── 110kmh_jour.png             # Analyse 110 km/h jour
│   └── 110kmh_nuit.png             # Analyse 110 km/h nuit
│
├── src/                             # Code source
│   ├── components/                  # Composants UI réutilisables
│   │   ├── __init__.py
│   │   ├── header.py               # En-tête application
│   │   ├── navbar.py               # Barre de navigation
│   │   └── footer.py               # Pied de page
│   │
│   ├── pages/                       # Pages du dashboard
│   │   ├── __init__.py
│   │   ├── home.py                 # Routage principal + création app
│   │   ├── simple_page.py          # Page dashboard statistique
│   │   ├── create_geo_loc.py       # Page carte choroplèthe
│   │   └── about.py                # Page à propos (si existe)
│   │
│   └── utils/                       # Scripts de traitement données
│       ├── __init__.py
│       ├── get_data.py             # Téléchargement Data.gouv.fr
│       ├── clean_data.py           # Nettoyage et normalisation CSV
│       ├── load_to_sqlite.py       # Import SQLite + calcul périodes
│       ├── build_dashboard_cache.py        # Agrégations statistiques
│       └── build_radars_departements.py    # Agrégation géographique
│
└── tests/                           # Tests unitaires (pytest)
    ├── __init__.py
    ├── test_clean_data.py          # Tests nettoyage données
    ├── test_load_to_sqlite.py      # Tests import SQLite
    ├── test_build_cache.py         # Tests agrégations
    ├── test_build_radars_departements.py   # Tests géospatial
    ├── test_get_data.py            # Tests téléchargement
    └── test_home.py                # Tests application Dash
```

**Fichiers générés automatiquement (non versionnés) :**
- `.pytest_cache/` : Cache des tests
- `venv/` : Environnement virtuel Python
- `__pycache__/` : Cache Python
- `data/raw/`, `data/cleaned/`, `data/database/` : Données générées

---

## Developer Guide

### Ajouter une nouvelle page

**Étape 1 :** Créer le fichier de page

```python
# src/pages/ma_nouvelle_page.py
from dash import html

layout = html.Div([
    html.H2("Ma nouvelle page"),
    html.P("Contenu de la page...")
])
```

**Étape 2 :** Ajouter la route dans `home.py`

```python
# src/pages/home.py
from src.pages.ma_nouvelle_page import layout as layout_new

# Dans la fonction create_app() :
routes = {
    # ... routes existantes
    "/new": lambda: layout_new,
}
```

**Étape 3 :** Ajouter le lien dans `navbar.py`

```python
# src/components/navbar.py
liens = [
    # ... liens existants
    ("Ma Page", "/new"),
]
```

### Bonnes pratiques respectées

- **PEP 8** : Respect des conventions Python
- **Docstrings** : Format Google/NumPy sur toutes les fonctions
- **Type hints** : Annotations de types sur paramètres/returns
- **Tests** : Couverture des modules critiques
- **DRY** : Éviter la duplication de code

---

## Rapport d'Analyse

### Constats principaux

#### 1. Respect global des limitations

**Plus de 60% des conducteurs respectent les limitations de vitesse**, ce qui témoigne d'une conscience générale des règles de sécurité routière.

![Dashboard principal](images/dashboard.png)

#### 2. Influence de la limitation

**Observation :** Plus la limitation est élevée (90, 110, 130 km/h), plus le taux d'infractions augmente.

**Hypothèse :** Sur les routes à grande vitesse, les conducteurs ont tendance à sous-estimer leur vitesse réelle et à dépasser plus facilement.

#### 3. Différence jour/nuit

**Zones 70 km/h :**
- **Jour** : Trafic dense, respect accru
- **Nuit** : Trafic faible, vigilance réduite, +15% d'infractions

| Limitation 70 km/h - Jour | Limitation 70 km/h - Nuit |
|---------------------------|---------------------------|
| ![70kmh jour](images/70kmh_jour.png) | ![70kmh nuit](images/70kmh_nuit.png) |

**Zones 110 km/h :**
- **Jour** : Infractions modérées
- **Nuit** : Augmentation significative des grands excès (> 20 km/h)

| Limitation 110 km/h - Jour | Limitation 110 km/h - Nuit |
|----------------------------|----------------------------|
| ![110kmh jour](images/110kmh_jour.png) | ![110kmh nuit](images/110kmh_nuit.png) |

**Conclusion :** La nuit, le sentiment de liberté lié à l'absence de trafic favorise les comportements à risque.

---

## Technologies Utilisées

| Catégorie | Technologies |
|-----------|-------------|
| **Frontend** | Dash 3.3.0, Plotly, HTML/CSS |
| **Backend** | Python 3.12, SQLite |
| **Data Processing** | Pandas, NumPy, GeoPandas |
| **Géospatial** | Shapely, GeoJSON |
| **API/Libs** | Astral (astronomie), Requests, tqdm |
| **Tests** | pytest, unittest |

---

## Licence et Crédits

**Projet réalisé dans le cadre du cours de Data Science — ESIEE Paris (2024-2025)**

**Auteur :** Adam Nouari

**Source des données :** [Data.gouv.fr](https://www.data.gouv.fr/) — Licence Ouverte / Open Licence

---

## Liens Utiles

- [Dépôt GitHub](https://github.com/adam-nouari/DataProject)
- [Données source](https://www.data.gouv.fr/fr/datasets/jeux-de-donnees-des-vitesses-relevees-par-les-voitures-radars-a-conduite-externalisee/)
- [Documentation Dash](https://dash.plotly.com/)
- [Astral Documentation](https://astral.readthedocs.io/)

---

## Déclaration d'Originalité

Je déclare sur l'honneur que l'ensemble du code présent dans ce dépôt est une production originale réalisée dans le cadre de ce projet académique, à l'exception des bibliothèques tierces listées dans `requirements.txt` et de la documentation officielle consultée pour l'implémentation.

**Bibliothèques externes utilisées :**
- Dash, Plotly (visualisation)
- Pandas, NumPy (traitement données)
- GeoPandas, Shapely (géospatial)
- Astral (calculs astronomiques)
- Pytest (tests unitaires)