"""
Tests unitaires pour le module build_radars_departements.
"""
import unittest
import pandas as pd
import geopandas as gpd
from src.utils.build_radars_departements import detecter_colonne_code, convertir_en_geodataframe


class TestBuildDepartements(unittest.TestCase):
    """Tests du calcul par département."""
    
    def test_detecter_colonne_code(self):
        """Vérifie la détection de la colonne code."""
        gdf = gpd.GeoDataFrame({"code": ["01", "02"], "nom": ["Ain", "Aisne"]})
        col = detecter_colonne_code(gdf)
        self.assertEqual(col, "code")
    
    def test_detecter_colonne_code_erreur(self):
        """Vérifie l'erreur si aucune colonne valide."""
        gdf = gpd.GeoDataFrame({"autre": ["val1", "val2"]})
        with self.assertRaises(ValueError):
            detecter_colonne_code(gdf)
    
    def test_convertir_en_geodataframe(self):
        """Vérifie la conversion en GeoDataFrame."""
        df = pd.DataFrame({
            "position": ["45.0 2.0", "46.0 3.0"],
            "depassement": [10, 15]
        })
        gdf = convertir_en_geodataframe(df)
        
        self.assertIsInstance(gdf, gpd.GeoDataFrame)
        self.assertEqual(len(gdf), 2)
        self.assertTrue(hasattr(gdf, 'geometry'))


if __name__ == '__main__':
    unittest.main()