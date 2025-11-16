"""
Composant footer du dashboard.
"""
from dash import html
from datetime import datetime


def footer() -> html.Footer:
    """
    Crée le pied de page de l'application.
    
    Returns:
        Composant Footer Dash
    """
    annee_courante = datetime.now().year
    
    liens_externes = [
        ("GitHub", "https://github.com/adam-nouari/DataProject"),
        ("Data.gouv.fr", "https://www.data.gouv.fr/fr/datasets/jeux-de-donnees-des-vitesses-relevees-par-les-voitures-radars-a-conduite-externalisee/"),
    ]
    
    elements_liens = [
        html.A(
            texte,
            href=url,
            target="_blank",
            style={
                "color": "#ffcc00",
                "marginRight": "1rem" if i == 0 else "0",
                "textDecoration": "none"
            },
        )
        for i, (texte, url) in enumerate(liens_externes)
    ]
    
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
                f"© {annee_courante} - Projet Data ESIEE | Développé en Python & Dash",
                style={"margin": "0", "fontSize": "0.9rem"},
            ),
            html.Div(elements_liens, style={"marginTop": "0.5rem"}),
        ],
    )