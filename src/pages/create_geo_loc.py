# src/pages/create_geo_loc.py
from pathlib import Path
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
import json

# Chemins
DATA_PATH = Path("data/cleaned/infractions_par_dept_agg.csv")
GEO_PATH = Path("data/geo/departements.geojson")

# Charger les données pré-calculées
if DATA_PATH.exists():
    df_dept = pd.read_csv(DATA_PATH)
    # Convertir code_dept en string pour matcher avec le GeoJSON
    df_dept['code_dept'] = df_dept['code_dept'].astype(str).str.zfill(2)
else:
    df_dept = pd.DataFrame({"code_dept": [], "nb_infractions": []})

# Charger le GeoJSON
if GEO_PATH.exists():
    with open(GEO_PATH, "r", encoding="utf-8") as f:
        geojson_dept = json.load(f)
else:
    geojson_dept = None

# Créer la carte choroplèthe
def create_choropleth():
    if geojson_dept is None or df_dept.empty:
        return go.Figure().add_annotation(
            text="⚠️ Données manquantes. Lance d'abord build_radars_departements.py",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
    
    # Créer un DataFrame complet avec TOUS les départements du GeoJSON
    all_depts = [feature['properties']['code'] for feature in geojson_dept['features']]
    df_complete = pd.DataFrame({'code_dept': all_depts})
    
    # Fusionner avec les données d'infractions (remplir 0 pour les manquants)
    df_complete = df_complete.merge(df_dept, on='code_dept', how='left').fillna(0)
    
    fig = go.Figure(go.Choroplethmapbox(
        geojson=geojson_dept,
        locations=df_complete["code_dept"],
        z=df_complete["nb_infractions"],
        featureidkey="properties.code",
        colorscale=[
            [0, '#fee5d9'],      # Beige très clair
            [0.2, '#fcbba1'],    # Rose clair
            [0.4, '#fc9272'],    # Saumon
            [0.6, '#fb6a4a'],    # Orange-rouge
            [0.8, '#de2d26'],    # Rouge
            [1, '#a50f15']       # Rouge foncé
        ],
        marker_opacity=0.85,
        marker_line_width=1.5,
        marker_line_color='#444444',
        text=df_complete["code_dept"],
        hovertemplate=(
            "<b>Département %{text}</b><br>"
            "Infractions: %{z:,.0f}<br>"
            "<extra></extra>"
        ),
        colorbar=dict(
            title="Infractions",
            x=1.02,
        ),
    ))
    
    fig.update_layout(
        mapbox_style="white-bg",  # Fond blanc sans carte
        mapbox_zoom=4.3,  # Zoom réduit pour voir toute la France + Corse
        mapbox_center={"lat": 46.5, "lon": 2.3},
        margin={"r": 80, "t": 20, "l": 20, "b": 20},
        paper_bgcolor='white',
    )
    
    return fig

# Layout de la page
layout = html.Div([
    html.H2("Géolocalisation des infractions", style={
        "textAlign": "center", 
        "marginBottom": "0.5rem", 
        "marginTop": "0",
        "fontWeight": "600",
        "fontSize": "2rem"
    }),
    html.H3("Répartition géographique des infractions par département en 2023", style={
        "textAlign": "center", 
        "color": "#444", 
        "fontSize": "1.3rem",
        "marginBottom": "1.5rem",
        "fontWeight": "500",
        "letterSpacing": "0.3px"
    }),
    dcc.Graph(
        id="carte-departements",
        figure=create_choropleth(),
        style={"height": "78vh", "width": "100%"},  
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'scrollZoom': False,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
        }
    ),
], style={"padding": "0.5rem 1rem", "maxWidth": "100%", "margin": "0 auto"})