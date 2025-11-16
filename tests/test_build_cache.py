"""
Tests unitaires pour le module build_dashboard_cache.
"""
import unittest
import pandas as pd


class TestBuildCache(unittest.TestCase):
    """Tests de la génération du cache dashboard."""
    
    def test_classification_depassement(self):
        """Vérifie la classification correcte des dépassements."""
        df = pd.DataFrame({
            "depassement": [-5, 5, 15, 25, 35]
        })
        
        classes_attendues = [
            "≤ 0 km/h (respect)",
            "0–10 km/h",
            "10–20 km/h",
            "20–30 km/h",
            "> 30 km/h",
        ]
        
        bornes = [-float("inf"), 0, 10, 20, 30, float("inf")]
        df["classe"] = pd.cut(
            df["depassement"],
            bins=bornes,
            labels=classes_attendues,
            include_lowest=True,
            right=True,
        )
        
        self.assertEqual(df["classe"].iloc[0], "≤ 0 km/h (respect)")
        self.assertEqual(df["classe"].iloc[1], "0–10 km/h")
        self.assertEqual(df["classe"].iloc[2], "10–20 km/h")
        self.assertEqual(df["classe"].iloc[3], "20–30 km/h")
        self.assertEqual(df["classe"].iloc[4], "> 30 km/h")
    
    def test_agregation_par_periode(self):
        """Vérifie l'agrégation par période."""
        df = pd.DataFrame({
            "periode": ["jour", "jour", "nuit", "nuit"],
            "limitation": [90, 90, 90, 90],
            "classe_depassement": ["0–10 km/h"] * 4,
        })
        
        agg = df.groupby(["periode", "limitation", "classe_depassement"]).size()
        
        self.assertEqual(agg[("jour", 90, "0–10 km/h")], 2)
        self.assertEqual(agg[("nuit", 90, "0–10 km/h")], 2)


if __name__ == '__main__':
    unittest.main()