"""
Page d'analyse statistique des excès de vitesse.
Affiche un histogramme interactif avec filtres par période et limitation.
"""
import pandas as pd
import plotly.express as px
from dash import html, dcc
from dash.dependencies import Input, Output
from pathlib import Path


CHEMIN_AGG = Path("data/cleaned/vitesses_agg_2023.csv")

# Chargement données
donnees = pd.read_csv(CHEMIN_AGG)

ORDRE_CLASSES = [
    "≤ 0 km/h (respect)",
    "0–10 km/h",
    "10–20 km/h",
    "20–30 km/h",
    "> 30 km/h",
]

LIMITATIONS_DISPONIBLES = sorted(donnees["limitation"].dropna().unique())


layout = html.Div([
    html.Div([
        html.H2(
            "Analyse des excès de vitesse selon les limitations",
            style={
                "textAlign": "center",
                "marginBottom": "0.5rem",
                "fontSize": "2rem",
                "fontWeight": "600"
            },
        ),
        html.H3(
            "Distribution des dépassements de vitesse en fonction de la période (jour / nuit) et de la limitation",
            style={
                "textAlign": "center",
                "color": "#444",
                "fontSize": "1.3rem",
                "marginBottom": "1.5rem",
                "fontWeight": "500",
                "letterSpacing": "0.3px"
            },
        ),
        
        html.Div([
            # Filtres
            html.Div([
                html.Div([
                    html.Label("Période", style={"fontWeight": "600", "marginBottom": "0.25rem"}),
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
                ], style={"flex": "1", "minWidth": "180px"}),
                
                html.Div([
                    html.Label("Limitation de vitesse", 
                             style={"fontWeight": "600", "marginBottom": "0.25rem"}),
                    dcc.Dropdown(
                        id="filtre-limitation",
                        options=[
                            {"label": f"{int(lim)} km/h", "value": lim}
                            for lim in LIMITATIONS_DISPONIBLES
                        ],
                        value=None,
                        placeholder="Toutes les limitations",
                        clearable=True,
                        style={"width": "220px", "fontSize": "0.9rem"},
                    ),
                ], style={"flex": "1", "minWidth": "220px"}),
            ], style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "2rem",
                "marginBottom": "1.5rem",
                "alignItems": "flex-end",
            }),
            
            # Graphique
            dcc.Graph(id="hist-taux-depassement", config={"displayModeBar": False}),
            
        ], style={
            "backgroundColor": "white",
            "borderRadius": "14px",
            "padding": "1.75rem",
            "boxShadow": "0 4px 14px rgba(0, 0, 0, 0.08)",
            "border": "1px solid #dde3f0",
        }),
    ], style={
        "maxWidth": "1100px",
        "margin": "0 auto",
        "padding": "1.5rem 1.5rem 3rem 1.5rem",
    })
])


def register_callbacks(app):
    """
    Enregistre les callbacks de la page.
    
    Args:
        app: Application Dash
    """
    @app.callback(
        Output("hist-taux-depassement", "figure"),
        Input("filtre-periode", "value"),
        Input("filtre-limitation", "value"),
    )
    def mettre_a_jour_graphique(periode, limitation):
        """
        Met à jour le graphique selon les filtres sélectionnés.
        
        Args:
            periode: Période sélectionnée (toutes/jour/nuit)
            limitation: Limitation de vitesse sélectionnée
            
        Returns:
            Figure Plotly mise à jour
        """
        df = donnees.copy()
        
        # Application des filtres
        if periode in ["jour", "nuit"]:
            df = df[df["periode"] == periode]
        
        if limitation is not None:
            df = df[df["limitation"] == limitation]
        
        # Calcul des statistiques
        comptages = (
            df.groupby("classe_depassement")["count"]
            .sum()
            .reindex(ORDRE_CLASSES, fill_value=0)
        )
        
        total = comptages.sum()
        pourcentages = (comptages / total * 100).round(2) if total > 0 else [0] * len(ORDRE_CLASSES)
        
        df_graphique = pd.DataFrame({
            "classe": ORDRE_CLASSES, 
            "taux": pourcentages
        })
        
        # Création du graphique
        titre = f"Distribution des dépassements ({int(total):,} mesures)".replace(",", " ")
        
        fig = px.bar(
            df_graphique,
            x="classe",
            y="taux",
            labels={"classe": "Niveau de dépassement", "taux": "Pourcentage (%)"},
            title=titre,
        )
        
        fig.update_traces(
            marker_color="#4361ee",
            marker_line_color="#27408b",
            marker_line_width=1.5,
            hovertemplate="Niveau : %{x}<br>Pourcentage : %{y:.1f}%<extra></extra>",
        )
        
        fig.update_layout(
            title_x=0.5,
            title_font=dict(size=22),
            xaxis_title_font=dict(size=16),
            yaxis_title_font=dict(size=16),
            font=dict(size=12),
            bargap=0.25,
            plot_bgcolor="rgba(248, 250, 255, 1)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickangle=0),
            yaxis=dict(gridcolor="rgba(200, 210, 230, 0.6)", zeroline=False),
            margin=dict(l=60, r=40, t=80, b=60),
        )
        
        fig.update_yaxes(ticksuffix=" %")
        
        return fig