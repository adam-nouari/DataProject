import pandas as pd
import plotly.express as px
from dash import html, dcc
from dash.dependencies import Input, Output
from pathlib import Path

AGG_PATH = Path("data/cleaned/vitesses_agg_2023.csv")

# ------------------------------------------------------------------
# 1) Chargement de la table agrégée (50 lignes)
# ------------------------------------------------------------------
AGG = pd.read_csv(AGG_PATH)

print("[DEBUG] AGG loaded:", AGG.shape)

CLASSES_ORDER = [
    "≤ 0 km/h (respect)",
    "0–10 km/h",
    "10–20 km/h",
    "20–30 km/h",
    "> 30 km/h",
]

LIMITATIONS = sorted(AGG["limitation"].dropna().unique())

# ------------------------------------------------------------------
# 2) Layout : filtres + graphique (version "carte" stylée)
# ------------------------------------------------------------------
layout = html.Div(
    [
        html.Div(
            [
                # Titre page
                html.H2(
                    "Analyse des excès de vitesse selon les limitations",
                    style={
                        "textAlign": "left",
                        "marginBottom": "0.25rem",
                        "fontSize": "2rem",
                    },
                ),
                html.P(
                    "Visualisation de la répartition des dépassements de vitesse "
                    "en fonction de la période (jour / nuit) et de la limitation en vigueur.",
                    style={
                        "marginTop": "0",
                        "marginBottom": "1.5rem",
                        "color": "#555",
                        "fontSize": "0.95rem",
                    },
                ),

                # Carte contenant filtres + graph
                html.Div(
                    [
                        # Ligne de filtres
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label(
                                            "Période",
                                            style={
                                                "fontWeight": "600",
                                                "marginBottom": "0.25rem",
                                            },
                                        ),
                                        dcc.RadioItems(
                                            id="filtre-periode",
                                            options=[
                                                {"label": "Toutes", "value": "toutes"},
                                                {"label": "Jour", "value": "jour"},
                                                {"label": "Nuit", "value": "nuit"},
                                            ],
                                            value="toutes",
                                            inline=True,
                                            style={"fontSize": "0.9rem"},
                                        ),
                                    ],
                                    style={"flex": "1", "minWidth": "180px"},
                                ),
                                html.Div(
                                    [
                                        html.Label(
                                            "Limitation de vitesse",
                                            style={
                                                "fontWeight": "600",
                                                "marginBottom": "0.25rem",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="filtre-limitation",
                                            options=[
                                                {"label": f"{int(lim)} km/h", "value": lim}
                                                for lim in LIMITATIONS
                                            ],
                                            value=None,
                                            placeholder="Toutes les limitations",
                                            clearable=True,
                                            style={"width": "220px", "fontSize": "0.9rem"},
                                        ),
                                    ],
                                    style={"flex": "1", "minWidth": "220px"},
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flexWrap": "wrap",
                                "gap": "2rem",
                                "marginBottom": "1.5rem",
                                "alignItems": "flex-end",
                            },
                        ),

                        # Graphique
                        dcc.Graph(
                            id="hist-taux-depassement",
                            config={"displayModeBar": False},  # pas de barre zoom / export
                        ),
                    ],
                    style={
                        "backgroundColor": "white",
                        "borderRadius": "14px",
                        "padding": "1.75rem",
                        "boxShadow": "0 4px 14px rgba(0, 0, 0, 0.08)",
                        "border": "1px solid #dde3f0",
                    },
                ),
            ],
            style={
                "maxWidth": "1100px",
                "margin": "0 auto",
                "padding": "1.5rem 1.5rem 3rem 1.5rem",
            },
        )
    ]
)

# ------------------------------------------------------------------
# 3) Callbacks (sur la table agrégée uniquement)
# ------------------------------------------------------------------
def register_callbacks(app):
    @app.callback(
        Output("hist-taux-depassement", "figure"),
        Input("filtre-periode", "value"),
        Input("filtre-limitation", "value"),
    )
    def update_histogram(periode, limitation):
        df = AGG.copy()

        # Filtre période
        if periode in ["jour", "nuit"]:
            df = df[df["periode"] == periode]

        # Filtre limitation
        if limitation is not None:
            df = df[df["limitation"] == limitation]

        # Regroupement final par classe
        counts = (
            df.groupby("classe_depassement")["count"]
            .sum()
            .reindex(CLASSES_ORDER, fill_value=0)
        )

        total = counts.sum()

        if total == 0:
            pourcentages = [0] * len(CLASSES_ORDER)
        else:
            pourcentages = (counts / total * 100).round(2)

        df_plot = pd.DataFrame({"classe": CLASSES_ORDER, "taux": pourcentages})

        # Titre dynamique avec nombre de mesures
        titre = (
            "Distribution des dépassements de vitesse par niveau d’infraction "
            f"({int(total):,} mesures)".replace(",", " ")
        )

        fig = px.bar(
            df_plot,
            x="classe",
            y="taux",
            labels={
                "classe": "Niveau de dépassement",
                "taux": "Pourcentage (%)",
            },
            title=titre,
        )

        # Style des barres & hover
        fig.update_traces(
            marker_color="#4361ee",
            marker_line_color="#27408b",
            marker_line_width=1.5,
            hovertemplate=(
                "Niveau de dépassement : %{x}<br>"
                "Pourcentage : %{y:.1f} %<extra></extra>"
            ),
        )

        # Mise en forme générale
        fig.update_layout(
            title_x=0.5,
            title_font=dict(size=22),
            xaxis_title_font=dict(size=16),
            yaxis_title_font=dict(size=16),
            font=dict(size=12),
            bargap=0.25,
            plot_bgcolor="rgba(248, 250, 255, 1)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                showgrid=False,
                tickangle=0,      # labels bien droits
            ),
            yaxis=dict(
                gridcolor="rgba(200, 210, 230, 0.6)",
                zeroline=False,
            ),
            margin=dict(l=60, r=40, t=80, b=60),
        )

        fig.update_yaxes(ticksuffix=" %")

        return fig
