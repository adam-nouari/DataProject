# src/components/footer.py
"""
Composant Footer du dashboard
Affiche les crédits, l'année et éventuellement des liens externes.
"""

from dash import html
from datetime import datetime

def footer():
    """
    Retourne le pied de page du dashboard.
    """
    current_year = datetime.now().year

    return html.Footer(
        className="footer",
        style={
            "backgroundColor": "#003366",
            "color": "white",
            "textAlign": "center",
            "padding": "1rem",
            "marginTop": "2rem",
            "borderTop": "2px solid #ffcc00",
        },
        children=[
            html.P(
                f"© {current_year} - Projet Data ESIEE | Développé en Python & Dash",
                style={"margin": "0", "fontSize": "0.9rem"},
            ),
            html.Div(
                [
                    html.A(
                        "GitHub",
                        href="https://github.com/adam-nouari/DataProject",
                        target="_blank",
                        style={"color": "#ffcc00", "marginRight": "1rem", "textDecoration": "none"},
                    ),
                    html.A(
                        "Data.gouv.fr",
                        href="https://www.data.gouv.fr/fr/datasets/jeux-de-donnees-des-vitesses-relevees-par-les-voitures-radars-a-conduite-externalisee/",
                        target="_blank",
                        style={"color": "#ffcc00", "textDecoration": "none"},
                    ),
                ],
                style={"marginTop": "0.5rem"},
            ),
        ],
    )
