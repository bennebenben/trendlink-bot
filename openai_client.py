#!/usr/bin/env python3
"""
OpenAI Client Module

Dieses Modul stellt Funktionen zum Interagieren mit der OpenAI API zur Verfügung.
Es ermöglicht eine einfache Integration von GPT-4 in Anwendungen.
Kompatibel mit OpenAI SDK 1.12.0.
"""

import os
import logging
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
        # OpenAI Client initialisieren
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
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
        # Fehlerbehandlung
        error_message = f"Fehler bei der Kommunikation mit OpenAI: {str(e)}"
        logger.error(error_message)
        return error_message

if __name__ == "__main__":
    """
    Wenn das Skript direkt ausgeführt wird, einen Beispielaufruf durchführen.
    """
    system_prompt = "Du bist ein hilfreicher Assistent."
    user_input = "Erkläre mir den Unterschied zwischen Python und JavaScript."
    
    response = get_gpt_response(user_input, system_prompt)
    print(f"Antwort von GPT-4:\n{response}") 