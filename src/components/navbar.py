# src/components/navbar.py
"""
Composant Navbar du dashboard
Barre de navigation simple (Accueil, À propos, Pages, etc.)
"""

from dash import html, dcc

def navbar():
    """
    Retourne la barre de navigation.
    Personnalise les liens selon les pages de ton dashboard.
    """
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
            # Section gauche : titre / logo / accueil
            html.Div(
                [
                    dcc.Link(
                        "🏠 Accueil",
                        href="/",
                        style={
                            "color": "white",
                            "textDecoration": "none",
                            "fontWeight": "bold",
                            "marginRight": "1.5rem",
                        },
                    ),
                    dcc.Link(
                        "📊 Dashboard",
                        href="/simple",
                        style={"color": "white", "textDecoration": "none", "marginRight": "1.5rem"},
                    ),
                    dcc.Link(
                        "📈 Géolocalisation",
                        href="/complex",
                        style={"color": "white", "textDecoration": "none", "marginRight": "1.5rem"},
                    ),
                    dcc.Link(
                        "ℹ️ À propos",
                        href="/about",
                        style={"color": "white", "textDecoration": "none"},
                    ),
                ],
                style={"display": "flex", "alignItems": "center"},
            ),
        ],
    )
