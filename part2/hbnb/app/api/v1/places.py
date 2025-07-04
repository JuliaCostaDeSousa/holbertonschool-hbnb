from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade

api = Namespace('places', description='Place operations')

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

place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'amenities': fields.List(fields.String, required=True, description="List of amenity IDs")
})


@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """Register a new place (authenticated users only)"""
        place_data = api.payload
        current_user_id = get_jwt_identity()
        place_data['owner_id'] = current_user_id

        try:
            new_place = facade.create_place(place_data)
        except ValueError as error:
            return {'error': str(error)}, 400

        return {
            'id': new_place.id,
            'title': new_place.title,
            'description': new_place.description,
            'price': new_place.price,
            'latitude': new_place.latitude,
            'longitude': new_place.longitude,
            'owner': {
                'id': new_place.owner.id,
                'first_name': new_place.owner.first_name,
                'last_name': new_place.owner.last_name,
                'email': new_place.owner.email
            },
            'amenities': [{
                'id': amenity.id,
                'name': amenity.name
            } for amenity in new_place.amenities]
        }, 201

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places"""
        places = facade.get_all_places()
        return [{
            'id': place.id,
            'title': place.title,
            'description': place.description,
            'price': place.price,
            'latitude': place.latitude,
            'longitude': place.longitude,
            'owner': {
                'id': place.owner.id,
                'first_name': place.owner.first_name,
                'last_name': place.owner.last_name,
                'email': place.owner.email
            },
            'amenities': [{
                'id': amenity.id,
                'name': amenity.name
            } for amenity in place.amenities]
        } for place in places], 200


@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details by ID"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        return {
            'id': place.id,
            'title': place.title,
            'description': place.description,
            'price': place.price,
            'latitude': place.latitude,
            'longitude': place.longitude,
            'owner': {
                'id': place.owner.id,
                'first_name': place.owner.first_name,
                'last_name': place.owner.last_name,
                'email': place.owner.email
            },
            'amenities': [{
                'id': amenity.id,
                'name': amenity.name
            } for amenity in place.amenities]
        }, 200

    @jwt_required()
    @api.expect(place_model, validate=True)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    def put(self, place_id):
        """Update a place's information (admins or owner)"""
        current_user = get_jwt_identity()
        is_admin = current_user.get('is_admin', False)
        user_id = current_user.get('id')

        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        if not is_admin and place.owner.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        place_data = api.payload
        try:
            updated_place = facade.update_place(place_id, place_data)
        except ValueError as error:
            return {'error': str(error)}, 400

        return {
            'id': updated_place.id,
            'title': updated_place.title,
            'description': updated_place.description,
            'price': updated_place.price,
            'latitude': updated_place.latitude,
            'longitude': updated_place.longitude,
            'owner': {
                'id': updated_place.owner.id,
                'first_name': updated_place.owner.first_name,
                'last_name': updated_place.owner.last_name,
                'email': updated_place.owner.email
            },
            'amenities': [
                {
                    'id': amenity.id,
                    'name': amenity.name
                }
                for amenity in updated_place.amenities
            ]
        }, 200
