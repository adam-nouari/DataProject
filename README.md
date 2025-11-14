🚗 Radar Dashboard — Résumé du projet
🎯 Objectif

Développer un dashboard interactif permettant d’analyser les vitesses relevées par les voitures-radars en France (2021 & 2023), en appliquant un pipeline complet : nettoyage → base SQLite → visualisation.

📁 Données utilisées

Données officielles : data.gouv.fr, relevées par voitures-radars.

Deux jeux :

2021 : ~6.6M lignes

2023 : ~7.2M lignes

Colonnes conservées : date, latitude, longitude, mesure, limite, dépassement.

⚙️ Pipeline technique

Téléchargement / Clean :

Normalisation des dates

Extraction latitude / longitude

Conversion en float

Base SQLite (vitesses.db) :

insertion via pandas + chunksize

Dashboard Dash/Plotly :

pages (home, simple, complex, about)

composants (header, navbar, footer)

API solaire : moment de la journée (lever / coucher)

📊 Résultats clés

La majorité des mesures respecte la limite mais présence d’une longue queue de dépassements.

Distribution centrée sur les limites usuelles : 50, 90, 130 km/h.

2023 montre davantage de dépassements que 2021.

Les périodes autour du lever/coucher du soleil influencent les comportements.

👨‍💻 Architecture (résumé)
src/
 ├── components/    # Header, navbar, footer, solar card…
 ├── pages/         # pages du dashboard
 └── utils/         # base, nettoyage, API solaire

🚀 Comment lancer
pip install -r requirements.txt
python -m src.utils.Create_Database
python main.py


➡️ Dashboard : http://127.0.0.1:8050

🧾 Déclaration

Projet original réalisé par notre binôme.
Les seules sources externes utilisées :

API Sunrise–Sunset (structure JSON)

Documentation Dash (multi-pages)