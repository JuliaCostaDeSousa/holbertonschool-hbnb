from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from app.services import facade

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user')
})


def user_to_dict(user):
    return {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'places': [
            {
                'id': place.id,
                'title': place.title,
                'description': place.description,
                'price': place.price
            }
            for place in user.places
        ],
        'reviews': [
            {
                'id': review.id,
                'text': review.text,
                'rating': review.rating,
                'place': {
                    'id': review.place.id,
                    'title': review.place.title,
                    'description': review.place.description,
                    'price': review.place.price
                }
            }
            for review in user.reviews
        ]
    }


@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(409, 'Email already registered')
    def post(self):
        """Register a new user"""
        user_data = api.payload
        email = user_data.get('email', '').strip().lower()

        if facade.get_user_by_email(email):
            return {'error': 'Email already registered'}, 409

        user_data['email'] = email
        new_user = facade.create_user(user_data)
        return user_to_dict(new_user), 201

    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """Get list of all users"""
        users = facade.get_all_users()
        return [user_to_dict(user) for user in users], 200


@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        return user_to_dict(user), 200

    @api.expect(user_model, validate=True)
    @api.response(200, 'User updated successfully')
    @api.response(400, 'Invalid input')
    @api.response(404, 'User not found')
    @api.response(403, 'Admin privileges required')
    @api.response(409, 'Email already registered')
    @jwt_required()
    def put(self, user_id):
        """Update user's information - Admin only"""
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        user_data = api.payload
        email = user_data.get('email', '').strip().lower()

        existing_user = facade.get_user_by_email(email)
        if existing_user and existing_user.id != user.id:
            return {'error': 'Email already registered'}, 409

        user_data['email'] = email
        try:
            user = facade.update_user(user_id, update_data)
            return {
                'id': user["id"],
                'first_name': user["first_name"],
                'last_name': user["last_name"],
                'email': user["email"]
            }, 200
        except ValueError:
            return {"error": "User not found"}, 404


        return user_to_dict(updated_user), 200
