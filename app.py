import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # CORS für Cross-Origin-Anfragen hinzugefügt
from dotenv import load_dotenv
import requests
from datetime import datetime
from dateutil import parser
import logging
import re

# Import the specialized Trendlink API module
from trendlink_api import get_curated_trends, get_trend_instruments
# Import the OpenAI client module
from openai_client import get_gpt_response

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# CORS aktivieren, um Cross-Origin-Anfragen zu erlauben
CORS(app)

# Configure OpenAI API
# Wir benötigen diesen Code nicht mehr, da wir jetzt den get_gpt_response() verwenden,
# der den API-Key selbst aus den Umgebungsvariablen lädt
# openai.api_key = os.getenv("OPENAI_API_KEY")

# Trendlink API configuration
TRENDLINK_API_URL = os.getenv("TRENDLINK_API_URL")
TRENDLINK_API_KEY = os.getenv("TRENDLINK_API_KEY")

# Utility function to fetch data from Trendlink API
def fetch_trendlink_data(query_params=None):
    """
    Fetch data from Trendlink API
    
    Args:
        query_params (dict): Optional query parameters for the API request
        
    Returns:
        dict: JSON response from the API
    """
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

# Helper function to format Trendlink data for the chatbot
def format_trendlink_data_for_chat(data):
    """
    Format Trendlink data for better readability in chat responses
    
    Args:
        data (dict): JSON data from Trendlink API
        
    Returns:
        str: Formatted string of relevant information
    """
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

# Helfer-Funktion zur Erkennung von spezifischen Trendaktien-Anfragen
def extract_trend_request(message):
    """
    Extrahiert Trend-Anfragen aus der Nutzereingabe.
    
    Args:
        message (str): Die Nachricht des Nutzers
        
    Returns:
        tuple: (ist_trend_aktien_anfrage, trendname) oder (False, None) wenn keine solche Anfrage
    """
    # Muster für Anfragen nach Aktien in einem bestimmten Trend
    patterns = [
        r'(?:aktien|wertpapiere|etfs?|fonds|investment|investieren|anlage)\s+(?:zu|für|im|zum|über|in|bereich|sektor|thema|themen|trend)\s+([a-zäöüß\s-]+)',
        r'(?:top|beste|gute|empfehlen\w*|interessante|lohnend\w*|wichtig\w*)\s+(?:\d+\s+)?(?:aktien|wertpapiere|etfs?|fonds|titel|investments?)\s+(?:zu|für|im|zum|über|in|bereich|sektor|thema|themen|trend)\s+([a-zäöüß\s-]+)',
        r'(?:welche|was\s+sind)\s+(?:die|)\s+(?:top|beste|gute|empfehlen\w*|interessante|lohnend\w*|wichtig\w*)\s+(?:\d+\s+)?(?:aktien|wertpapiere|etfs?|fonds|titel|investments?)\s+(?:zu|für|im|zum|über|in|bereich|sektor|thema|themen|trend)\s+([a-zäöüß\s-]+)',
        r'(?:nice|top)\s+(?:\d+)?\s+(?:aktien|wertpapiere|etfs?|fonds|titel|investment|investments?)\s+(?:im|zum|zu|für|über|in|bereich|sektor|thema|themen|trend)\s+([a-zäöüß\s-]+)'
    ]
    
    message_lower = message.lower()
    
    for pattern in patterns:
        matches = re.search(pattern, message_lower)
        if matches:
            trend_name = matches.group(1).strip()
            return True, trend_name
    
    return False, None

# Helfer-Funktion zur Überprüfung, ob eine Anfrage themenrelevant ist
def is_finance_trend_related(message):
    """
    Überprüft, ob die Nachricht sich auf Finanzen, Trends oder Marktthemen bezieht.
    
    Args:
        message (str): Die Nachricht des Nutzers
        
    Returns:
        bool: True, wenn die Nachricht themenrelevant ist, sonst False
    """
    # Liste von Begriffen, die auf eine themenrelevante Anfrage hindeuten
    finance_terms = [
        "aktie", "aktien", "börse", "kurs", "kurse", "markt", "märkte",
        "finanz", "finanzen", "geld", "anlage", "anlegen", "investieren", 
        "investment", "fonds", "etf", "sparplan", "dividende", "rendite",
        "bank", "zins", "zinsen", "inflation", "wirtschaft", "konjunktur",
        "trend", "trends", "trendig", "trendlink", "entwicklung", "wachstum",
        "sektor", "branche", "industrie", "technologie", "rohstoff", "rohstoffe",
        "krypto", "bitcoin", "ethereum", "blockchain", "nft", "token",
        "wertpapier", "wertpapiere", "depot", "portfolio", "diversifikation",
        "gewinn", "verlust", "risiko", "chance", "prognose", "analyse", "bewertung",
        "isin", "wkn", "ticker", "symbol", "chart", "kursverlauf", "performance"
    ]
    
    message_lower = message.lower()
    
    # Prüfen, ob mindestens ein themenrelevanter Begriff in der Nachricht vorkommt
    return any(term in message_lower for term in finance_terms)

# Root endpoint to render the chat interface
@app.route("/", methods=["GET"])
def index():
    """
    Render the chat interface
    """
    return render_template("index.html")

# Chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    """
    Chat endpoint that processes user messages and responds using OpenAI's GPT-4,
    incorporating data from Trendlink when relevant.
    
    This bot ONLY answers finance and trend-related questions, using Trendlink data
    as the primary source for all trend information. Non-relevant questions will be
    politely declined.
    """
    try:
        data = request.json
        
        if not data or "message" not in data:
            return jsonify({"error": "No message provided"}), 400
            
        user_message = data["message"]
        
        # Prüfen, ob die Anfrage themenrelevant ist (Finanzen/Trends)
        if not is_finance_trend_related(user_message):
            # Nicht-themenrelevante Anfrage höflich ablehnen
            return jsonify({
                "response": "Ich bin spezialisiert auf Finanz- und Trend-Themen und kann Ihnen leider keine Informationen zu anderen Bereichen geben. Bitte stellen Sie mir Fragen zu Trends, Aktien, Märkten oder Finanzthemen.",
                "has_trend_data": False,
                "query_type": "off_topic"
            })
        
        # Prüfen, ob es eine Anfrage nach Aktien in einem spezifischen Trend ist
        is_trend_stock_query, trend_name = extract_trend_request(user_message)
        
        # Standard Trend-Keywords für allgemeine Trend-Anfragen
        trend_keywords = ["trend", "trends", "trending", "aktuell", "neu", "neueste", "markt", 
                         "finanzen", "wirtschaft", "entwicklung", "zukunft", "investition"]
        
        # Prüfen, ob es eine allgemeine trend-bezogene Anfrage ist
        is_general_trend_query = any(keyword in user_message.lower() for keyword in trend_keywords) and not is_trend_stock_query
        
        # Strengen System-Prompt definieren, der das Modell auf Trendlink-Daten beschränkt
        system_prompt = (
            "Du bist ein spezialisierter Finanztrend-Bot, der AUSSCHLIESSLICH auf Basis der Trendlink-Datenbank "
            "antwortet. VERWENDE NIEMALS dein allgemeines Wissen bei Trend-bezogenen Fragen, sondern NUR die "
            "bereitgestellten Daten. Bei Fragen zu bestimmten Trends oder Aktien antworte NUR mit den Informationen, "
            "die direkt aus den Trendlink-Daten stammen. Wenn keine relevanten Daten vorhanden sind, teile dies dem "
            "Nutzer mit, anstatt allgemeine Informationen zu geben. "
            "Deine Antworten sollten präzise, faktenbasiert und effizient sein. "
            "Beantworte ausschließlich Fragen zu Finanzen, Märkten und Trends."
        )
        
        trendlink_context = ""
        trendlink_data_type = None
        
        # Bei Anfragen für Aktien zu einem spezifischen Trend
        if is_trend_stock_query and trend_name:
            try:
                logger.info(f"Trend stock query detected for trend: {trend_name}")
                
                # Abrufen der Instrument-Daten für den Trend
                trend_instruments = get_trend_instruments(trend_name)
                trendlink_context = trend_instruments
                trendlink_data_type = "trend_instruments"
                
                # Erweitere den System-Prompt mit den Trend-Aktien-Daten
                system_prompt += f"\n\nHier sind die Top-Aktien im Trend '{trend_name}':\n\n{trend_instruments}"
                system_prompt += "\n\nBasiere deine Antwort AUSSCHLIESSLICH auf diesen Daten. Ergänze KEINE zusätzlichen Informationen aus deinem eigenen Wissen."
                logger.info(f"Successfully incorporated trend instruments data for '{trend_name}'")
            except Exception as e:
                logger.error(f"Error fetching trend instruments: {e}")
                system_prompt += f"\n\nIch habe versucht, Informationen zum Trend '{trend_name}' abzurufen, aber leider sind keine Daten verfügbar. Bitte teile dem Nutzer mit, dass keine Informationen in der Trendlink-Datenbank für diesen Trend gefunden wurden."
        
        # Bei allgemeinen Trend-Anfragen die kuratierten Trends abrufen
        elif is_general_trend_query:
            try:
                logger.info("General trend query detected - fetching curated trends")
                trend_data = get_curated_trends(limit=5)
                
                # Trend-Daten in den System-Prompt einbauen
                if trend_data:
                    system_prompt += f"\n\nHier sind die aktuellen Trend-Daten aus der Trendlink-Datenbank:\n\n{trend_data}"
                    system_prompt += "\n\nBasiere deine Antwort AUSSCHLIESSLICH auf diesen Daten. Ergänze KEINE zusätzlichen Informationen aus deinem eigenen Wissen."
                    trendlink_context = trend_data
                    trendlink_data_type = "curated_trends"
                    logger.info("Successfully incorporated general trend data")
            except Exception as e:
                logger.error(f"Error fetching curated trends: {e}")
                system_prompt += "\n\nIch habe versucht, aktuelle Trend-Daten abzurufen, aber leider sind keine Daten verfügbar. Bitte teile dem Nutzer mit, dass derzeit keine Trend-Informationen in der Trendlink-Datenbank verfügbar sind."
        
        # GPT-4 Antwort mit get_gpt_response generieren
        logger.info("Generating response with GPT-4")
        response_text = get_gpt_response(user_message, system_prompt)
        
        # Antwort als JSON zurückgeben
        return jsonify({
            "response": response_text,
            "has_trend_data": bool(trendlink_context),
            "query_type": trendlink_data_type if trendlink_data_type else "general_finance"
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    """
    Simple health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

# Main entry point
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)), debug=True) 