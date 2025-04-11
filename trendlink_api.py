#!/usr/bin/env python3
"""
Trendlink API Module

Dieses Modul stellt Funktionen zum Abrufen und Formatieren von Trendlink-Daten bereit.
Es ermöglicht die einfache Integration von Trendlink-Daten in andere Anwendungen.
"""

import os
import requests
from datetime import datetime
import logging

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_curated_trends(limit=5):
    """
    Ruft die neuesten kuratierten Trends von der Trendlink API ab.
    
    Args:
        limit (int): Anzahl der abzurufenden Trends (Standard: 5)
        
    Returns:
        str: Formatierter String mit den Trend-Informationen
        
    Raises:
        Exception: Bei Fehlern in der API-Kommunikation oder Datenverarbeitung
    """
    # API-Endpunkt für kuratierte Trends
    api_url = "https://api-preview.trendlink.com/v2/trends/curated"
    
    # API-Token aus Umgebungsvariable holen
    api_token = os.getenv("TRENDLINK_API_TOKEN")
    
    if not api_token:
        error_msg = "TRENDLINK_API_TOKEN ist nicht in den Umgebungsvariablen definiert"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Abfrageparameter mit Token
    params = {
        "limit": limit,
        "sort": "date_desc",  # Neueste zuerst
        "token": api_token    # Token als URL-Parameter statt im Header
    }
    
    # Standard-Headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        # API-Anfrage senden
        logger.info(f"Trendlink API-Anfrage an {api_url} wird gesendet...")
        response = requests.get(
            url=api_url,
            headers=headers,
            params=params,
            timeout=10
        )
        
        # Fehlerbehandlung
        response.raise_for_status()
        
        # JSON-Antwort parsen
        trend_data = response.json()
        
        # Formatieren der Daten
        return format_trend_data(trend_data)
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Fehler bei der Trendlink API-Anfrage: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    except (ValueError, KeyError) as e:
        error_msg = f"Fehler beim Verarbeiten der Trendlink-Daten: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

def format_trend_data(trend_data):
    """
    Formatiert die Trendlink API-Antwort als lesbaren String.
    
    Args:
        trend_data (dict): JSON-Antwort von der Trendlink API
        
    Returns:
        str: Formatierter String mit den Trend-Informationen
    """
    # Prüfen, ob Daten vorhanden sind
    if not trend_data or "trends" not in trend_data or not trend_data["trends"]:
        return "Keine Trend-Daten verfügbar"
    
    trends = trend_data.get("trends", [])
    
    # Limitiere auf Top 5 Trends
    trends = trends[:5]
    
    # Überschrift
    formatted_output = "=== AKTUELLE KURATIERTE TRENDS ===\n\n"
    
    # Jeden Trend formatieren
    for i, trend in enumerate(trends, 1):
        # Basisdaten
        name = trend.get("name", "Unbekannter Trend")
        score = trend.get("score", "N/A")
        category = trend.get("category", "Allgemein")
        
        # Datum formatieren, falls vorhanden
        if "date" in trend and trend["date"]:
            try:
                date_obj = datetime.fromisoformat(trend["date"].replace("Z", "+00:00"))
                date_str = date_obj.strftime("%d.%m.%Y")
            except (ValueError, TypeError):
                date_str = trend.get("date", "Unbekanntes Datum")
        else:
            date_str = "Unbekanntes Datum"
        
        # Beschreibung
        description = trend.get("description", "Keine Beschreibung verfügbar")
        
        # Trend-Eintrag formatieren
        formatted_output += f"{i}. {name} ({category})\n"
        formatted_output += f"   Relevanz-Score: {score}\n"
        formatted_output += f"   Datum: {date_str}\n"
        
        # Beschreibung mit Zeilenumbrüchen für bessere Lesbarkeit
        formatted_output += f"   Beschreibung: {description}\n"
        
        # Quellen, falls vorhanden
        if "sources" in trend and trend["sources"]:
            formatted_output += "   Quellen:\n"
            for source in trend["sources"][:3]:  # Maximal 3 Quellen anzeigen
                source_name = source.get("name", "Unbekannte Quelle")
                source_url = source.get("url", "#")
                formatted_output += f"   - {source_name}: {source_url}\n"
        
        # Trennlinie zwischen Trends
        if i < len(trends):
            formatted_output += "\n" + "-" * 50 + "\n\n"
    
    return formatted_output

if __name__ == "__main__":
    """
    Wenn das Skript direkt ausgeführt wird, die kuratierten Trends abrufen und ausgeben.
    """
    try:
        trends = get_curated_trends()
        print(trends)
    except Exception as e:
        print(f"Fehler: {e}")
        print("Bitte stellen Sie sicher, dass die Umgebungsvariable TRENDLINK_API_TOKEN korrekt gesetzt ist.") 