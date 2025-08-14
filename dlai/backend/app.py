#!/usr/bin/env python3
"""
Flask Backend for Gatorade AB Testing Dashboard
Integrates the advanced chatbot with session memory and embeddings
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import asyncio
import os
import sys
import logging
from datetime import datetime
import uuid

# Add parent directory to path to import our chatbot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modern_chatbot import ModernDataChatbot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])  # Allow React dev server

# Global chatbot instance
chatbot = None
active_sessions = {}

def initialize_chatbot():
    """Initialize the chatbot with data files"""
    global chatbot
    try:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'tiendas_detalle.csv')
        maestro_path = os.path.join(os.path.dirname(__file__), '..', 'maestro_tiendas.csv')
        
        chatbot = ModernDataChatbot(data_path, maestro_path)
        logger.info("✅ Chatbot initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize chatbot: {e}")
        return False

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "chatbot_ready": chatbot is not None
    })

@app.route('/api/chat/start', methods=['POST'])
def start_chat_session():
    """Start a new chat session"""
    try:
        data = request.get_json()
        user_email = data.get('userEmail', 'anonymous')
        
        # Generate new session ID
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Store session info
        active_sessions[session_id] = {
            'user_email': user_email,
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        
        logger.info(f"🆔 New session started: {session_id} for {user_email}")
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "welcome_message": "¡Hola! Soy tu asistente de análisis de datos para el proyecto Gatorade. Puedo ayudarte con consultas sobre las tiendas, experimentos A/B, conversiones y métricas de negocio. ¿Qué te gustaría analizar?"
        })
    
    except Exception as e:
        logger.error(f"❌ Error starting chat session: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """Process a chat message"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message = data.get('message', '').strip()
        
        if not session_id or not message:
            return jsonify({"success": False, "error": "Missing session_id or message"}), 400
        
        if chatbot is None:
            return jsonify({"success": False, "error": "Chatbot not initialized"}), 500
        
        # Update session activity
        if session_id in active_sessions:
            active_sessions[session_id]['last_activity'] = datetime.now()
        
        logger.info(f"💬 Processing message in session {session_id}: {message[:50]}...")
        
        # Process message with our advanced chatbot (run async in sync context)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(chatbot.ask(message, session_id=session_id))
        finally:
            loop.close()
        
        # Format response for frontend
        chat_response = {
            "success": True,
            "response": {
                "text": response["answer"],
                "data": response.get("data", []),
                "sql_used": response.get("sql_used", ""),
                "sql_executed": response.get("sql_executed", True),
                "confidence": response.get("confidence", 0.5),
                "execution_time": response.get("execution_time", 0),
                "cached": response.get("cached", False),
                "insights": response.get("insights", {}),
                "session_id": session_id
            }
        }
        
        logger.info(f"✅ Response generated for {session_id} in {response.get('execution_time', 0):.2f}s")
        return jsonify(chat_response)
    
    except Exception as e:
        logger.error(f"❌ Error processing chat message: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chat/history/<session_id>')
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        if chatbot is None:
            return jsonify({"success": False, "error": "Chatbot not initialized"}), 500
        
        history = chatbot.get_session_history(session_id)
        
        return jsonify({
            "success": True,
            "history": history,
            "session_info": active_sessions.get(session_id, {})
        })
    
    except Exception as e:
        logger.error(f"❌ Error getting chat history: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/analytics/sessions')
def get_session_analytics():
    """Get analytics about chat sessions"""
    try:
        if chatbot is None:
            return jsonify({"success": False, "error": "Chatbot not initialized"}), 500
        
        cache_stats = chatbot.get_cache_stats()
        session_stats = chatbot.get_session_stats()
        
        return jsonify({
            "success": True,
            "analytics": {
                "cache": cache_stats,
                "sessions": session_stats,
                "active_sessions": len(active_sessions),
                "total_sessions": len(active_sessions)
            }
        })
    
    except Exception as e:
        logger.error(f"❌ Error getting analytics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/data/summary')
def get_data_summary():
    """Get summary of available data for the frontend"""
    try:
        if chatbot is None:
            return jsonify({"success": False, "error": "Chatbot not initialized"}), 500
        
        # Get basic schema info
        schema_info = chatbot.schema_info
        
        summary = {
            "tables": list(schema_info.get('tables', {}).keys()),
            "columns": schema_info.get('columns', {}),
            "sample_data": schema_info.get('categorical_samples', {}),
            "stats": schema_info.get('stats', {})
        }
        
        return jsonify({
            "success": True,
            "data_summary": summary
        })
    
    except Exception as e:
        logger.error(f"❌ Error getting data summary: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Serve React app for production
@app.route('/')
def serve_react_app():
    """Serve the React frontend"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_react_assets(path):
    """Serve React static assets"""
    return send_from_directory(app.static_folder, path)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors by serving React app (for client-side routing)"""
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Initialize chatbot on startup
    logger.info("🚀 Starting Flask backend for Gatorade AB Testing Dashboard...")
    
    if initialize_chatbot():
        logger.info("🤖 Chatbot ready! Starting Flask server...")
        
        # Run in development mode
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    else:
        logger.error("❌ Failed to initialize chatbot. Exiting...")
        sys.exit(1)