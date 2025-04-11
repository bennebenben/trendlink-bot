#!/usr/bin/env python3
"""
Test-Skript für den /chat-Endpoint mit verschiedenen Anfragen.
Dieses Skript testet beide Szenarien:
1. Anfragen zu Trends (sollten get_curated_trends nutzen)
2. Allgemeine Marktdaten-Anfragen (sollten fetch_trendlink_data nutzen)
"""

import requests
import json
import os
import sys
from dotenv import load_dotenv

# Konfiguration
API_URL = "http://localhost:5000/chat"
HEADERS = {
    "Content-Type": "application/json"
}

# Test-Anfragen
TEST_QUERIES = [
    {
        "type": "trend",
        "message": "Was sind die aktuellen Trends im Technologiebereich?",
        "description": "Direkte Anfrage nach Trends - sollte get_curated_trends verwenden"
    },
    {
        "type": "trend",
        "message": "Zeige mir die neuesten Markttrends",
        "description": "Anfrage nach neuesten Trends - sollte get_curated_trends verwenden"
    },
    {
        "type": "general",
        "message": "Wie sieht die Marktlage für Elektrofahrzeuge aus?",
        "description": "Anfrage nach Marktinformationen ohne explizite Erwähnung von Trends - sollte fetch_trendlink_data verwenden"
    },
    {
        "type": "general",
        "message": "Hast du Daten zur Entwicklung erneuerbarer Energien?",
        "description": "Anfrage nach Daten ohne explizite Erwähnung von Trends - sollte fetch_trendlink_data verwenden"
    },
    {
        "type": "none",
        "message": "Wie ist das Wetter heute?",
        "description": "Allgemeine Anfrage ohne Bezug zu Trends oder Marktdaten - sollte keine Trendlink-Daten verwenden"
    }
]

def send_chat_request(message):
    """Sendet eine Anfrage an den /chat-Endpoint und gibt die Antwort zurück."""
    response = requests.post(
        API_URL,
        headers=HEADERS,
        data=json.dumps({"message": message})
    )
    
    if response.status_code != 200:
        print(f"Fehler: HTTP {response.status_code}")
        print(response.text)
        return None
    
    return response.json()

def main():
    """Hauptfunktion, die die verschiedenen Test-Anfragen ausführt."""
    # Umgebungsvariablen laden
    load_dotenv()
    
    print("=== Test des /chat-Endpoints ===\n")
    
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"Test {i}: {query['description']}")
        print(f"Anfrage: \"{query['message']}\"")
        print("Sende Anfrage...")
        
        result = send_chat_request(query['message'])
        
        if result:
            print("\nAntwort erhalten:")
            print(f"Trendlink-Daten enthalten: {result.get('trendlink_data_included', False)}")
            print(f"Trendlink-Datentyp: {result.get('trendlink_data_type', 'none')}")
            
            expected_type = None
            if query['type'] == 'trend':
                expected_type = 'curated_trends'
            elif query['type'] == 'general':
                expected_type = 'general_data'
            
            if expected_type and result.get('trendlink_data_type') != expected_type:
                print(f"WARNUNG: Erwarteter Datentyp '{expected_type}', aber '{result.get('trendlink_data_type')}' erhalten")
            
            # Gekürzte Antwort anzeigen
            response_text = result.get('response', '')
            if len(response_text) > 100:
                response_text = response_text[:100] + "..."
            print(f"Antwort: {response_text}")
        
        print("\n" + "-" * 50 + "\n")

if __name__ == "__main__":
    main() 