"""
Tests unitaires pour le module load_to_sqlite.
"""
import unittest
import pandas as pd
import sqlite3
from pathlib import Path
import tempfile
import os
from src.utils.load_to_sqlite import verifier_colonne_existe, localiser_paris


class TestLoadToSQLite(unittest.TestCase):
    """Tests du chargement vers SQLite."""
    
    def setUp(self):
        """Préparation avant chaque test."""
        fd, chemin = tempfile.mkstemp(suffix=".db")
        os.close(fd)  # Ferme le descripteur de fichier
        self.chemin_db = Path(chemin)
        self.conn = sqlite3.connect(self.chemin_db)
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        try:
            self.conn.close()
            # Petite pause pour Windows
            import time
            time.sleep(0.1)
            if self.chemin_db.exists():
                self.chemin_db.unlink()
        except Exception:
            pass  # Ignore les erreurs de nettoyage
    
    def test_verifier_colonne_existe_true(self):
        """Vérifie la détection d'une colonne existante."""
        self.conn.execute("CREATE TABLE test (id INTEGER, nom TEXT)")
        self.conn.commit()
        self.assertTrue(verifier_colonne_existe(self.conn, "test", "nom"))
    
    def test_verifier_colonne_existe_false(self):
        """Vérifie la détection d'une colonne inexistante."""
        self.conn.execute("CREATE TABLE test (id INTEGER, nom TEXT)")
        self.conn.commit()
        self.assertFalse(verifier_colonne_existe(self.conn, "test", "prenom"))
    
    def test_localiser_paris(self):
        """Vérifie la localisation en fuseau Europe/Paris."""
        series_naive = pd.Series(["2023-06-15 12:00:00"])
        series_tz = localiser_paris(series_naive)
        
        self.assertIsNotNone(series_tz.dt.tz)
        self.assertEqual(str(series_tz.dt.tz), "Europe/Paris")
    
    def test_localiser_paris_gestion_erreurs(self):
        """Vérifie la gestion des dates invalides."""
        series_invalide = pd.Series(["invalide", "2023-06-15 12:00:00"])
        series_tz = localiser_paris(series_invalide)
        
        self.assertEqual(len(series_tz), 2)
        self.assertTrue(pd.isna(series_tz.iloc[0]))


if __name__ == '__main__':
    unittest.main()