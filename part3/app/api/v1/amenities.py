from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade
from app.extensions import db

api = Namespace('amenities', description='Amenity operations')

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})


@api.route('/')
class AmenityList(Resource):
    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """List all amenities"""
        try:
            amenities = facade.get_all_amenities()
            return [a.to_dict() for a in amenities], 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @jwt_required()
    @api.expect(amenity_model)
    @api.response(201, 'Amenity created successfully')
    @api.response(403, 'Admin access required')
    @api.response(400, 'Amenity already exists or invalid data')
    def post(self):
        """Create a new amenity (admin only)"""
        try:
            current_user = facade.get_user(get_jwt_identity())
            if not current_user:
                return {'error': 'Current user not found'}, 404
            if not current_user.is_admin:
                return {'error': 'Admin access required'}, 403

            amenity_data = api.payload
            existing = facade.amenity_repo.get_by_attribute('name', amenity_data.get('name'))
            if existing:
                return {'error': 'Amenity already exists'}, 400

            new_amenity = facade.create_amenity(amenity_data)
            return new_amenity.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400


@api.route('/<amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(403, 'Admin access required')
    @api.response(404, 'Amenity not found or user not found')
    def get(self, amenity_id):
        """Get an amenity by ID (admin only)"""
        try:
            current_user = facade.get_user(get_jwt_identity())
            if not current_user:
                return {'error': 'Current user not found'}, 404
            if not current_user.is_admin:
                return {'error': 'Admin access required'}, 403

            amenity = facade.get_amenity(amenity_id)
            if not amenity:
                return {'error': 'Amenity not found'}, 404
            return amenity.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @jwt_required()
    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(403, 'Admin access required')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid data')
    def put(self, amenity_id):
        """Update an amenity (admin only)"""
        try:
            current_user = facade.get_user(get_jwt_identity())
            if not current_user:
                return {'error': 'Current user not found'}, 404
            if not current_user.is_admin:
                return {'error': 'Admin access required'}, 403

            updated = facade.update_amenity(amenity_id, api.payload)
            if not updated:
                return {'error': 'Amenity not found'}, 404
            return updated.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

    @jwt_required()
    @api.response(204, 'Amenity deleted successfully')
    @api.response(403, 'Admin access required')
    @api.response(404, 'Amenity not found')
    def delete(self, amenity_id):
        """Delete an amenity (admin only)"""
        try:
            current_user = facade.get_user(get_jwt_identity())
            if not current_user:
                return {'error': 'Current user not found'}, 404
            if not current_user.is_admin:
                return {'error': 'Admin access required'}, 403

            facade.delete_amenity(amenity_id)
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400
