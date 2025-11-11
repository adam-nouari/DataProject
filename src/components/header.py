# src/components/header.py
"""
Composant Header du dashboard
Affiche le titre principal, un sous-titre et éventuellement un logo.
"""

from dash import html

def header(title: str = "Radar Dashboard", subtitle: str = "Analyse des vitesses relevées par les radars"):
    """
    Retourne le header du dashboard.
    Tu peux modifier les styles ou ajouter un logo facilement.
    """
    return html.Header(
        className="header",
        style={
            "backgroundColor": "#003366",
            "color": "white",
            "padding": "1.5rem",
            "textAlign": "center",
            "borderBottom": "3px solid #ffcc00",
        },
        children=[
            html.H1(title, style={"marginBottom": "0.5rem", "fontSize": "2rem"}),
            html.H3(subtitle, style={"marginTop": "0", "fontWeight": "normal"}),
        ],
    )
