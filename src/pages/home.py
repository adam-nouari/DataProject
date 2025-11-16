# src/pages/home.py
from dash import Dash, html, dcc
from dash.dependencies import Input, Output

from src.components.header import header
from src.components.navbar import navbar
from src.components.footer import footer

from src.pages.simple_page import layout as simple_layout, register_callbacks

# ⚠️ IMPORTANT : importer la page géolocalisation si elle existe
try:
    from src.pages.create_geo_loc import layout as complex_layout
except ImportError:
    complex_layout = html.Div("Page en construction 🚧")


def create_app() -> Dash:
    app = Dash(
        __name__,
        suppress_callback_exceptions=True,
        title="Radar Dashboard",
    )
    server = app.server

    def serve_layout():
        return html.Div(
            id="root",
            children=[
                header(),
                navbar(),
                dcc.Location(id="url", refresh=False),
                html.Div(id="page-content", className="container", style={"padding": "1rem"}),
                footer(),
            ],
        )

    app.layout = serve_layout
    register_callbacks(app)

    # ---------- Routage ----------
    ROUTES = {
        "/": lambda: html.Div([
            html.H2("Bienvenue 👋"),
            html.P("Choisissez une page dans la barre de navigation."),
        ]),
        "/simple": lambda: simple_layout,
        "/complex": lambda: complex_layout,  # ✅ Route ajoutée
        "/about": lambda: html.Div([
            html.H2("À propos"),
            html.P("Projet d'analyse des radars automatiques en France (2023)"),
        ]),
    }

    @app.callback(Output("page-content", "children"), Input("url", "pathname"))
    def display_page(pathname: str):
        if not pathname:
            pathname = "/"
        render = ROUTES.get(pathname)
        if render is None:
            return html.Div([
                html.H3("404 - Page non trouvée"),
                html.P(f"Chemin inconnu : {pathname}"),
                dcc.Link("⟵ Retour à l'accueil", href="/"),
            ], style={"padding": "2rem"})
        return render()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run_server(debug=True, host="127.0.0.1", port=8050)