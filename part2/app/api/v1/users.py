from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
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
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def get(self):
        """List all users (admin only)"""
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Forbidden'}, 403
        users = facade.get_users()
        return [user.to_dict() for user in users]
    
    @api.expect(user_model)
    def post(self):
        """Create a new user (public route)"""
        data = api.payload
        required_fields = ['first_name', 'last_name', 'email', 'password']
        for field in required_fields:
            if field not in data or not isinstance(data[field], str) or not data[field].strip():
                return {'error': "Field '{}' is required and cannot be empty.".format(field)}, 400

        if facade.get_user_by_email(data['email']):
            return {'error': 'Email already registered'}, 400

        # (Facultatif) Bloquer la création d'admin manuellement
        data['is_admin'] = False

        user = facade.create_user(data)
        return user.to_dict(), 201

@api.route('/<string:user_id>')
@api.param('user_id', 'The user identifier')
class UserResource(Resource):
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def get(self, user_id):
        """Get user details"""
        current_user = get_jwt_identity()
        if user_id != current_user['id'] and not current_user['is_admin']:
            return {'error': 'Forbidden'}, 403
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict()

    @jwt_required()
    @api.expect(user_model)
    @api.doc(security='Bearer Auth')
    def put(self, user_id):
        """Update user data"""
        current_user = get_jwt_identity()
        data = api.payload

        if user_id != current_user['id'] and not current_user['is_admin']:
            return {'error': 'Forbidden'}, 403
        required_fields = ['first_name', 'last_name', 'email']
        for field in required_fields:
            if field not in data or not isinstance(data[field], str) or not data[field].strip():
                return {'error': "Field '{}' is required and cannot be empty.".format(field)}, 400
        if 'password' in data and (not isinstance(data['password'], str) or not data['password'].strip()):
            return {'error': "Password cannot be empty if provided."}, 400
        
        updated_user = facade.update_user(user_id, data)
        return updated_user.to_dict()

    @jwt_required()
    @api.doc(security='Bearer Auth')
    def delete(self, user_id):
        """Delete user (self or admin only)"""
        current_user = get_jwt_identity()
        if user_id != current_user['id'] and not current_user['is_admin']:
            return {'error': 'Forbidden'}, 403
        facade.delete_user(user_id)
        return {'message': 'User deleted'}, 204
