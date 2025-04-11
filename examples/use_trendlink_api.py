#!/usr/bin/env python3
"""
Beispielskript zur Verwendung der trendlink_api.py in der Chatbot-Anwendung.
"""

import os
import sys
from dotenv import load_dotenv

# Pfad zum übergeordneten Verzeichnis hinzufügen, um das Hauptmodul zu importieren
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trendlink_api import get_curated_trends

def main():
    """
    Hauptfunktion zum Testen der Trendlink API-Integration.
    """
    # Umgebungsvariablen aus .env laden
    load_dotenv()
    
    print("Trendlink API Beispiel")
    print("======================\n")
    
    try:
        # Trendlink API aufrufen und Ergebnisse anzeigen
        print("Abrufen der neuesten kuratierten Trends...\n")
        trends = get_curated_trends(limit=5)
        
        print(trends)
        
        print("\nBeispiel für die Integration in den Chatbot:")
        print("-------------------------------------------\n")
        print("# In app.py, Funktion chat(), ergänzen Sie:")
        print("""
if "trends" in user_message.lower() or "trend" in user_message.lower():
    # Kuratierte Trends abrufen
    from trendlink_api import get_curated_trends
    
    try:
        trendlink_context = get_curated_trends(limit=5)
    except Exception as e:
        trendlink_context = f"Fehler beim Abrufen der Trends: {str(e)}"
        
    # Nachrichten für OpenAI vorbereiten
    messages = [
        {"role": "system", "content": "Du bist ein hilfreicher Assistent mit Zugriff auf aktuelle Markttrends."},
        {"role": "system", "content": f"Hier sind die neuesten kuratierten Trends:\\n{trendlink_context}"},
        {"role": "user", "content": user_message}
    ]
        """)
        
    except Exception as e:
        print(f"Fehler: {e}")
        print("\nBitte stellen Sie sicher, dass die Umgebungsvariable TRENDLINK_API_TOKEN korrekt gesetzt ist.")
        print("Kopieren Sie die .env.example zu .env und ergänzen Sie Ihren API-Token.")

if __name__ == "__main__":
    main() 