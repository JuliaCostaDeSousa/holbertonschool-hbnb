from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user')
})

@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(409, 'Invalid input data')
    def post(self):
        """Register a new user"""
        user_data = api.payload

        try:
            facade.get_user_by_email(user_data['email'])
            return {"error": "Email already used"}, 400
        except ValueError:
            pass

        new_user = facade.create_user(user_data)
        return {
            'id': new_user["id"],
            'first_name': new_user["first_name"],
            'last_name': new_user["last_name"],
            'email': new_user["email"]
        }, 201


    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """Get list of all users"""
        users = facade.get_all_users()
        return [{
            'id': user["id"],
            'first_name': user["first_name"],
            'last_name': user["last_name"],
            'email': user["email"]
        } for user in users], 200


@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID"""
        try:
            user = facade.get_user(user_id)
            return {
                'id': user["id"],
                'first_name': user["first_name"],
                'last_name': user["last_name"],
                'email': user["email"]
            }, 200
        except:
            return {"error": "User not found"}, 404

    @api.expect(user_model, validate=True)
    @api.response(200, 'User updated successfully')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input')
    def put(self, user_id):
        """Update an existing user's information"""
        update_data = api.payload
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


