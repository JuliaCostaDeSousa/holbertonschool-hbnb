from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
)
from flask import request
from app.services import facade
from app.extensions import db

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user'),
    'is_admin': fields.Boolean(required=False, description='Is admin user')
})


@api.route('/')
class UserList(Resource):
    @jwt_required()
    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """List all users (admin only)"""
        try:
            user_id = get_jwt_identity()
            current_user = facade.get_user(user_id)
            if not current_user or not current_user.is_admin:
                return {'error': 'Admin access required'}, 403

            users = facade.get_users()
            return [user.to_dict() for user in users], 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @api.expect(user_model)
    @api.response(201, 'User created successfully')
    @api.response(409, 'Email already registered')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Create a new user (public route)"""
        data = api.payload

        is_admin_requested = data.get('is_admin', False)
        all_users = facade.get_users()
        if is_admin_requested and all_users:
            try:
                verify_jwt_in_request()
                jwt_data = get_jwt()
                if not jwt_data.get('is_admin'):
                    return {'error': 'Admin privileges required to set is_admin'}, 403
            except Exception:
                return {'error': 'Authentication required to set is_admin'}, 401

        if facade.get_user_by_email(data['email']):
            return {'error': 'Email already registered'}, 409

        try:
            user = facade.create_user(data)
            return user.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400


@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    @jwt_required()
    def get(self, user_id):
        """Get user details"""
        try:
            user = facade.get_user(user_id)
            if not user:
                return {'error': 'User not found'}, 404
            return user.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @jwt_required()
    @api.expect(user_model)
    @api.response(200, 'User updated successfully')
    @api.response(400, 'You cannot modify email or password')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')
    def put(self, user_id):
        """Update user data"""
        try:
            updated_user = facade.update_user(user_id, api.payload)
            return updated_user.to_dict(), 200
        except PermissionError as e:
            db.session.rollback()
            return {'error': str(e)}, 403
        except ValueError as e:
            db.session.rollback()
            return {'error': str(e)}, 404
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @jwt_required()
    @api.response(204, 'User deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')
    def delete(self, user_id):
        """Delete user (self or admin only)"""
        try:
            current_user_id = get_jwt_identity()
            current_user = facade.get_user(current_user_id)
            if not current_user:
                return {'error': 'Current user not found'}, 404

            if user_id != current_user.id and not current_user.is_admin:
                return {'error': 'Unauthorized action'}, 403

            facade.delete_user(user_id)
            return '', 204
        except ValueError as e:
            db.session.rollback()
            return {'error': str(e)}, 404
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
