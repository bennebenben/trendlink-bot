#!/usr/bin/env python3
"""
Test-Skript für die Trendlink AI Chatbot API-Endpunkte.
"""

import unittest
import json
import sys
import os

# Pfad zum übergeordneten Verzeichnis hinzufügen, um das Hauptmodul zu importieren
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class TestChatbotAPI(unittest.TestCase):
    """Test-Suite für die Chatbot-API-Endpunkte."""
    
    def setUp(self):
        """Vorbereitung der Tests."""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_endpoint(self):
        """Test des Health-Check-Endpunkts."""
        response = self.app.get('/health')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
        self.assertTrue('timestamp' in data)
    
    def test_chat_endpoint_empty_message(self):
        """Test des Chat-Endpunkts mit leerer Nachricht."""
        response = self.app.post(
            '/chat',
            data=json.dumps({}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 400)
        self.assertTrue('error' in data)
    
    def test_chat_endpoint_with_message(self):
        """Test des Chat-Endpunkts mit einer Nachricht."""
        # Da wir nicht die tatsächliche OpenAI-API aufrufen möchten,
        # müssen wir den Test hier anpassen oder einen Mock verwenden.
        # Dies ist ein einfacher Test, der nur prüft, ob der Endpunkt erreichbar ist.
        
        # In einer realen Umgebung würden wir die OpenAI und Trendlink API-Aufrufe mocken.
        if os.getenv('OPENAI_API_KEY') and os.getenv('TRENDLINK_API_KEY'):
            response = self.app.post(
                '/chat',
                data=json.dumps({"message": "Hallo, wie geht es dir?"}),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue('response' in data)
        else:
            print("\nÜberspringe test_chat_endpoint_with_message: API-Schlüssel nicht konfiguriert.")
            print("Setzen Sie OPENAI_API_KEY und TRENDLINK_API_KEY in der Umgebung, um diesen Test auszuführen.")

    def test_root_endpoint(self):
        """Test des Root-Endpunkts (HTML-Oberfläche)."""
        response = self.app.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'<!DOCTYPE html>' in response.data)
        self.assertTrue(b'Trendlink AI Chatbot' in response.data)

if __name__ == '__main__':
    unittest.main() 