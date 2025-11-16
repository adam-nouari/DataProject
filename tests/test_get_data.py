"""
Tests unitaires pour le module get_data.
"""
import unittest
from src.utils.get_data import URL_BASE, RESSOURCES


class TestGetData(unittest.TestCase):
    """Tests du module de téléchargement."""
    
    def test_ressources_non_vides(self):
        """Vérifie que les ressources sont définies."""
        self.assertGreater(len(RESSOURCES), 0)
    
    def test_url_base_valide(self):
        """Vérifie que l'URL de base est correcte."""
        self.assertIn("data.gouv.fr", URL_BASE)
        self.assertTrue(URL_BASE.startswith("https://"))
    
    def test_ressources_format(self):
        """Vérifie le format des identifiants de ressources."""
        for annee, id_ressource in RESSOURCES.items():
            self.assertIsInstance(annee, str)
            self.assertIsInstance(id_ressource, str)
            self.assertGreater(len(id_ressource), 10)


if __name__ == '__main__':
    unittest.main()