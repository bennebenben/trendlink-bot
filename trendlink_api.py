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
import re

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
    
    # Abfrageparameter definieren - Token als eigener Parameter
    params = {
        "token": api_token,
        "limit": limit,
        "sort": "date_desc"  # Neueste zuerst
    }
    
    # Standard-Headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        # URL mit Parametern für Debugging ausgeben
        debug_url = f"{api_url}?token={api_token}&limit={limit}&sort=date_desc"
        logger.info(f"Trendlink API-Anfrage wird vorbereitet: {debug_url}")
        
        # API-Anfrage senden - wichtig: params wird separat übergeben, nicht in der URL
        logger.info(f"Sende Anfrage mit Parametern: {params}")
        response = requests.get(
            url=api_url,
            headers=headers,
            params=params,
            timeout=10
        )
        
        # Tatsächlich gesendete URL im Log anzeigen
        logger.info(f"Tatsächlich gesendete URL: {response.url}")
        logger.info(f"Request-Headers: {response.request.headers}")
        
        # Fehlerbehandlung
        response.raise_for_status()
        
        # Statuscode und Antwortgröße protokollieren
        logger.info(f"Antwort-Status: {response.status_code}, Antwortgröße: {len(response.content)} Bytes")
        
        # Prüfen, ob Antwort vorhanden
        if not response.content:
            logger.warning("Leere Antwort von der API erhalten")
            return "Keine Daten von der API erhalten"
        
        # Antwort-Debug für sehr niedrige Log-Level
        logger.debug(f"Antwort-Inhalt: {response.text[:500]}...")
        
        # JSON-Antwort parsen
        trend_data = response.json()
        
        # Kurze Zusammenfassung der Daten für Debug-Zwecke
        if isinstance(trend_data, dict) and "trends" in trend_data:
            trend_count = len(trend_data["trends"])
            logger.info(f"Trends gefunden: {trend_count}")
        else:
            logger.warning(f"Unerwartetes Antwortformat: {type(trend_data)}")
            logger.warning(f"Antwort-Inhalt: {trend_data}")
        
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

def get_trend_instruments(trend_name, nice_top=5):
    """
    Sucht nach einem Trend mit dem angegebenen Namen und ruft die wichtigsten Instrumente ab.
    
    Args:
        trend_name (str): Name des Trends oder Suchbegriff (z.B. "Elektroautos")
        nice_top (int): Anzahl der Top-Instrumente, die abgerufen werden sollen
        
    Returns:
        str: Formatierter String mit den Trend-Informationen und Top-Instrumenten
        
    Raises:
        Exception: Bei Fehlern in der API-Kommunikation oder Datenverarbeitung
    """
    # API-Endpunkt für Trends
    api_url = "https://api-preview.trendlink.com/v2/trends"
    
    # API-Token aus Umgebungsvariable holen
    api_token = os.getenv("TRENDLINK_API_TOKEN")
    
    if not api_token:
        error_msg = "TRENDLINK_API_TOKEN ist nicht in den Umgebungsvariablen definiert"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Abfrageparameter definieren - Token als eigener Parameter
    params = {
        "token": api_token,
        "nice5": "true",       # Top 5 Instrumente abrufen
        "lang": "de"           # Deutsche Sprache
    }
    
    # Standard-Headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        # URL mit Parametern für Debugging ausgeben
        debug_url = f"{api_url}?token={api_token}&nice5=true&lang=de"
        logger.info(f"Trendlink API-Anfrage wird vorbereitet: {debug_url}")
        
        # API-Anfrage senden - wichtig: params wird separat übergeben, nicht in der URL
        logger.info(f"Sende Anfrage mit Parametern: {params}")
        response = requests.get(
            url=api_url,
            headers=headers,
            params=params,
            timeout=10
        )
        
        # Tatsächlich gesendete URL im Log anzeigen
        logger.info(f"Tatsächlich gesendete URL: {response.url}")
        logger.info(f"Request-Headers: {response.request.headers}")
        
        # Fehlerbehandlung
        response.raise_for_status()
        
        # Statuscode und Antwortgröße protokollieren
        logger.info(f"Antwort-Status: {response.status_code}, Antwortgröße: {len(response.content)} Bytes")
        
        # Prüfen, ob Antwort vorhanden
        if not response.content:
            logger.warning("Leere Antwort von der API erhalten")
            return f"Keine Daten zum Thema '{trend_name}' von der API erhalten"
        
        # Antwort-Debug für sehr niedrige Log-Level
        logger.debug(f"Antwort-Inhalt: {response.text[:500]}...")
        
        # JSON-Antwort parsen
        trends_data = response.json()
        
        # Kurze Zusammenfassung der Daten für Debug-Zwecke
        if isinstance(trends_data, list):
            trend_count = len(trends_data)
            logger.info(f"Trends gefunden: {trend_count}")
        else:
            logger.warning(f"Unerwartetes Antwortformat: {type(trends_data)}")
            logger.warning(f"Antwort-Inhalt: {trends_data}")
        
        # Suche nach dem angegebenen Trend
        target_trend = None
        search_term_lower = trend_name.lower()
        
        # Regulärer Ausdruck für flexiblere Suche (ignoriert Pluralformen, etc.)
        search_pattern = re.compile(r'\b' + re.escape(search_term_lower) + r'[a-zäöüß]*\b')
        
        for trend in trends_data:
            # Prüfe Namen und Synonyme
            if search_term_lower in trend.get('name', '').lower():
                target_trend = trend
                break
            
            # Prüfe Beschreibung
            if 'description' in trend and search_pattern.search(trend.get('description', '').lower()):
                target_trend = trend
                break
                
            # Prüfe Synonyme
            for synonym in trend.get('synonyms', []):
                if search_pattern.search(synonym.lower()):
                    target_trend = trend
                    break
            
            if target_trend:
                break
        
        if not target_trend:
            return f"Leider wurde kein Trend zum Thema '{trend_name}' gefunden."
        
        # Formatiere den gefundenen Trend und seine Instrumente
        return format_trend_with_instruments(target_trend)
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Fehler bei der Trendlink API-Anfrage: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    except (ValueError, KeyError) as e:
        error_msg = f"Fehler beim Verarbeiten der Trendlink-Daten: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

def format_trend_with_instruments(trend):
    """
    Formatiert einen einzelnen Trend mit seinen Instrumenten als lesbaren String.
    
    Args:
        trend (dict): Trend-Daten aus der Trendlink API
        
    Returns:
        str: Formatierter String mit den Trend- und Instrument-Informationen
    """
    name = trend.get('name', 'Unbekannter Trend')
    description = trend.get('description', 'Keine Beschreibung verfügbar')
    
    # Formatiere die Ausgabe
    formatted_output = f"=== TREND: {name} ===\n\n"
    formatted_output += f"Beschreibung: {description}\n\n"
    
    # Top-Instrumente formatieren
    formatted_output += "=== TOP INSTRUMENTE IM TREND ===\n"
    
    instruments = trend.get('instruments', [])
    if not instruments:
        formatted_output += "Keine Instrumente verfügbar für diesen Trend.\n"
    else:
        for i, instrument in enumerate(instruments, 1):
            isin = instrument.get('isin', 'Unbekannte ISIN')
            weighting = instrument.get('weighting', 'normal')
            is_nice = instrument.get('nice', False)
            
            # Speichere den Namen des Instruments (müsste in einer realen Anwendung aus 
            # einer anderen API-Anfrage kommen oder aus einer lokalen Datenbank)
            instrument_name = f"Instrument mit ISIN {isin}"
            
            # Markiere Top-Instrumente
            nice_marker = "★ " if is_nice else ""
            
            formatted_output += f"{i}. {nice_marker}{instrument_name}\n"
            formatted_output += f"   ISIN: {isin}\n"
            formatted_output += f"   Gewichtung: {weighting}\n"
            
            if i < len(instruments):
                formatted_output += "\n"
    
    return formatted_output

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

# Überprüfen Sie den API-Token und führen Sie einen Test-Request durch
def validate_api_token():
    """
    Überprüft, ob der API-Token korrekt konfiguriert ist und führt eine Test-Anfrage durch.
    
    Returns:
        str: Validierungsmeldung mit Testergebnis
    """
    api_token = os.getenv("TRENDLINK_API_TOKEN")
    
    if not api_token:
        return "FEHLER: TRENDLINK_API_TOKEN ist nicht in den Umgebungsvariablen definiert"
    
    # Test-URL für kuratierte Trends
    api_url = "https://api-preview.trendlink.com/v2/trends/curated"
    params = {"token": api_token, "limit": 1}
    
    try:
        logger.info(f"Führe Test-Anfrage durch: {api_url} mit token={api_token}")
        response = requests.get(url=api_url, params=params, timeout=5)
        
        logger.info(f"Test-Anfrage URL: {response.url}")
        logger.info(f"Test-Anfrage Status: {response.status_code}")
        
        if response.status_code == 200:
            return f"API-Token erfolgreich validiert. Statuscode: 200 OK"
        else:
            return f"API-Token-Test fehlgeschlagen. Statuscode: {response.status_code}"
    
    except Exception as e:
        return f"API-Token-Test fehlgeschlagen mit Fehler: {str(e)}"

if __name__ == "__main__":
    """
    Wenn das Skript direkt ausgeführt wird, die kuratierten Trends abrufen und ausgeben.
    """
    try:
        # Validiere den API-Token und zeige eine Test-URL an
        validation_message = validate_api_token()
        print(validation_message)
        print("\n" + "-" * 50 + "\n")
        
        # Versuche, Trends abzurufen
        print("Versuche, kuratierte Trends abzurufen...")
        trends = get_curated_trends()
        print(trends)
        
        # Beispiel: Suche nach einem spezifischen Trend
        print("\n" + "-" * 50 + "\n")
        print("Versuche, Informationen zum Trend 'Elektroauto' abzurufen...")
        elektroauto_trend = get_trend_instruments("Elektroauto")
        print("\n\n" + elektroauto_trend)
    except Exception as e:
        print(f"Fehler: {e}")
        print("Bitte stellen Sie sicher, dass die Umgebungsvariable TRENDLINK_API_TOKEN korrekt gesetzt ist.") 