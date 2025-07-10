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
    def get(self):
        """List all amenities"""
        return facade.get_all_amenities(), 200
    
    @jwt_required()
    @api.expect(amenity_model)
    @api.doc(security='Bearer Auth')
    def post(self):
        """Create a new amenity"""
        current_user = get_jwt_identity()
        if not current_user['is_admin']:
            return {'error': 'Admin access required'}, 403
        amenity = facade.create_amenity(api.payload)
        return amenity.to_dict(), 201

@api.route('/<string:amenity_id>')
@api.param('amenity_id', 'The amenity identifier')
class AmenityResource(Resource):
    def get(self, amenity_id):
        """Get an amenity by ID"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return amenity.to_dict(), 200
    
    @jwt_required()
    @api.expect(amenity_model)
    @api.doc(security='Bearer Auth')
    def put(self, amenity_id):
        """Update an amenity"""
        current_user = get_jwt_identity()
        if not current_user['is_admin']:
            return {'error': 'Admin access required'}, 403
        updated = facade.update_amenity(amenity_id, api.payload)
        if not updated:
            return {'error': 'Amenity not found'}, 404
        return updated.to_dict(), 200

    @jwt_required()
    @api.doc(security='Bearer Auth')
    def delete(self, amenity_id):
        """Delete an amenity"""
        current_user = get_jwt_identity()
        if not current_user['is_admin']:
            return {'error': 'Admin access required'}, 403
        facade.delete_amenity(amenity_id)
        return {'message': 'Amenity deleted'}, 204
