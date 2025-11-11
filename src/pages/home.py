# src/pages/home.py
"""
Point d'entrée du dashboard.
- Assemble les composants (header / navbar / footer)
- Gère le routage entre les pages
- Expose app et server (utile pour le déploiement)
"""

from dash import Dash, html, dcc
from dash.dependencies import Input, Output

# === Composants réutilisables ===
from src.components.header import header       # ex: def header(): return html.Div(...)
from src.components.navbar import navbar       # ex: def navbar(): return html.Nav(...)
from src.components.footer import footer       # ex: def footer(): return html.Footer(...)

# === Pages ===
# from src.pages.about import layout as about_layout
# from src.pages.simple_page import layout as simple_layout
# from src.pages.more_complex_page.layout import layout as complex_layout


# ------------------------------------------------------------------------------
# Factory d'app : pratique pour tester/importer ailleurs
# ------------------------------------------------------------------------------
def create_app() -> Dash:
    app = Dash(
        __name__,
        suppress_callback_exceptions=True,  # permet de charger des layouts de pages à la volée
        title="Radar Dashboard",
    )
    # utile pour gunicorn/Render/Heroku
    server = app.server  # noqa: F841 (exposé via app.server)

    # Layout principal (fonction pour toujours reconstruire un état propre)
    def serve_layout():
        return html.Div(
            id="root",
            children=[
                # En-tête
                header(),

                # Barre de navigation
                navbar(),

                # Gestion de l'URL & conteneur de page
                dcc.Location(id="url", refresh=False),
                html.Div(id="page-content", className="container", style={"padding": "1rem"}),

                # Pied de page
                footer(),
            ],
        )

    app.layout = serve_layout

    # ------------------------------------------------------------------------------
    # Routage des pages
    # ------------------------------------------------------------------------------
    ROUTES = {
        "/": lambda: html.Div(
            [
                html.H2("Bienvenue 👋"),
                html.P("Choisissez une page dans la barre de navigation."),
            ]
        ),
      #   "/about": about_layout,
      #   "/simple": simple_layout,
      #   "/complex": complex_layout,
    }

    @app.callback(Output("page-content", "children"), Input("url", "pathname"))
    def display_page(pathname: str):
        # Normalisation simple
        if not pathname:
            pathname = "/"
        # Récupération de la page, sinon 404
        render = ROUTES.get(pathname, None)
        if render is None:
            return html.Div(
                [
                    html.H3("404 - Page non trouvée"),
                    html.P(f"Chemin inconnu : {pathname}"),
                    dcc.Link("⟵ Retour à l'accueil", href="/"),
                ],
                style={"padding": "2rem"},
            )
        return render()

    return app


# ------------------------------------------------------------------------------
# Exécution directe
# ------------------------------------------------------------------------------
app = create_app()
server = app.server  # export pour le déploiement

if __name__ == "__main__":
    app.run_server(debug=True, host="127.0.0.1", port=8050)
