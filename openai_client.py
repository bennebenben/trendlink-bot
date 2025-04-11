#!/usr/bin/env python3
"""
OpenAI Client Module

Dieses Modul stellt Funktionen zum Interagieren mit der OpenAI API zur Verfügung.
Es ermöglicht eine einfache Integration von GPT-4 in Anwendungen.
Kompatibel mit OpenAI SDK 1.12.0.
"""

import os
import logging
import httpx
from openai import OpenAI

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_gpt_response(user_input, system_prompt):
    """
    Sendet eine Anfrage an die OpenAI API und liefert die Antwort des GPT-4-Modells zurück.
    
    Args:
        user_input (str): Die Benutzereingabe, die an das Modell gesendet werden soll
        system_prompt (str): Der Systemkontext, der dem Modell die Rolle und Verhaltensweise vorgibt
        
    Returns:
        str: Die Textantwort des Modells oder eine Fehlermeldung
    """
    try:
        # API-Key aus Umgebungsvariable holen
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            error_message = "OpenAI API-Schlüssel nicht gefunden. Bitte überprüfen Sie Ihre Umgebungsvariablen."
            logger.error(error_message)
            return error_message
        
        # OpenAI Client mit minimaler Konfiguration initialisieren
        client = OpenAI(api_key=api_key)
        
        # Nachrichten formatieren
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # API-Anfrage senden
        logger.info("Sende Anfrage an OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
        
        # Antwort extrahieren und zurückgeben
        return response.choices[0].message.content
        
    except Exception as e:
        # Fehlerbehandlung mit detaillierter Diagnose
        error_message = f"Fehler bei der Kommunikation mit OpenAI: {str(e)}"
        logger.error(error_message)
        
        # Bei Proxy-Fehlern einen spezifischen Hinweis geben und alternative Methode versuchen
        if "proxies" in str(e):
            logger.info("Proxy-Fehler erkannt. Versuche alternative Methode...")
            try:
                # Direkter Aufruf ohne OpenAI-Client als Fallback
                # Diese Methode verwendet keine Proxies oder andere Systemkonfigurationen
                return fallback_gpt_request(api_key, messages)
            except Exception as fallback_error:
                logger.error(f"Auch alternativer Ansatz fehlgeschlagen: {fallback_error}")
                error_message += "\n\nAlternativer Ansatz wurde ebenfalls versucht, war aber auch nicht erfolgreich."
        
        return error_message

def fallback_gpt_request(api_key, messages):
    """
    Fallback-Methode, die direkt mit der OpenAI API kommuniziert, wenn der reguläre Client fehlschlägt.
    Diese Methode vermeidet Proxy-Probleme, indem sie einen eigenen HTTP-Client verwendet.
    
    Args:
        api_key (str): Der OpenAI API-Schlüssel
        messages (list): Liste von Nachrichten für die API
        
    Returns:
        str: Die Textantwort des Modells
    """
    import json
    
    # HTTP-Client ohne Proxy-Einstellungen erstellen
    with httpx.Client(proxies=None, timeout=30.0) as client:
        # Direkten API-Aufruf durchführen
        response = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 800
            }
        )
        
        # Fehler bei HTTP-Status überprüfen
        response.raise_for_status()
        
        # JSON-Antwort parsen
        result = response.json()
        
        # Inhalt extrahieren
        if "choices" in result and len(result["choices"]) > 0:
            if "message" in result["choices"][0] and "content" in result["choices"][0]["message"]:
                return result["choices"][0]["message"]["content"]
        
        # Fehler, wenn keine gültige Antwort verfügbar ist
        raise ValueError("Unerwartetes Antwortformat von der OpenAI API")

if __name__ == "__main__":
    """
    Wenn das Skript direkt ausgeführt wird, einen Beispielaufruf durchführen.
    """
    system_prompt = "Du bist ein hilfreicher Assistent."
    user_input = "Erkläre mir den Unterschied zwischen Python und JavaScript."
    
    response = get_gpt_response(user_input, system_prompt)
    print(f"Antwort von GPT-4:\n{response}") 