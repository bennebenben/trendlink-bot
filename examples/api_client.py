#!/usr/bin/env python3
"""
Ein einfacher API-Client für den Trendlink AI Chatbot.
Dieses Skript demonstriert, wie man mit dem Chatbot über die API interagieren kann.
"""

import requests
import json
import sys
import os

# Konfiguration des API-Clients
API_URL = "http://localhost:5000/chat"
HEADERS = {
    "Content-Type": "application/json"
}

def chat_with_bot(message):
    """
    Sendet eine Nachricht an den Chatbot und gibt die Antwort zurück.
    
    Args:
        message (str): Die Nachricht an den Chatbot
        
    Returns:
        dict: Die JSON-Antwort des Chatbots
    """
    try:
        payload = {
            "message": message
        }
        
        response = requests.post(
            API_URL,
            headers=HEADERS,
            data=json.dumps(payload)
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der API-Anfrage: {e}")
        return None

def interactive_chat():
    """
    Startet eine interaktive Chat-Sitzung mit dem Chatbot in der Konsole.
    """
    print("=== Trendlink AI Chatbot Konsolen-Client ===")
    print("Tippen Sie 'exit' oder 'quit', um zu beenden.")
    print("----------------------------------------------")
    
    while True:
        user_input = input("\nIhre Frage: ")
        
        if user_input.lower() in ["exit", "quit", "beenden"]:
            print("Chat beendet. Auf Wiedersehen!")
            break
        
        print("\nBot antwortet...")
        response = chat_with_bot(user_input)
        
        if response:
            print(f"\n{response['response']}")
            
            if response.get("trendlink_data_included"):
                print("\n[Mit Trendlink-Daten angereichert]")
        else:
            print("\nKeine Antwort vom Server erhalten.")

def main():
    """
    Hauptfunktion des Skripts
    """
    # Prüfen, ob ein Argument übergeben wurde
    if len(sys.argv) > 1:
        # Singleshot-Modus: Eine Frage stellen und beenden
        question = " ".join(sys.argv[1:])
        print(f"Frage: {question}")
        print("Antwort wird abgerufen...")
        
        response = chat_with_bot(question)
        
        if response:
            print(f"\n{response['response']}")
            
            if response.get("trendlink_data_included"):
                print("\n[Mit Trendlink-Daten angereichert]")
        else:
            print("Keine Antwort vom Server erhalten.")
    else:
        # Interaktiver Modus
        interactive_chat()

if __name__ == "__main__":
    main() 