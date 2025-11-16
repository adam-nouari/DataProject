"""
Composants réutilisables du dashboard :
- header : bandeau supérieur
- navbar : barre de navigation
- footer : pied de page

Ce module centralise les imports pour faciliter l'utilisation dans les pages Dash.
"""

from .header import header
from .navbar import navbar
from .footer import footer

__all__ = [
    "header",
    "navbar",
    "footer",
]