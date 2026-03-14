from flask import Blueprint, request, jsonify
from app.services.ai_service import AIOrientationService
import traceback

chat_bp = Blueprint('chat', __name__)

# Creazione di un'istanza pigra per l'AIOrientationService
# L'inizializzazione richiede la GOOGLE_API_KEY
ai_service = None

def get_ai_service():
    global ai_service
    if ai_service is None:
        ai_service = AIOrientationService()
    return ai_service

@chat_bp.route('/ask', methods=['POST'])
def ask_polibai():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Nessun messaggio fornito'}), 400
        
    user_message = data['message']
    
    try:
        service = get_ai_service()
        response_data = service.hybrid_orchestrator(user_message)
        
        return jsonify({
            'status': 'success',
            'reply': response_data['answer'],
            'debug_routing': response_data['routing']
        })
    except Exception as e:
        print("Errore nella Chat API:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500
