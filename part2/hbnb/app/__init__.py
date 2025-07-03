from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from api.v1.auth import api as auth_namespace
from api.v1.users import api as users_namespace
from api.v1.places import api as places_namespace
from api.v1.reviews import api as reviews_namespace
from api.v1.amenities import api as amenities_namespace

jwt = JWTManager()

def create_app(config_class=None):
    app = Flask(__name__)
    api = Api(app,version="1.0",
        title="HBnB API",
        description="API documentation for the HBnB project"
    )
    api.add_namespace(auth_namespace, path="/api/v1/auth")
    api.add_namespace(users_namespace, path="/api/v1/users")
    api.add_namespace(places_namespace, path="/api/v1/places")
    api.add_namespace(reviews_namespace, path="/api/v1/reviews")
    api.add_namespace(amenities_namespace, path="/api/v1/ameneties")

    return app
