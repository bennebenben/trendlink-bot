#!/usr/bin/env python3
"""
Testskript für das trendlink_api Modul.
"""

import unittest
import os
import sys
from unittest import mock

# Pfad zum übergeordneten Verzeichnis hinzufügen, um das Hauptmodul zu importieren
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trendlink_api import get_curated_trends, format_trend_data

class TestTrendlinkAPI(unittest.TestCase):
    """Test-Suite für das trendlink_api Modul."""
    
    def setUp(self):
        """Test-Setup"""
        # Beispiel-Antwort der API für die Tests
        self.sample_trend_data = {
            "trends": [
                {
                    "name": "Künstliche Intelligenz im Gesundheitswesen",
                    "score": 95,
                    "category": "Technologie",
                    "date": "2023-05-15T10:30:00Z",
                    "description": "KI wird zunehmend im Gesundheitswesen eingesetzt, um Diagnosen zu verbessern und personalisierte Behandlungen zu ermöglichen.",
                    "sources": [
                        {
                            "name": "HealthTech Journal",
                            "url": "https://healthtech-journal.com/ai-healthcare-trends"
                        }
                    ]
                },
                {
                    "name": "Nachhaltiger E-Commerce",
                    "score": 87,
                    "category": "Wirtschaft",
                    "date": "2023-05-10T08:45:00Z",
                    "description": "Online-Händler setzen verstärkt auf nachhaltige Verpackungen und klimaneutrale Lieferoptionen.",
                    "sources": [
                        {
                            "name": "E-Commerce Today",
                            "url": "https://ecommerce-today.com/sustainable-practices"
                        }
                    ]
                }
            ]
        }
    
    @mock.patch('trendlink_api.requests.get')
    @mock.patch('trendlink_api.os.getenv')
    def test_get_curated_trends(self, mock_getenv, mock_requests_get):
        """Test der get_curated_trends Funktion mit Mock-Daten"""
        # Mock für die Umgebungsvariable
        mock_getenv.return_value = "fake_api_token"
        
        # Mock für die HTTP-Antwort
        mock_response = mock.Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.sample_trend_data
        mock_requests_get.return_value = mock_response
        
        # Funktion aufrufen
        result = get_curated_trends(limit=2)
        
        # API-Aufruf prüfen
        mock_requests_get.assert_called_once()
        args, kwargs = mock_requests_get.call_args
        
        # Prüfen der URL und Parameter
        self.assertEqual(kwargs['url'], "https://api.trendlink.com/v2/trends/curated")
        self.assertEqual(kwargs['params']['limit'], 2)
        self.assertEqual(kwargs['params']['sort'], "date_desc")
        
        # Header prüfen
        self.assertEqual(kwargs['headers']['Authorization'], "Bearer fake_api_token")
        
        # Ergebnis prüfen (sollte ein nicht-leerer String sein)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Überprüfen, ob Trendinformationen im Ergebnis vorhanden sind
        self.assertIn("Künstliche Intelligenz im Gesundheitswesen", result)
        self.assertIn("Nachhaltiger E-Commerce", result)
    
    @mock.patch('trendlink_api.os.getenv')
    def test_get_curated_trends_missing_token(self, mock_getenv):
        """Test der get_curated_trends Funktion ohne API-Token"""
        # Kein Token in den Umgebungsvariablen
        mock_getenv.return_value = None
        
        # Funktion sollte eine ValueError-Exception auslösen
        with self.assertRaises(ValueError):
            get_curated_trends()
    
    def test_format_trend_data(self):
        """Test der format_trend_data Funktion"""
        result = format_trend_data(self.sample_trend_data)
        
        # Prüfen, ob die formatierte Ausgabe die erwarteten Informationen enthält
        self.assertIn("=== AKTUELLE KURATIERTE TRENDS ===", result)
        self.assertIn("1. Künstliche Intelligenz im Gesundheitswesen (Technologie)", result)
        self.assertIn("Relevanz-Score: 95", result)
        self.assertIn("2. Nachhaltiger E-Commerce (Wirtschaft)", result)
        self.assertIn("Relevanz-Score: 87", result)
        
        # Datumsformatierung prüfen
        self.assertIn("Datum: 15.05.2023", result)
        
        # Quellen prüfen
        self.assertIn("Quellen:", result)
        self.assertIn("HealthTech Journal", result)
    
    def test_format_trend_data_empty(self):
        """Test der format_trend_data Funktion mit leeren Daten"""
        result = format_trend_data({})
        self.assertEqual(result, "Keine Trend-Daten verfügbar")
        
        result = format_trend_data({"trends": []})
        self.assertEqual(result, "Keine Trend-Daten verfügbar")

if __name__ == '__main__':
    unittest.main() 