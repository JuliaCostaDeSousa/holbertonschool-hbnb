from flask import Flask
from app.api.v1 import api_bp  # <-- import du blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(api_bp)  # <-- enregistrement du blueprint
    return app