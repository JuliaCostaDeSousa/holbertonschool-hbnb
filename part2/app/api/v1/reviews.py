from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('reviews', description='Review operations')

# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'place_id': fields.String(required=True, description='ID of the place')
})

@api.route('/')
class ReviewList(Resource):
    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """List all reviews"""
        reviews = facade.get_all_reviews()
        return [r.to_dict() for r in reviews]

    @jwt_required()
    @api.expect(review_model)
    @api.response(201, "Review is created")
    @api.response(400, 'Invalid input data or business rule violated')
    def post(self):
        current_user = get_jwt_identity()
        data = api.payload

        place = facade.get_place(data['place_id'])
        if not place:
            return {'error': 'Place not found'}, 404

        if place.owner_id == current_user['id']:
            return {'error': 'You cannot review your own place.'}, 400

        if facade.user_already_reviewed_place(current_user['id'], data['place_id']):
            return {'error': 'You have already reviewed this place.'}, 400

        try:
            new_review = facade.create_review(data)
            return new_review.to_dict(), 201
        except ValueError as e:
            return {'error': str(e)}, 400

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get a review by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        return review.to_dict()
    
    @jwt_required()
    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')    
    def put(self, review_id):
        """Update a review"""
        current_user = get_jwt_identity()
        data = api.payload
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        if review.user_id != current_user['id'] and not current_user.get('is_admin', False):
            return {'error': 'Forbidden'}, 403
        if not (1 <= data['rating'] <= 5):
            return {'error': 'Rating must be between 1 and 5'}, 400
        updated = facade.update_review(review_id, data)
        return updated.to_dict(), 200
    
    @jwt_required()
    @api.response(204, 'Review deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review"""
        current_user = get_jwt_identity()
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        if review.user_id != current_user['id'] and not current_user['is_admin']:
            return {'error': 'Forbidden'}, 403
        facade.delete_review(review_id)
        return {'message': 'Review deleted'}, 200
