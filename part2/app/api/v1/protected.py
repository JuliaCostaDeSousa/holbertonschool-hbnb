from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Namespace('protected', description='Protected resource operations')

@api.route('/protected')
class ProtectedResource(Resource):
    @jwt_required()
    def get(self):
        """A protected endpoint that requires a valid JWT token"""
        current_user = get_jwt_identity()
        user_id = current_user['id']
        is_admin = current_user.get('is_admin', False)


        return {'message': f'Hello, user {current_user}'}, 200