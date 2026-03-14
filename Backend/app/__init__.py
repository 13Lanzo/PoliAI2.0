from flask import Flask
from flask_cors import CORS
from .config import Config
from app.utils.db import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Enable CORS for Angular frontend
    CORS(app)

    # Register Blueprints here
    from app.controllers.chat_controller import chat_bp
    app.register_blueprint(chat_bp, url_prefix='/api/chat')

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'message': 'PolibAI 2.0 API is running!'}

    return app
