from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade
from app.extensions import db

api = Namespace('places', description='Place operations')

# Swagger models
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
    'id': fields.String(description='Place ID'),
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'amenities': fields.List(fields.String, required=True, description="List of amenities ID's")
})

@api.route('/')
class PlaceList(Resource):
    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """List all places"""
        try:
            places = facade.get_all_places()
            return [p.to_dict() for p in places], 200
        except Exception as e:
            return {'error': 'Unexpected error: ' + str(e)}, 500

    @jwt_required()
    @api.expect(place_model)
    @api.response(201, "Place successfully created")
    @api.response(400, "Bad request")
    @api.response(404, "User or amenity not found")
    def post(self):
        """Create a new place (auth required)"""
        user_id = get_jwt_identity()
        try:
            user = facade.get_user(user_id)
            if not user:
                return {'error': 'User not found'}, 404

            data = api.payload
            data['owner_id'] = user_id

            new_place = facade.create_place(data)
            return new_place.to_dict(), 201
        except KeyError as error:
            return {"error": str(error)}, 404
        except ValueError as error:
            return {"error": str(error)}, 400
        except Exception as e:
            return {"error": "Unexpected error: " + str(e)}, 500


@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.response(200, "Place details retrieved successfully")
    @api.response(404, "Place not found")
    def get(self, place_id):
        """Fetch a place by ID"""
        try:
            place = facade.get_place(place_id)
            if not place:
                return {'error': 'Place not found'}, 404
            return place.to_dict(), 200
        except Exception as e:
            return {'error': 'Unexpected error: ' + str(e)}, 500

    @jwt_required()
    @api.expect(place_model)
    @api.response(200, "Place updated successfully")
    @api.response(403, "Forbidden")
    @api.response(404, "Place not found")
    @api.response(400, "Invalid data")
    def put(self, place_id):
        """Update a place (auth required)"""
        try:
            updated_place = facade.update_place(place_id, api.payload)
            return updated_place.to_dict(), 200
        except PermissionError:
            return {"error": "forbidden"}, 403
        except KeyError as e:
            return {"error": str(e)}, 404
        except ValueError as err:
            return {"error": str(err)}, 400
        except Exception as e:
            return {"error": "Unexpected error: " + str(e)}, 500

    @jwt_required()
    @api.response(204, "Place deleted successfully")
    @api.response(403, "Forbidden")
    @api.response(404, "Place not found")
    def delete(self, place_id):
        """Delete a place (auth required)"""
        try:
            facade.delete_place(place_id)
            return '', 204
        except PermissionError:
            return {"error": "forbidden"}, 403
        except KeyError:
            return {"error": "Place not found"}, 404
        except Exception as e:
            return {"error": "Unexpected error: " + str(e)}, 500
