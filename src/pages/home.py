# src/pages/home.py

from dash import Dash, html, dcc
from dash.dependencies import Input, Output

from src.components.header import header
from src.components.navbar import navbar
from src.components.footer import footer

# ⚠️ on importe BIEN register_callbacks ici
from src.pages.simple_page import layout as simple_layout, register_callbacks


def create_app() -> Dash:
    app = Dash(
        __name__,
        suppress_callback_exceptions=True,
        title="Radar Dashboard",
    )
    server = app.server

    # ---------- Layout global ----------
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

    # 🔗 ICI : on enregistre les callbacks de simple_page
    register_callbacks(app)

    # ---------- Routage ----------
    ROUTES = {
        "/": lambda: html.Div(
            [
                html.H2("Bienvenue 👋"),
                html.P("Choisissez une page dans la barre de navigation."),
            ]
        ),
        "/simple": lambda: simple_layout,   # Dashboard
    }

    @app.callback(Output("page-content", "children"), Input("url", "pathname"))
    def display_page(pathname: str):
        if not pathname:
            pathname = "/"
        render = ROUTES.get(pathname)
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


# Ce bloc n'est utilisé que si tu lances directement home.py
if __name__ == "__main__":
    app = create_app()
    app.run_server(debug=True, host="127.0.0.1", port=8050)
