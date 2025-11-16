"""
Page de géolocalisation des infractions.
Affiche une carte choroplèthe interactive par département.
"""
from pathlib import Path
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
import json


CHEMIN_DONNEES = Path("data/cleaned/infractions_par_dept_agg.csv")
CHEMIN_GEOJSON = Path("data/geo/departements.geojson")

# Chargement des données
if CHEMIN_DONNEES.exists():
    df_departements = pd.read_csv(CHEMIN_DONNEES)
    df_departements['code_dept'] = df_departements['code_dept'].astype(str).str.zfill(2)
else:
    df_departements = pd.DataFrame({"code_dept": [], "nb_infractions": []})

# Chargement GeoJSON
if CHEMIN_GEOJSON.exists():
    with open(CHEMIN_GEOJSON, "r", encoding="utf-8") as f:
        geojson_departements = json.load(f)
else:
    geojson_departements = None


def creer_carte():
    """
    Crée la carte choroplèthe des infractions par département.
    
    Returns:
        Figure Plotly de la carte
    """
    if geojson_departements is None or df_departements.empty:
        return go.Figure().add_annotation(
            text="Données manquantes",
            xref="paper", yref="paper", x=0.5, y=0.5, 
            showarrow=False, font=dict(size=16)
        )
    
    # Complétion avec tous les départements du GeoJSON
    codes_tous = [f['properties']['code'] for f in geojson_departements['features']]
    df_complet = pd.DataFrame({'code_dept': codes_tous})
    df_complet = df_complet.merge(df_departements, on='code_dept', how='left').fillna(0)
    
    # Création de la carte
    fig = go.Figure(go.Choroplethmapbox(
        geojson=geojson_departements,
        locations=df_complet["code_dept"],
        z=df_complet["nb_infractions"],
        featureidkey="properties.code",
        colorscale=[
            [0, '#fee5d9'],
            [0.2, '#fcbba1'],
            [0.4, '#fc9272'],
            [0.6, '#fb6a4a'],
            [0.8, '#de2d26'],
            [1, '#a50f15']
        ],
        marker_opacity=0.85,
        marker_line_width=1.5,
        marker_line_color='#444444',
        text=df_complet["code_dept"],
        hovertemplate="<b>Département %{text}</b><br>Infractions: %{z:,.0f}<br><extra></extra>",
        colorbar=dict(title="Infractions", x=1.02),
    ))
    
    fig.update_layout(
        mapbox_style="white-bg",
        mapbox_zoom=4.3,
        mapbox_center={"lat": 46.5, "lon": 2.3},
        margin={"r": 80, "t": 20, "l": 20, "b": 20},
        paper_bgcolor='white',
    )
    
    return fig


layout = html.Div([
    html.H2(
        "Géolocalisation des infractions",
        style={
            "textAlign": "center",
            "marginBottom": "0.5rem",
            "marginTop": "0",
            "fontWeight": "600",
            "fontSize": "2rem"
        }
    ),
    html.H3(
        "Répartition géographique des infractions par département",
        style={
            "textAlign": "center",
            "color": "#444",
            "fontSize": "1.3rem",
            "marginBottom": "1.5rem",
            "fontWeight": "500",
            "letterSpacing": "0.3px"
        }
    ),
    dcc.Graph(
        id="carte-departements",
        figure=creer_carte(),
        style={"height": "82vh", "width": "100%"},
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'scrollZoom': False,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
        }
    ),
], style={"padding": "0.5rem 1rem", "maxWidth": "100%", "margin": "0 auto"})