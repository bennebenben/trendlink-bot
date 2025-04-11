import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # CORS für Cross-Origin-Anfragen hinzugefügt
from dotenv import load_dotenv
import requests
from datetime import datetime
from dateutil import parser
import logging

# Import the specialized Trendlink API module
from trendlink_api import get_curated_trends
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
    
    If the message is about trends, it uses the specialized get_curated_trends() function
    to fetch the latest curated trends directly from the Trendlink API and provides them
    to GPT-4 for a contextualized, expert response.
    """
    try:
        data = request.json
        
        if not data or "message" not in data:
            return jsonify({"error": "No message provided"}), 400
            
        user_message = data["message"]
        
        # Trend-Keywords für die Erkennung relevanter Anfragen
        trend_keywords = ["trend", "trends", "trending", "aktuell", "neu", "neueste", "markt", 
                         "finanzen", "wirtschaft", "entwicklung", "zukunft", "investition"]
        
        # Prüfen, ob es eine trend-bezogene Anfrage ist
        is_trend_query = any(keyword in user_message.lower() for keyword in trend_keywords)
        
        # Experten-System-Prompt definieren
        system_prompt = (
            "Du bist ein Finanztrend-Experte. Antworte klar, faktenbasiert und effizient. "
            "Deine Expertise liegt in der Analyse von Markttrends und wirtschaftlichen Entwicklungen. "
            "Halte deine Antworten präzise und nutzerorientiert. "
            "Wenn du über Trends sprichst, sei spezifisch und stelle die relevantesten Informationen in den Vordergrund."
        )
        
        trendlink_context = ""
        
        # Bei trend-bezogenen Anfragen die kuratierten Trends abrufen
        if is_trend_query:
            try:
                logger.info("Trend query detected - fetching curated trends")
                trend_data = get_curated_trends(limit=5)
                
                # Trend-Daten in den System-Prompt einbauen
                if trend_data:
                    system_prompt += f"\n\nHier sind die aktuellen Trenddaten, auf die du dich in deiner Antwort beziehen sollst:\n\n{trend_data}"
                    trendlink_context = trend_data
                    logger.info("Successfully incorporated trend data into prompt")
            except Exception as e:
                logger.error(f"Error fetching curated trends: {e}")
                system_prompt += "\n\nHinweis: Es gab ein Problem beim Abrufen der aktuellen Trenddaten. Bitte erwähne dies in deiner Antwort."
        
        # GPT-4 Antwort mit get_gpt_response generieren
        logger.info("Generating response with GPT-4")
        response_text = get_gpt_response(user_message, system_prompt)
        
        # Antwort als JSON zurückgeben
        return jsonify({
            "response": response_text,
            "has_trend_data": bool(trendlink_context),
            "query_type": "trend_related" if is_trend_query else "general"
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