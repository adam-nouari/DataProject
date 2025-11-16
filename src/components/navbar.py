"""
Composant barre de navigation du dashboard.
"""
from dash import html, dcc


def navbar() -> html.Nav:
    """
    Crée la barre de navigation.
    
    Returns:
        Composant Nav Dash
    """
    liens = [
        ("Accueil", "/"),
        ("Dashboard", "/simple"),
        ("Géolocalisation", "/complex"),
        ("À propos", "/about"),
    ]
    
    elements_nav = [
        dcc.Link(
            texte,
            href=url,
            style={
                "color": "white",
                "textDecoration": "none",
                "fontWeight": "bold" if i == 0 else "normal",
                "marginRight": "1.5rem" if i < len(liens) - 1 else "0",
            },
        )
        for i, (texte, url) in enumerate(liens)
    ]
    
    return html.Nav(
        className="navbar",
        style={
            "backgroundColor": "#004080",
            "padding": "0.75rem 2rem",
            "display": "flex",
            "justifyContent": "space-between",
            "alignItems": "center",
        },
        children=[
            html.Div(
                elements_nav,
                style={"display": "flex", "alignItems": "center"}
            )
        ],
    )