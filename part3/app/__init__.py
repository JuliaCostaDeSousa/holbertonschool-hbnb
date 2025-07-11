from config import DevelopmentConfig
from flask import Flask
from flask_restx import Api
from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.auth import api as auth_ns
from app.extensions import db, bcrypt, jwt
from app.api.v1.protected import api as protected_ns
from flask_jwt_extended import JWTManager
jwt = JWTManager()

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["JWT_SECRET_KEY"] = "super-secret-key"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"

    bcrypt.init_app(app)
    db.init_app(app)
    jwt.init_app(app) 
    with app.app_context():
        db.create_all()

    api = Api(app, version='1.0', title='HBnB Auth and DB', description='HBnB Authentication and Database')
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(auth_ns, path="/api/v1/auth")
    api.add_namespace(protected_ns, path="/api/v1/protected")

    return app
