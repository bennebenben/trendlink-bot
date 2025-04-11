# Deployment auf Render.com

Diese Anleitung erklärt, wie Sie den Trendlink AI Chatbot auf [Render.com](https://render.com) bereitstellen können.

## Voraussetzungen

- Ein Render.com-Konto
- Ein Git-Repository mit dem Trendlink AI Chatbot-Code
- API-Schlüssel für OpenAI und Trendlink

## Deployment-Optionen

Sie haben zwei Möglichkeiten, den Chatbot auf Render.com zu deployen:

### Option 1: Blueprint-Deployment (empfohlen)

Verwenden Sie die `render.yaml`-Datei als Blueprint, um die Anwendung mit allen Konfigurationen automatisch zu deployen.

1. Melden Sie sich bei Render.com an.
2. Klicken Sie auf die Schaltfläche "New" und wählen Sie "Blueprint".
3. Verbinden Sie Ihr GitHub-Repository oder importieren Sie das Repository von einer anderen Quelle.
4. Render wird automatisch die `render.yaml`-Datei erkennen und den Service für Sie konfigurieren.
5. Füllen Sie die erforderlichen Umgebungsvariablen aus (siehe unten).
6. Klicken Sie auf "Apply" und warten Sie, bis das Deployment abgeschlossen ist.

### Option 2: Manuelles Web Service-Deployment

1. Melden Sie sich bei Render.com an.
2. Klicken Sie auf die Schaltfläche "New" und wählen Sie "Web Service".
3. Verbinden Sie Ihr GitHub-Repository oder importieren Sie das Repository von einer anderen Quelle.
4. Füllen Sie die folgenden Felder aus:
   - **Name**: `trendlink-ai-chatbot` (oder ein Name Ihrer Wahl)
   - **Environment**: `Python`
   - **Region**: Wählen Sie die Region aus, die Ihren Benutzern am nächsten ist
   - **Branch**: `main` (oder der Branch, den Sie verwenden möchten)
   - **Build Command**: `pip install -r requirements-deploy.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --log-level info`
   - **Health Check Path**: `/health`
   - **Plan**: Wählen Sie den geeigneten Plan (für Tests kann "Free" verwendet werden)
5. Fügen Sie die erforderlichen Umgebungsvariablen hinzu (siehe unten).
6. Klicken Sie auf "Create Web Service" und warten Sie, bis das Deployment abgeschlossen ist.

## Umgebungsvariablen

Folgende Umgebungsvariablen müssen bei Render.com konfiguriert werden:

| Variable | Beschreibung |
|----------|-------------|
| `OPENAI_API_KEY` | Ihr OpenAI API-Schlüssel |
| `TRENDLINK_API_URL` | Die URL für die Trendlink API |
| `TRENDLINK_API_KEY` | Ihr Trendlink API-Schlüssel |
| `TRENDLINK_API_TOKEN` | Ihr Trendlink API-Token |
| `FLASK_ENV` | Sollte auf `production` gesetzt sein |
| `PORT` | Wird von Render.com automatisch gesetzt; verwenden Sie `$PORT` in Ihrem Code |
| `PYTHON_VERSION` | `3.9` (oder höher, falls benötigt) |

## Nach dem Deployment

1. Nach erfolgreichem Deployment können Sie auf den "Open App"-Button klicken, um die Anwendung zu öffnen.
2. Überprüfen Sie die Logs, um sicherzustellen, dass alles korrekt funktioniert.
3. Testen Sie den `/health`-Endpunkt, um zu prüfen, ob die Anwendung ordnungsgemäß läuft.
4. Testen Sie den Chatbot über die Benutzeroberfläche oder die API-Endpunkte.

## Fehlerbehebung

Falls Probleme beim Deployment auftreten:

1. **Überprüfen Sie die Logs**: In der Render.com-Oberfläche können Sie die Logs einsehen, um Fehler zu identifizieren.
2. **Umgebungsvariablen**: Stellen Sie sicher, dass alle erforderlichen Umgebungsvariablen korrekt gesetzt sind.
3. **Dateizugriff**: Stellen Sie sicher, dass Ihre Anwendung keine lokalen Dateien schreibt, die nicht im Render-Dateisystem erlaubt sind.
4. **Port-Konfiguration**: Stellen Sie sicher, dass Ihre Anwendung den PORT verwendet, den Render.com über die Umgebungsvariable bereitstellt.

## Automatische Deployments

Die `render.yaml`-Konfiguration enthält die Einstellung `autoDeploy: true`, wodurch bei jedem Push in den konfigurierten Branch automatisch ein neues Deployment ausgelöst wird. Dies kann im Render.com-Dashboard deaktiviert werden, wenn Sie manuelle Deployments bevorzugen.

## Ressourcen und Kosten

- Der Free-Plan bei Render.com reicht für einfache Tests aus, hat aber Einschränkungen hinsichtlich Rechenleistung und Verfügbarkeit (die Anwendung "schläft" nach Inaktivität).
- Für produktive Anwendungen sollten Sie einen bezahlten Plan in Betracht ziehen, der kontinuierliche Verfügbarkeit und mehr Ressourcen bietet.
- Beachten Sie, dass OpenAI-API-Aufrufe separat abgerechnet werden und zusätzliche Kosten verursachen können. 