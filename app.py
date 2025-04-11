import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import openai
import requests
from datetime import datetime
from dateutil import parser
import logging

# Import the specialized Trendlink API module
from trendlink_api import get_curated_trends

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    Chat endpoint that processes user messages and responds using OpenAI,
    incorporating data from Trendlink when relevant.
    
    If the message is about trends, it uses the specialized get_curated_trends() function
    to fetch the latest curated trends directly from the Trendlink API.
    
    For other Trendlink data requests, it falls back to the general fetch_trendlink_data function.
    """
    try:
        data = request.json
        
        if not data or "message" not in data:
            return jsonify({"error": "No message provided"}), 400
            
        user_message = data["message"]
        
        # Check if OpenAI API key is configured
        if not openai.api_key:
            return jsonify({"error": "OpenAI API key is not configured"}), 500
        
        # Determine if this is a trends-related query
        is_trend_query = any(keyword in user_message.lower() for keyword in 
                            ["trend", "trends", "trending", "aktuell", "neu", "neueste"])
        
        # Determine if we need other Trendlink data
        need_general_data = any(keyword in user_message.lower() for keyword in 
                               ["data", "statistics", "market", "information", "daten", "statistik", "markt"])
        
        trendlink_context = ""
        trendlink_data_type = None
        
        # Try to get curated trends first if it's a trend query
        if is_trend_query:
            try:
                logger.info("Trend query detected - fetching curated trends")
                trendlink_context = get_curated_trends(limit=5)
                trendlink_data_type = "curated_trends"
            except Exception as e:
                logger.error(f"Error fetching curated trends: {e}")
                # Fallback to general API if specialized call fails
                if need_general_data:
                    trendlink_data = fetch_trendlink_data()
                    trendlink_context = format_trendlink_data_for_chat(trendlink_data)
                    trendlink_data_type = "general_data"
        
        # For non-trend queries that still need market data
        elif need_general_data:
            logger.info("General data query detected")
            trendlink_data = fetch_trendlink_data()
            trendlink_context = format_trendlink_data_for_chat(trendlink_data)
            trendlink_data_type = "general_data"
        
        # Construct the message for OpenAI
        messages = [
            {"role": "system", "content": "You are a helpful assistant with access to market trend data. "
                                         "Provide insightful and concise responses based on the available information. "
                                         "If you have trend data available, incorporate it meaningfully into your response."}
        ]
        
        # Add Trendlink context if available
        if trendlink_context:
            if trendlink_data_type == "curated_trends":
                messages.append({"role": "system", "content": 
                                f"Here are the latest curated trends from Trendlink:\n\n{trendlink_context}"})
            else:
                messages.append({"role": "system", "content": 
                                f"Here is the latest data from Trendlink:\n\n{trendlink_context}"})
            
        # Add user message
        messages.append({"role": "user", "content": user_message})
        
        # Get response from OpenAI
        logger.info("Sending request to OpenAI API")
        response = openai.chat.completions.create(
            model="gpt-4",  # or another appropriate model
            messages=messages,
            max_tokens=800,
            temperature=0.7,
        )
        
        # Extract the assistant's message
        assistant_message = response.choices[0].message.content
        
        return jsonify({
            "response": assistant_message,
            "trendlink_data_included": bool(trendlink_context),
            "trendlink_data_type": trendlink_data_type
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
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True) 