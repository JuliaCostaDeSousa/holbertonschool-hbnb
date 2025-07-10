from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade


api = Namespace('places', description='Place operations')

# Define the models for related entities
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

# Define the place model for input validation and documentation
place_model = api.model('Place', {
    'id': fields.String(description='Place ID'),
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'owner': fields.Nested(user_model, description='Owner details'),
    'amenities': fields.List(fields.String, required=True, description="List of amenities ID's")
})

@api.route('/')
class PlaceList(Resource):
    @api.doc('list_places')
    def get(self):
        """List all places"""
        places = facade.get_all_places()
        return [p.to_dict() for p in places]

    @jwt_required()
    @api.expect(place_model)
    @api.doc(security='Bearer Auth')
    def post(self):
        """Create a new place (auth required)"""
        current_user = get_jwt_identity()
        data = api.payload
        try:
            new_place = facade.create_place(data)
            return new_place.to_dict(), 201
        except ValueError as e:
            return {'error': str(e)}, 400

@api.route('/<string:place_id>')
@api.param('place_id', 'The place identifier')
class PlaceResource(Resource):
    @api.doc('get_place')
    def get(self, place_id):
        """Fetch a place by ID"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        return place.to_dict()

    @jwt_required()
    @api.expect(place_model)
    @api.doc(security='Bearer Auth')
    def put(self, place_id):
        """Update a place (auth required)"""
        current_user = get_jwt_identity()
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        if place.owner_id != current_user['id'] and not current_user['is_admin']:
            return {'error': 'Forbidden'}, 403
        data = api.payload
        updated_place = facade.update_place(place_id, data)
        return updated_place.to_dict()

    @jwt_required()
    @api.doc(security='Bearer Auth')
    def delete(self, place_id):
        """Delete a place (auth required)"""
        current_user = get_jwt_identity()
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        if place.owner_id != current_user['id'] and not current_user['is_admin']:
            return {'error': 'Forbidden'}, 403
        facade.delete_place(place_id)
        return {'message': 'Place deleted'}, 204
