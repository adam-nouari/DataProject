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

---

## 📁 Data

### 📌 Source des données
Les données proviennent du jeu officiel :  
👉 https://www.data.gouv.fr/fr/datasets/jeux-de-donnees-des-vitesses-relevees-par-les-voitures-radars-a-conduite-externalisee/

Deux jeux sont utilisés :
- **2023** : opendata-vitesses-pratiquees-voitures-radars-2023-01-01-2023-12-31.csv

### ⚙️ Préparation des données
1. 🔧 **Nettoyage (`clean_data.py`)**
   - Normalisation des colonnes : `date`, `mesure`, `limite`, `position`
   - Extraction `latitude` / `longitude`
   - Conversion des types
   - Suppression lignes invalides

2. 🗄️ **Création de base SQLite (`Create_Database.py`)**
   - Table `vitesses` avec :  
     `date`, `latitude`, `longitude`, `mesure`, `limite`, `depassement`

3. 🌞 **Enrichissement API solaire**
   - API Sunrise–Sunset : https://api.sunrise-sunset.org/json  
   - Détermine si, pour une position, il fait :  
     🌅 avant lever / ☀️ jour / 🌙 après coucher

---

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

* Téléchargement des données brutes (via src/utils/get_data.py)
* Nettoyage et normalisation (via src/utils/clean_data.py)
* Création de la base SQLite vitesses.db
* Lancement du dashboard

Aucune manipulation manuelle n'est nécessaire.
Le script détecte automatiquement si la base existe déjà pour éviter un reprocessing inutile.
### 🚀 Lancer le Dashboard
```bash
python main.py
```
➡️ Cela déclenche la chaîne complète :

Téléchargement des fichiers bruts si absents

Nettoyage → génération des CSV nettoyés

Construction de la base
data/database/vitesses.db

Démarrage du dashboard Dash

Le dashboard est accessible à :
👉 http://127.0.0.1:8050