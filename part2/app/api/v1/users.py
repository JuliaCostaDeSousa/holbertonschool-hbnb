from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import request
from app.services import facade


api = Namespace('users', description='User operations')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user')
})

@api.route('/')
class UserList(Resource):
    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """List all users (admin only)"""
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Forbidden'}, 403
        users = facade.get_users()
        return [user.to_dict() for user in users]
    
    @api.expect(user_model)
    @api.response(201, 'User created with success')
    @api.response(409, 'Email already registered')
    @api.response(400, 'Input data invalid')
    def post(self):
        """Create a new user (public route)"""
        data = api.payload

        data_is_admin = data.get('is_admin', None)
        if data_is_admin:
            current_user = get_jwt()
            print(current_user)
            if current_user == {} or current_user['is_admin'] is False:
                return {'error': 'Admin privileges required'}, 403

        if facade.get_user_by_email(data['email']):
            return {'error': 'Email already registered'}, 400

        try:
            user = facade.create_user(data)
            return user.to_dict(), 201
        except Exception as error:
            return {'error': str(error)}, 400            

@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict(), 200

    @jwt_required()
    @api.expect(user_model)
    @api.response(200, 'User updated successfully')
    @api.response(404, 'User not found')
    @api.response(400, 'You cannot modify email or password.')
    @api.response(403, 'Unauthorized action')       
    def put(self, user_id):
        """Update user data"""
        try:
            current_user = get_jwt_identity()
            data = api.payload

            if user_id != current_user['id'] and not current_user['is_admin']:
                return {'error': 'Unauthorized action'}, 403
            if ('email' in data or 'password' in data) and current_user['is_admin'] is False:
                return {'error': 'You cannot modify email or password'}, 400
            
            user = facade.get_user(user_id)
            if not user:
                return {'error': 'User not found'}, 404
            
            updated_user = facade.update_user(user_id, data)
            return updated_user.to_dict()
        except Exception as e:
            return {'error': str(e)}, 500

    @jwt_required()
    @api.doc(security='Bearer Auth')
    def delete(self, user_id):
        """Delete user (self or admin only)"""
        try:
            current_user = get_jwt_identity()
            if user_id != current_user['id'] and not current_user['is_admin']:
                return {'error': 'Unauthorized action'}, 403
            user = facade.get_user(user_id)
            if not user:
                return {'error': 'User not found'}, 404
            facade.delete_user(user_id)
            return {'message': 'User deleted'}, 204
        except Exception as e:
            return {'error': str(e)}, 500
