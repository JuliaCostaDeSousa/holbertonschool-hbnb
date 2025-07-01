from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from api.v1.auth import api as auth_namespace

jwt = JWTManager()

def create_app(config_class=None):
    app = Flask(__name__)
    if config_class:
        app.config.from_object(config_class)
    else:
        app.config["SECRET_KEY"] = "supersecretkey"
        app.config["JWT_SECRET_KEY"] = app.config["SECRET_KEY"]

    jwt.init_app(app)

    api = Api(
        app,
        version="1.0",
        title="HBnB API",
        description="API documentation for the HBnB project"
    )
    api.add_namespace(auth_namespace, path="/api/v1/auth")

    return app
