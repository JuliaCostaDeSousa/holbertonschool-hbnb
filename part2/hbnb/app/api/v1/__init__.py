from flask_restx import Api
from flask import Blueprint
from .amenities import api as amenities_ns
from .reviews import api as reviews_ns
from .places import api as places_ns
from .users import api as users_ns

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(api_bp, title='HBnB API', version='1.0', description='A simple HBnB REST API')

api.add_namespace(amenities_ns)
api.add_namespace(reviews_ns)
api.add_namespace(places_ns)