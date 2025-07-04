from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from app.services import facade

api = Namespace('amenities', description='Amenity operations')

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})


@api.route('/')
class AmenityList(Resource):
    @api.expect(amenity_model, validate=True)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    @api.response(409, 'Amenity already exists')
    @jwt_required()
    def post(self):
        """Create a new amenity (admin only)"""
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        amenity_data = api.payload
        name = amenity_data.get('name', '').strip()

        if not name:
            return {'error': 'Name is required'}, 400

        if facade.get_amenity_by_name(name):
            return {'error': 'Amenity already exists'}, 409

        try:
            new_amenity = facade.create_amenity({'name': name})
            return {'id': new_amenity.id, 'name': new_amenity.name}, 201
        except ValueError as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """Retrieve a list of all amenities"""
        amenities = facade.get_all_amenities()
        return [{'id': a.id, 'name': a.name} for a in amenities], 200


@api.route('/<amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get amenity details by ID"""
        try:
            amenity = facade.get_amenity(amenity_id)
            return {'id': amenity.id, 'name': amenity.name}, 200
        except ValueError as e:
            return {'error': str(e)}, 404

    @api.expect(amenity_model, validate=True)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    @jwt_required()
    def put(self, amenity_id):
        """Update an amenity (admin only)"""
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        amenity_data = api.payload
        name = amenity_data.get('name', '').strip()

        if not name:
            return {'error': '"name" is required'}, 400

        try:
            updated_amenity = facade.update_amenity(amenity_id, {'name': name})
            return {'id': updated_amenity.id, 'name': updated_amenity.name}, 200
        except ValueError as e:
            if str(e) == "Amenity not found":
                return {'error': str(e)}, 404
            return {'error': str(e)}, 400
