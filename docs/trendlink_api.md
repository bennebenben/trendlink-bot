# Trendlink API Integration

Dieses Dokument beschreibt, wie die Trendlink API mit dem Chatbot integriert ist und wie Sie die Integration an Ihre Bedürfnisse anpassen können.

## Überblick

Die Trendlink API wird verwendet, um aktuelle Markttrends und Daten abzurufen, die dann vom Chatbot verwendet werden, um kontextbezogene und datengestützte Antworten zu liefern. Die Integration erfolgt in zwei Hauptschritten:

1. Abrufen von Daten aus der Trendlink API
2. Formatieren der Daten für die Verwendung im Chatbot

## Konfiguration

Die Konfiguration der Trendlink API erfolgt über Umgebungsvariablen in der `.env`-Datei:

```
TRENDLINK_API_URL=your_trendlink_api_url_here
TRENDLINK_API_KEY=your_trendlink_api_key_here
```

## Hauptfunktionen

### 1. `fetch_trendlink_data(query_params=None)`

Diese Funktion ist verantwortlich für den Abruf von Daten aus der Trendlink API. Sie sendet eine GET-Anfrage an die API und gibt die JSON-Antwort zurück.

```python
def fetch_trendlink_data(query_params=None):
    headers = {
        "Authorization": f"Bearer {TRENDLINK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            TRENDLINK_API_URL,
            headers=headers,
            params=query_params
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching data from Trendlink API: {e}")
        return {"error": str(e)}
```

#### Parameter anpassen

Abhängig von der Struktur Ihrer Trendlink API können Sie die `query_params` anpassen. Hier einige Beispiele:

```python
# Beispiel: Filtern nach Kategorien
query_params = {
    "category": "technology",
    "limit": 10
}

# Beispiel: Filtern nach Zeitraum
query_params = {
    "from_date": "2023-01-01",
    "to_date": "2023-12-31"
}
```

### 2. `format_trendlink_data_for_chat(data)`

Diese Funktion formatiert die von der API abgerufenen Daten in ein für den Chatbot besser verständliches Format.

```python
def format_trendlink_data_for_chat(data):
    if "error" in data:
        return f"Error retrieving Trendlink data: {data['error']}"
    
    try:
        # Adapt this to match the actual structure of the Trendlink API response
        formatted_data = "Trendlink Data Summary:\n"
        
        # Example formatting - adjust according to actual Trendlink API structure
        if "trends" in data:
            formatted_data += "\nCurrent Trends:\n"
            for trend in data["trends"][:5]:  # Limit to top 5 trends
                formatted_data += f"- {trend.get('name')}: {trend.get('score')} popularity score\n"
        
        if "insights" in data:
            formatted_data += "\nKey Insights:\n"
            for insight in data["insights"][:3]:  # Limit to top 3 insights
                formatted_data += f"- {insight.get('description')}\n"
                
        return formatted_data
    except Exception as e:
        app.logger.error(f"Error formatting Trendlink data: {e}")
        return f"Error formatting Trendlink data: {str(e)}"
```

#### Anpassen an Ihre API-Struktur

Sie müssen diese Funktion an die tatsächliche Struktur Ihrer Trendlink API anpassen. Identifizieren Sie die wichtigsten Datenfelder und formatieren Sie sie in einer für den Endbenutzer leicht verständlichen Weise.

## Integration mit dem Chat-Endpunkt

In der `chat`-Funktion wird entschieden, ob Trendlink-Daten abgerufen werden sollen, basierend auf dem Inhalt der Benutzeranfrage:

```python
# Determine if we need to fetch Trendlink data based on the user message
fetch_trendlink = any(keyword in user_message.lower() for keyword in 
                     ["trend", "data", "statistics", "market", "information"])

trendlink_context = ""
if fetch_trendlink:
    # You can customize query parameters based on user message
    trendlink_data = fetch_trendlink_data()
    trendlink_context = format_trendlink_data_for_chat(trendlink_data)
```

### Anpassen der Schlüsselwörter

Sie können die Liste der Schlüsselwörter anpassen, die bestimmen, wann Trendlink-Daten abgerufen werden sollen:

```python
# Beispiel für angepasste Schlüsselwörter
fetch_trendlink = any(keyword in user_message.lower() for keyword in 
                     ["trend", "markt", "statistik", "daten", "analyse", 
                      "prognose", "entwicklung", "branche", "sektor"])
```

### Anpassen der Abfrageparameter basierend auf der Benutzeranfrage

Sie können auch die Abfrageparameter basierend auf dem Inhalt der Benutzeranfrage anpassen:

```python
# Beispiel für kontextbezogene Abfrageparameter
query_params = {}

if "technologie" in user_message.lower() or "tech" in user_message.lower():
    query_params["category"] = "technology"
elif "finanzen" in user_message.lower():
    query_params["category"] = "finance"
elif "gesundheit" in user_message.lower():
    query_params["category"] = "healthcare"

# Zeitbezogene Parameter extrahieren
if "letzte woche" in user_message.lower():
    # Berechnen des Datums für letzte Woche
    from datetime import datetime, timedelta
    today = datetime.now()
    last_week = today - timedelta(days=7)
    query_params["from_date"] = last_week.strftime("%Y-%m-%d")
    query_params["to_date"] = today.strftime("%Y-%m-%d")

trendlink_data = fetch_trendlink_data(query_params)
```

## Fortgeschrittene Konzepte

### Caching von API-Antworten

Um die Anzahl der API-Aufrufe zu reduzieren, könnten Sie ein Caching-System implementieren:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_fetch_trendlink_data(query_params_str):
    # Konvertieren des String zurück in ein Dictionary
    import json
    query_params = json.loads(query_params_str)
    return fetch_trendlink_data(query_params)

# Verwendung:
import json
query_params = {"category": "technology"}
# Cache-kompatible String-Repräsentation erstellen
query_params_str = json.dumps(query_params, sort_keys=True)
data = cached_fetch_trendlink_data(query_params_str)
```

### Verarbeiten komplexer Antworten

Wenn Ihre Trendlink API komplexe Antworten liefert, können Sie erwägen, eine detailliertere Analyse durchzuführen:

```python
def analyze_trendlink_data(data):
    """
    Führt eine detaillierte Analyse der Trendlink-Daten durch.
    """
    # Implementieren Sie hier eine erweiterte Analyse
    # Beispiel: Identifizieren von Ausreißern, Berechnen von Statistiken, etc.
    pass
```

## Debugging

Wenn Sie Probleme mit der Trendlink API-Integration haben, können Sie zusätzliches Logging hinzufügen:

```python
import logging

# Logger konfigurieren
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def fetch_trendlink_data(query_params=None):
    logger.debug(f"Fetching Trendlink data with params: {query_params}")
    # Restlicher Code...
    logger.debug(f"Received response: {response.status_code}")
    return response.json()
```

## Fehlerbehandlung

Verbessern Sie die Fehlerbehandlung, um robuster mit API-Fehlern umzugehen:

```python
def fetch_trendlink_data(query_params=None, max_retries=3):
    """
    Fetch data from Trendlink API with retry logic
    """
    headers = {
        "Authorization": f"Bearer {TRENDLINK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                TRENDLINK_API_URL,
                headers=headers,
                params=query_params,
                timeout=10  # Add timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Error fetching data (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:  # Last attempt
                return {"error": str(e)}
            time.sleep(1)  # Wait before retry
```

## Zusammenfassung

Die Trendlink API-Integration ermöglicht es dem Chatbot, datengestützte Antworten zu liefern. Durch Anpassung der API-Aufrufe, Formatierung und Integration können Sie eine maßgeschneiderte Lösung für Ihre spezifischen Anforderungen erstellen. 