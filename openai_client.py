#!/usr/bin/env python3
"""
OpenAI Client Module

Dieses Modul stellt Funktionen zum Interagieren mit der OpenAI API zur Verfügung.
Es ermöglicht eine einfache Integration von GPT-4 und anderen OpenAI-Modellen in Anwendungen.
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
        str: Die Textantwort des Modells
        
    Raises:
        Exception: Bei Fehlern in der API-Kommunikation oder Datenverarbeitung
    """
    # API-Key aus Umgebungsvariable holen
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        error_msg = "OPENAI_API_KEY ist nicht in den Umgebungsvariablen definiert"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        # OpenAI Client initialisieren
        client = OpenAI(api_key=api_key)
        
        # Nachrichten formatieren
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # API-Anfrage senden
        logger.info("OpenAI API-Anfrage wird gesendet...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
        
        # Antwort extrahieren
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        else:
            error_msg = "Keine Antwort von OpenAI erhalten"
            logger.error(error_msg)
            return f"Fehler: {error_msg}"
        
    except Exception as e:
        error_msg = f"Fehler bei der Kommunikation mit OpenAI: {str(e)}"
        logger.error(error_msg)
        return f"Fehler: {error_msg}"

if __name__ == "__main__":
    """
    Wenn das Skript direkt ausgeführt wird, einen Beispielaufruf durchführen.
    """
    try:
        system_prompt = "Du bist ein hilfreicher Assistent."
        user_input = "Erkläre mir den Unterschied zwischen Python und JavaScript."
        
        response = get_gpt_response(user_input, system_prompt)
        print(f"Antwort von GPT-4:\n{response}")
    except Exception as e:
        print(f"Fehler: {e}")
        print("Bitte stellen Sie sicher, dass die Umgebungsvariable OPENAI_API_KEY korrekt gesetzt ist.") 