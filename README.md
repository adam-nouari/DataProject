# 🚗 Radar Dashboard — Analyse des vitesses relevées par les radars

> Tableau de bord interactif pour explorer et analyser les vitesses relevées par les voitures-radars en France (data.gouv.fr).

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Dash](https://img.shields.io/badge/Dash-3.2.0-blue)
![SQLite](https://img.shields.io/badge/SQLite-Database-blueviolet)
![Plotly](https://img.shields.io/badge/Plotly-Visualisation-orange)
![API](https://img.shields.io/badge/API-Sunrise%2FSunset-yellow)
![License](https://img.shields.io/badge/License-ESIEE--Student-lightgrey)

---

## 📚 Description

Ce projet consiste à développer un **dashboard web interactif** permettant :
- d’explorer les vitesses mesurées par les voitures-radars en France,
- d’analyser les dépassements,
- de visualiser les localisations sur carte,
- d’utiliser une **API solaire** (lever/coucher du soleil) pour enrichir les analyses.

Le dashboard est réalisé en **Dash / Plotly**, avec une gestion de données en **SQLite**, et un nettoyage préalable des fichiers CSV bruts.

## 🧭 User Guide

### 🔧 Installation

1. Cloner le dépôt
```bash
git clone https://github.com/adam-nouari/DataProject.git
cd DataProject
```
2. Créer et activer un environnement virtuel
**Windows :**
```bash
python -m venv .venv
.venv\Scripts\activate
```
**Linux / macOS :**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
3. Installer les dépendances
```bash
pip install -r requirements.txt
```
### 🗄️ Préparation des données
L’application est conçue pour que main.py fasse tout automatiquement :

- Téléchargement des données CSV (via src/utils/get_data.py)
- Nettoyage et normalisation (via src/utils/clean_data.py)
- Création de la base SQLite (via src/utils/load_to_sqlite.py)
- Lancement du dashboard

Aucune manipulation manuelle n'est nécessaire.
Le script détecte automatiquement si la base existe déjà pour éviter un reprocessing inutile.
### 🚀 Lancer le Dashboard
```bash
python main.py
```
Le dashboard est accessible à :
👉 http://127.0.0.1:8050

## 📊 Data

### 🌐 Source Utilisé

Les données proviennent du jeu officiel sur data.gouv.fr :
- https://www.data.gouv.fr/fr/datasets/jeux-de-donnees-des-vitesses-relevees-par-les-voitures-radars-a-conduite-externalisee/

Nous utilisons exclusivement le fichier :

- opendata-vitesses-pratiquees-voitures-radars-2023-01-01-2023-12-31.csv

Détails :
- Taille : 667 Mo (CSV)
- Volume : 12 Milions de lignes 

Les colonnes exploitées :
- `date`  
- `position`  
- `mesure` (vitesse mesurée)  
- `limite` (vitesse limite)  
- `periode` (jour-nuit)

Traitement des données :
- Téléchargement automatique des vitesses relevées
- Nettoyage des données
- Création de la database sur SQLite
- Appel de l'API

---

## 🌞 Données externes — API Solaire

Pour déterminer le **moment du jour** (lever, journée, coucher, nuit), nous utilisons l’API officielle :

API :  
https://api.sunrise-sunset.org/json  

Exemple d'appel :  
https://api.sunrise-sunset.org/json?lat=36.72016&lng=-4.42034&date=2025-11-12

## Developer Guide
### 🗂️ Architecture du projet

```bash
    data_project
|-- .gitignore
|-- .venv
|   |-- *
|-- config.py                                   # fichier de configuration
|-- main.py                                     # fichier principal permettant de lancer le dashboard
|-- requirements.txt                            # liste des packages additionnels requis
|-- README.md
|-- data                                        # les données
│   |-- cleaned
│   │   |-- vitesse_2023_cleaned.csv
│   |-- database
│   │   |-- vitesse.db
│   |-- raw
│       |-- vitesse_2023.csv
|-- images
│   |-- 70kmh_jour.png
│   |-- 70kmh_nuit.png
│   |-- 110kmh_jour.png
│   |-- 110kmh_nuit.png
│   |-- dashboard.png
|-- src                                         # le code source du dashboard
|   |-- components                              # les composants du dashboard
|   |   |-- __init__.py
|   |   |-- footer.py
|   |   |-- header.py
|   |   |-- navbar.py
|   |-- pages                                   # les pages du dashboard
|   |   |-- __init__.py
|   |   |-- simple_page.py
|   |   |-- more_complex_page
|   |   |   |-- __init__.py
|   |   |   |-- layout.py
|   |   |   |-- page_specific_component.py
|   |   |-- home.py
|   |   |-- about.py
|   |-- utils                                   # les fonctions utilitaires
|   |   |-- __init__.py
|   |   |-- build_dashboard_cache.py
|   |   |-- get_data.py                         # script de récupération des données
|   |   |-- clean_data.py                       # script de nettoyage des données
|   |   |-- load_to_sqlite.py                         # script qui importe sur sqlite
|-- video.mp4
```
---
## Ajouter une nouvelle page

Etape 1 : Créer un fichier : 
```bash
# src/pages/ma_page.py
from dash import html
def layout():
    return html.Div([html.H3("Nouvelle page")])
```

Etape 2 : Ajouter la route dans `src/pages/home.py`
```bash
from src.pages.ma_page import layout as new_page
ROUTES["/ma_page"] = new_page
```
Etape 3 : Ajouter dans le lien dans `src/components/navbar.py`
```bash
dcc.Link("ma_page", href="/simple", style={"color": "white", "textDecoration": "none", "marginRight": "1.5rem"},),
```

## 🧠 Rapport d'analyse
La section suivante présente les principaux enseignements tirés de l’analyse des données, accompagnés de visualisations issues du dashboard.
Ce dashboard met en évidence que la majorité des conducteurs respecte les limitations de vitesse, avec plus de 60 % de trajets sans infraction.
![Dashboard](images/dashboard.png "Dashboard")
On se rend compte que plus la limitation est élevée, plus le nombre d’infractions augmente. On peut également supposer que durant la nuit, avec un trafic plus faible, les conducteurs ont tendance à relâcher leur vigilance et à rouler plus vite.
![70kmh jour](images/70kmh_jour.png "70kmh jour")

![70kmh nuit](images/70kmh_nuit.png "70kmh nuit")

![110kmh jour](images/110kmh_jour.png "110kmh jour")

![110kmh nuit](images/110kmh_nuit.png "110kmh nuit")
La carte montre une répartition géographique des infractions concentrée dans l’Ouest et le Nord de la France. Ces zones apparaissent nettement plus chargées, mais cela ne signifie pas que ces régions “infractionnent plus” que les autres : la distribution reflète avant tout la couverture réelle du dataset, qui n’inclut pas l’Île-de-France ni une grande partie du Sud du pays.<br>
En l’absence de ces régions, les départements visibles correspondent principalement
à la façade Atlantique,au Nord et Nord-Ouest,et à une partie de l’Est.<br>
Il est donc normal que les infractions semblent fortement concentrées dans ces zones.
![Geolocalisation](images/Géolocalisation.png "Géolocalisation")

## © Copyright

Je déclare sur l’honneur que l’ensemble du code présent dans ce dépôt est une production originale réalisée par notre binôme, à l’exception des éléments explicitement listés ci-dessous: