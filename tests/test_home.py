"""
Tests unitaires pour l'application Dash.
"""
import unittest
from src.pages.home import create_app


class TestDashApp(unittest.TestCase):
    """Tests de l'application Dash principale."""
    
    def setUp(self):
        """Préparation avant chaque test."""
        self.app = create_app()
        self.app.config.suppress_callback_exceptions = True
    
    def test_app_creation(self):
        """Vérifie que l'application se crée sans erreur."""
        self.assertIsNotNone(self.app)
        self.assertEqual(self.app.title, "Radar Dashboard")
    
    def test_layout_exists(self):
        """Vérifie que le layout est défini."""
        self.assertIsNotNone(self.app.layout)
    
    def test_server_attribute(self):
        """Vérifie que l'attribut server existe."""
        self.assertIsNotNone(self.app.server)


class TestComponents(unittest.TestCase):
    """Tests des composants de l'interface."""
    
    def test_header_import(self):
        """Vérifie l'import du composant header."""
        try:
            from src.components.header import header
            result = header()
            self.assertIsNotNone(result)
        except ImportError:
            self.fail("Impossible d'importer header")
    
    def test_navbar_import(self):
        """Vérifie l'import du composant navbar."""
        try:
            from src.components.navbar import navbar
            result = navbar()
            self.assertIsNotNone(result)
        except ImportError:
            self.fail("Impossible d'importer navbar")
    
    def test_footer_import(self):
        """Vérifie l'import du composant footer."""
        try:
            from src.components.footer import footer
            result = footer()
            self.assertIsNotNone(result)
        except ImportError:
            self.fail("Impossible d'importer footer")


if __name__ == '__main__':
    unittest.main()