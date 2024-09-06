from flask import Flask
from flask_mongoengine import MongoEngine
from flask_socketio import SocketIO
from .controllers.client_controller import client_blueprint 
from .controllers.llm_controller import llm_blueprint, register_socketio_handlers

from .config import Config

db = MongoEngine()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)

    # Loading configuration
    app.config.from_object(Config)

    app.register_blueprint(llm_blueprint, url_prefix='/bot')
    app.register_blueprint(client_blueprint, url_prefix='/client')

    # Initialize MongoDB
    db.init_app(app)
    
    register_socketio_handlers(socketio)
    
    socketio.init_app(app)


    return app
