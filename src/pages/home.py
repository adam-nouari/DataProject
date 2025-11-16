"""
Application principale du dashboard.
Gère le routage entre les différentes pages.
"""
from dash import Dash, html, dcc
from dash.dependencies import Input, Output

from src.components.header import header
from src.components.navbar import navbar
from src.components.footer import footer
from src.pages.simple_page import layout as layout_stats, register_callbacks


try:
    from src.pages.create_geo_loc import layout as layout_geo
except ImportError:
    layout_geo = html.Div("Page en construction", style={"padding": "2rem"})


def create_app() -> Dash:
    """
    Crée et configure l'application Dash.
    
    Returns:
        Application Dash configurée
    """
    app = Dash(__name__, suppress_callback_exceptions=True, title="Radar Dashboard")
    server = app.server

    def creer_layout():
        """Génère le layout principal de l'application."""
        return html.Div(
            id="root",
            children=[
                header(),
                navbar(),
                dcc.Location(id="url", refresh=False),
                html.Div(id="page-content", className="container", 
                        style={"padding": "1rem"}),
                footer(),
            ],
        )

    app.layout = creer_layout
    register_callbacks(app)

    # Définition des routes
    routes = {
        "/": lambda: html.Div([
            html.H2("Bienvenue", style={"textAlign": "center"}),
            html.P("Utilisez le menu de navigation pour accéder aux analyses.",
                  style={"textAlign": "center", "color": "#666"}),
        ]),
        "/simple": lambda: layout_stats,
        "/complex": lambda: layout_geo,
        "/about": lambda: html.Div([
            html.H2("À propos", style={"textAlign": "center"}),
            html.P("Analyse des infractions radar en France - Données 2023",
                  style={"textAlign": "center"}),
            html.P("Source: Data.gouv.fr",
                  style={"textAlign": "center", "fontSize": "0.9rem", "color": "#777"}),
        ]),
    }

    @app.callback(Output("page-content", "children"), Input("url", "pathname"))
    def afficher_page(chemin: str):
        """
        Callback de routage principal.
        
        Args:
            chemin: URL de la page demandée
            
        Returns:
            Layout de la page correspondante
        """
        if not chemin:
            chemin = "/"
        
        generateur = routes.get(chemin)
        
        if generateur is None:
            return html.Div([
                html.H3("Page non trouvée", style={"textAlign": "center"}),
                dcc.Link("Retour à l'accueil", href="/", 
                        style={"display": "block", "textAlign": "center"}),
            ], style={"padding": "2rem"})
        
        return generateur()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run_server(debug=True, host="127.0.0.1", port=8050)