from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.services import facade

api = Namespace('auth', description='Authentication operations')

login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

@api.route('/login')
class LoginResource(Resource):
    @api.expect(login_model)
    @api.response(200, "Login successful")
    @api.response(401, "Invalid credentials")
    @api.doc(description="Authenticate a user and return a JWT token.")
    def post(self):
        """Authenticate user and return a JWT token"""
        credentials = api.payload
        if not credentials.get("email") or not credentials.get("password"):
            return {'error': 'Email and password are required'}, 400

        user = facade.get_user_by_email(credentials['email'])

        if user and user.verify_password(credentials['password']):
            identity_payload = {
                "id": user.id,
                "is_admin": user.is_admin
            }
            access_token = create_access_token(identity=identity_payload)
            return {'access_token': access_token}, 200

        return {'error': 'Invalid credentials'}, 401
