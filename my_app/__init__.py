from flask import Flask
from flask_cors import CORS
from flask_wtf import CSRFProtect
import os
from dotenv import load_dotenv
from flask_socketio import SocketIO

load_dotenv(override=True)

csrf = CSRFProtect()
cors = CORS()
socketio = SocketIO()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.getenv("SECRET_KEY")
        )
    else:
        app.config.from_mapping(test_config)

    cors.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app)

    # Register download blueprint
    from .routes import download_bp
    app.register_blueprint(download_bp)

    return app