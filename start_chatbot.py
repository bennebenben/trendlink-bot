#!/usr/bin/env python3
"""
Starthilfe-Skript für den Trendlink AI Chatbot.
Prüft Voraussetzungen und startet dann die Anwendung.
"""

import os
import sys
import subprocess
import platform
import webbrowser
from pathlib import Path
from time import sleep

# Farben für Terminal-Ausgaben
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_color(message, color):
    """Gibt eine Nachricht in Farbe aus."""
    print(f"{color}{message}{Colors.ENDC}")

def check_env_file():
    """Prüft, ob die .env-Datei existiert und die notwendigen Variablen enthält."""
    env_path = Path(".env")
    
    if not env_path.exists():
        print_color("FEHLER: .env-Datei nicht gefunden!", Colors.RED)
        print_color("Bitte stellen Sie sicher, dass die .env-Datei im Projektverzeichnis vorhanden ist.", Colors.YELLOW)
        return False
    
    # Prüfen der notwendigen Variablen
    required_vars = ["OPENAI_API_KEY", "TRENDLINK_API_TOKEN"]
    missing_vars = []
    placeholder_values = []
    
    with open(env_path, "r") as f:
        content = f.read()
        
    for var in required_vars:
        if var not in content:
            missing_vars.append(var)
        elif f"{var}=sk-example" in content or f"{var}=tl_example" in content:
            placeholder_values.append(var)
    
    if missing_vars:
        print_color(f"FEHLER: Folgende Variablen fehlen in der .env-Datei: {', '.join(missing_vars)}", Colors.RED)
        return False
        
    if placeholder_values:
        print_color(f"WARNUNG: Folgende Variablen haben noch Beispielwerte: {', '.join(placeholder_values)}", Colors.YELLOW)
        print_color("Der Chatbot wird möglicherweise nicht korrekt funktionieren.", Colors.YELLOW)
    
    return True

def check_dependencies():
    """Prüft, ob alle Python-Abhängigkeiten installiert sind."""
    try:
        import flask
        import requests
        import openai
        import dotenv
        print_color("✓ Alle notwendigen Python-Pakete sind installiert.", Colors.GREEN)
        return True
    except ImportError as e:
        print_color(f"FEHLER: Python-Paket fehlt: {e}", Colors.RED)
        print_color("Führen Sie 'pip install -r requirements.txt' aus, um alle Abhängigkeiten zu installieren.", Colors.YELLOW)
        return False

def get_available_port(preferred_port=5000):
    """Findet einen freien Port, beginnend mit dem bevorzugten Port."""
    import socket
    
    port = preferred_port
    max_port = preferred_port + 10
    
    while port < max_port:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
        port += 1
    
    return None

def start_flask_app(port):
    """Startet die Flask-Anwendung und öffnet den Browser."""
    print_color(f"\nStarte Trendlink AI Chatbot auf Port {port}...", Colors.BLUE)
    
    # Umgebungsvariablen für den Unterprocess setzen
    env = os.environ.copy()
    env["FLASK_APP"] = "app.py"
    env["FLASK_ENV"] = "development"
    env["PORT"] = str(port)
    
    # Flask-Anwendung im Hintergrund starten
    system = platform.system().lower()
    if system == "windows":
        process = subprocess.Popen(
            ["python", "app.py"],
            env=env,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        process = subprocess.Popen(
            ["python", "app.py"],
            env=env
        )
    
    # Kurz warten, damit die Anwendung starten kann
    print_color("Warte auf Start des Chatbots...", Colors.BLUE)
    sleep(2)
    
    # Browser öffnen
    webbrowser.open(f"http://localhost:{port}")
    
    print_color("\n✓ Trendlink AI Chatbot läuft jetzt!", Colors.GREEN)
    print_color(f"  Öffnen Sie http://localhost:{port} in Ihrem Browser\n", Colors.BLUE)
    print_color("Drücken Sie Strg+C, um den Chatbot zu beenden.", Colors.YELLOW)
    
    try:
        # Prozess aktiv halten, bis der Benutzer abbricht
        process.wait()
    except KeyboardInterrupt:
        print_color("\nBeende Trendlink AI Chatbot...", Colors.YELLOW)
        process.terminate()
        print_color("Auf Wiedersehen!", Colors.GREEN)

def main():
    """Hauptfunktion zur Überprüfung und zum Start des Chatbots."""
    print_color("\n=== Trendlink AI Chatbot Starthilfe ===\n", Colors.BOLD + Colors.BLUE)
    
    # Arbeitsverzeichnis prüfen
    if not os.path.exists("app.py"):
        print_color("FEHLER: app.py nicht gefunden!", Colors.RED)
        print_color("Bitte starten Sie dieses Skript aus dem Hauptverzeichnis des Projekts.", Colors.YELLOW)
        return False
    
    # .env-Datei prüfen
    if not check_env_file():
        return False
    
    # Abhängigkeiten prüfen
    if not check_dependencies():
        return False
    
    # Verfügbaren Port finden
    port = get_available_port()
    if not port:
        print_color("FEHLER: Konnte keinen freien Port finden!", Colors.RED)
        return False
    
    # Anwendung starten
    start_flask_app(port)
    
    return True

if __name__ == "__main__":
    main() 