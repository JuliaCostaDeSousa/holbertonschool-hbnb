from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('amenities', description='Amenity operations')

# Define the amenity model for input validation and documentation
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

@api.route('/')
class AmenityList(Resource):
    @api.expect(amenity_model)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new amenity"""
        amenity_data = api.payload

        if not amenity_data or 'name' not in amenity_data:
            return {'error': '"name" is required'}, 400
        if not isinstance(amenity_data['name'], str):
            return {'error': '"name" must be a string'}, 400    
        
        try:
            
            new_amenity = facade.create_amenity(amenity_data)
            return new_amenity, 201

        except ValueError as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """Retrieve a list of all amenities"""

        amenities = facade.get_all_amenities()
        return amenities, 200

@api.route('/<amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get amenity details by ID"""
        try:
            amenity = facade.get_amenity(amenity_id)
            return amenity, 200
        except ValueError as e:
            return {'error': str(e)}, 404

    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    def put(self, amenity_id):
        amenity_data = api.payload

        if not amenity_data:
            return {'error': 'Amenity does not exist'}, 404
        if not amenity_data or 'name' not in amenity_data:
            return {'error': '"name" is required'}, 400
        if not isinstance(amenity_data['name'], str):
            return {'error': '"name" must be a string'}, 400    
        
        try:
            updated_amenity = facade.update_amenity(amenity_id, amenity_data)
            return {"message": "Amenity updated successfully"}, 200
        except ValueError as e:
            if str(e) == "Amenity not found":
                return {'error': str(e)}, 404
            return {'error': str(e)}, 400
