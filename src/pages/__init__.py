"""
Package des pages du dashboard.
Expose les layouts et fonctions nécessaires :
- Page dashboard
- Page géolocalisation
- Application principale
"""

from .home import create_app
from .simple_page import layout as simple_layout
from .simple_page import register_callbacks as simple_callbacks
from .create_geo_loc import layout as geo_layout
from .create_geo_loc import creer_carte as create_choropleth

__all__ = [
    "create_app",
    "simple_layout",
    "simple_callbacks",
    "geo_layout",
    "create_choropleth",
]
