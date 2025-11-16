"""
Composant header du dashboard.
"""
from dash import html


def header(titre: str = "Radar Dashboard", 
          sous_titre: str = "Analyse des vitesses relevées par les radars") -> html.Header:
    """
    Crée le header de l'application.
    
    Args:
        titre: Titre principal
        sous_titre: Sous-titre descriptif
        
    Returns:
        Composant Header Dash
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
            html.H1(titre, style={"marginBottom": "0.5rem", "fontSize": "2rem"}),
            html.H3(sous_titre, style={"marginTop": "0", "fontWeight": "normal"}),
        ],
    )