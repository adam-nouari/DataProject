"""
Tests unitaires pour le module clean_data.
"""
import unittest
import pandas as pd
from pathlib import Path
import tempfile
import shutil
from src.utils.clean_data import nettoyer_fichier


class TestCleanData(unittest.TestCase):
    """Tests du nettoyage des données."""
    
    def setUp(self):
        """Préparation avant chaque test."""
        self.rep_temp = tempfile.mkdtemp()
        self.chemin_entree = Path(self.rep_temp) / "test_input.csv"
        self.chemin_sortie = Path(self.rep_temp) / "test_output.csv"
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        shutil.rmtree(self.rep_temp)
    
    def test_renommage_colonnes(self):
        """Vérifie que les colonnes sont correctement renommées."""
        # Données test
        df_test = pd.DataFrame({
            "date": ["2023-01-01 10:00:00"],
            "position": ["45.0 2.0"],
            "mesure": [95],
            "limite": [90]
        })
        df_test.to_csv(self.chemin_entree, index=False, sep=";")
        
        # Exécution
        nettoyer_fichier(self.chemin_entree, self.chemin_sortie)
        
        # Vérification
        df_result = pd.read_csv(self.chemin_sortie, sep=";")
        self.assertIn("vitesse_mesuree", df_result.columns)
        self.assertIn("limitation", df_result.columns)
        self.assertNotIn("mesure", df_result.columns)
        self.assertNotIn("limite", df_result.columns)
    
    def test_suppression_valeurs_manquantes(self):
        """Vérifie la suppression des lignes avec NaN."""
        df_test = pd.DataFrame({
            "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "position": ["45.0 2.0", None, "46.0 3.0"],
            "mesure": [95, 100, None],
            "limite": [90, 90, 90]
        })
        df_test.to_csv(self.chemin_entree, index=False, sep=";")
        
        nettoyer_fichier(self.chemin_entree, self.chemin_sortie)
        
        df_result = pd.read_csv(self.chemin_sortie, sep=";")
        self.assertEqual(len(df_result), 1)
    
    def test_conversion_numerique(self):
        """Vérifie la conversion en types numériques."""
        df_test = pd.DataFrame({
            "date": ["2023-01-01"],
            "position": ["45.0 2.0"],
            "mesure": ["95"],
            "limite": ["90"]
        })
        df_test.to_csv(self.chemin_entree, index=False, sep=";")
        
        nettoyer_fichier(self.chemin_entree, self.chemin_sortie)
        
        df_result = pd.read_csv(self.chemin_sortie, sep=";")
        self.assertTrue(pd.api.types.is_numeric_dtype(df_result["vitesse_mesuree"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(df_result["limitation"]))


if __name__ == '__main__':
    unittest.main()