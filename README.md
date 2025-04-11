# Trendlink AI Chatbot

Ein intelligenter Chatbot, der Daten aus der Trendlink API abruft und mit OpenAI verarbeitet, um Nutzern wertvolle Einblicke in Markttrends zu geben.

## Funktionen

- Natürliche Konversationen über eine moderne Chat-Benutzeroberfläche
- Integration mit OpenAI für intelligente Antworten
- Automatische Anreicherung von Antworten mit Daten aus der Trendlink API
- Spezialisierte Abfrage von kuratierten Trends für trendrelevante Fragen
- Einfache Flask-basierte REST-API
- Spezialisierte Funktionen für kuratierte Trends

## Technologiestack

- **Backend**: Python 3.9+, Flask
- **Frontend**: HTML, CSS, JavaScript
- **APIs**: OpenAI API, Trendlink API
- **Konfiguration**: python-dotenv für sichere Umgebungsvariablen

## Installation

### Voraussetzungen

- Python 3.9 oder höher
- OpenAI API-Schlüssel
- Trendlink API-Zugangsdaten (API-Key und API-Token)

### Setup

1. Klonen Sie das Repository:
   ```bash
   git clone https://github.com/yourusername/trendlink-ai-chatbot.git
   cd trendlink-ai-chatbot
   ```

2. Erstellen Sie eine virtuelle Umgebung und aktivieren Sie diese:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Installieren Sie die Abhängigkeiten:
   ```bash
   pip install -r requirements.txt
   ```

4. Konfigurieren Sie die Umgebungsvariablen:
   - Eine `.env`-Datei ist bereits mit Beispielwerten vorbereitet
   - Öffnen Sie diese in einem Texteditor und aktualisieren Sie die Werte mit Ihren eigenen API-Schlüsseln:
     ```bash
     # Beispiel .env
     OPENAI_API_KEY=sk-IhrActualOpenAISchlüsselHier
     TRENDLINK_API_TOKEN=tl_IhrActualTrendlinkTokenHier
     ```
   - **Wichtig**: Verwenden Sie Ihre eigenen API-Schlüssel, da die Beispielwerte nicht funktionieren

## Lokales Starten und Testen

### Einfacher Start mit dem Starthelfer

Am einfachsten starten Sie den Chatbot mit unserem Starthelfer-Skript:

```bash
python start_chatbot.py
```

Dieses Skript:
- Überprüft die Konfiguration und Abhängigkeiten
- Findet einen verfügbaren Port
- Startet den Server
- Öffnet automatisch den Browser mit der Chatbot-Oberfläche

### Manuelle Startoptionen

Alternativ können Sie den Server auch manuell starten:

1. Starten Sie den Chatbot-Server mit einem dieser Befehle:
   ```bash
   # Sicherstellen, dass Sie sich im Hauptverzeichnis des Projekts befinden
   # und die virtuelle Umgebung aktiviert ist

   # Option 1: Mit Python direkt starten
   python app.py

   # Option 2: Mit Flask starten
   flask run --host=0.0.0.0 --port=5000
   ```

2. Öffnen Sie Ihren Browser und navigieren Sie zu:
   ```
   http://localhost:5000
   ```

3. Testen Sie den Chatbot mit Beispielanfragen:
   - *"Was sind die neuesten Trends im Technologiebereich?"*
   - *"Zeige mir aktuelle Marktdaten zu erneuerbaren Energien"*
   - *"Wie entwickelt sich der Markt für KI-Tools?"*

4. Führen Sie das Test-Skript aus, um verschiedene Anfragen automatisch zu testen:
   ```bash
   python examples/test_chat_endpoint.py
   ```

## Fehlerbehebung beim lokalen Start

Falls Fehler auftreten:

1. **API-Schlüssel-Probleme:**
   - Überprüfen Sie, ob Ihre API-Schlüssel in der `.env`-Datei korrekt sind
   - Stellen Sie sicher, dass die `.env`-Datei im Hauptverzeichnis des Projekts liegt

2. **Port-Konflikte:**
   - Falls Port 5000 bereits verwendet wird, ändern Sie den Port in der `.env`-Datei:
     ```
     PORT=5001
     ```
   - Und starten Sie dann mit: `python app.py` oder `flask run --port=5001`
   - Alternativ nutzen Sie `python start_chatbot.py`, das automatisch einen freien Port findet

3. **Log-Ausgaben überprüfen:**
   - Die Anwendung protokolliert Informationen und Fehler in der Konsole
   - Überprüfen Sie diese Ausgaben, um mögliche Fehlerursachen zu identifizieren

## Verwendung

Beginnen Sie, mit dem Chatbot zu chatten! Sie können nach Markttrends fragen oder spezifische Daten abfragen.

## Trendlink API-Integration

Die Anwendung bietet verschiedene Möglichkeiten zur Integration mit der Trendlink API:

### Intelligente Trendlink-Integration im Chat-Endpoint

Der `/chat`-Endpoint analysiert Benutzeranfragen und wählt automatisch die passende Datenquelle:

- **Kuratierte Trends** (via `get_curated_trends()`) für Anfragen zu Trends, neuesten Entwicklungen oder aktuellen Marktbewegungen
- **Allgemeine Marktdaten** (via `fetch_trendlink_data()`) für andere datenbezogene Anfragen

Die Benutzeroberfläche zeigt an, welcher Typ von Trendlink-Daten für die Antwort verwendet wurde, mit speziellen visuellen Indikatoren für kuratierte Trends.

### Allgemeine Integration (app.py)

Die Hauptanwendung verwendet die Funktionen `fetch_trendlink_data` und `format_trendlink_data_for_chat` für eine generische Abfrage der Trendlink API. Diese können an die spezifische Struktur und Endpunkte der Trendlink API angepasst werden.

### Spezialisierte Integration (trendlink_api.py)

Für spezialisierte Abfragen steht das `trendlink_api.py` Modul zur Verfügung:

- `get_curated_trends(limit=5)`: Ruft die 5 neuesten kuratierten Trends vom Endpunkt `/v2/trends/curated` ab und gibt sie als formatierten String zurück.

Beispiel zur Verwendung:

```python
from trendlink_api import get_curated_trends

# Abrufen und Ausgeben der 5 neuesten kuratierten Trends
trends = get_curated_trends(limit=5)
print(trends)
```

Das Modul verwendet die Umgebungsvariable `TRENDLINK_API_TOKEN` für die Authentifizierung. Stellen Sie sicher, dass diese in Ihrer `.env`-Datei definiert ist.

## API-Endpunkte

### GET /
Die Hauptseite mit der Chat-Benutzeroberfläche.

### POST /chat
Der Haupt-Chatendpunkt, der Benutzernachrichten entgegennimmt und intelligente Antworten liefert.

**Request-Beispiel:**
```json
{
  "message": "Welche Trends gibt es aktuell in der KI-Branche?"
}
```

**Response-Beispiel:**
```json
{
  "response": "Aktuell gibt es mehrere wichtige Trends in der KI-Branche...",
  "trendlink_data_included": true,
  "trendlink_data_type": "curated_trends"
}
```

### GET /health
Ein einfacher Health-Check-Endpunkt zur Überwachung des Service-Status.

## Beispielcode

Im Verzeichnis `examples/` finden Sie Beispielskripte zur Verwendung der verschiedenen Funktionen:

- `api_client.py`: Ein Konsolen-Client für die Chatbot-API
- `use_trendlink_api.py`: Beispiel zur Verwendung des `trendlink_api.py` Moduls
- `test_chat_endpoint.py`: Testet den Chat-Endpoint mit verschiedenen Arten von Anfragen

## Tests

Führen Sie die Tests aus, um die Funktionalität zu überprüfen:

```bash
python -m unittest discover -s tests
```

Sie können auch den Chat-Endpoint mit verschiedenen Anfragen testen:

```bash
python examples/test_chat_endpoint.py
```

## Lizenz

MIT

## Kontakt

Bei Fragen oder Problemen kontaktieren Sie bitte [Ihre E-Mail-Adresse]. 