from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
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
    def get(self):
        """List all reviews"""
        reviews = facade.get_all_reviews()
        return [r.to_dict() for r in reviews]

    @jwt_required()
    @api.expect(review_model)
    @api.doc(security='Bearer Auth')
    def post(self):
        current_user = get_jwt_identity()
        data = api.payload
        print(f"Review POST data: {data}")

        data['user_id'] = current_user['id']
        if 'place_id' not in data or not data['place_id']:
            return {'error': 'place_id is required'}, 400
        if 'text' not in data or not data['text']:
            return {'error': 'text is required'}, 400
        if 'rating' not in data or not isinstance(data['rating'], int):
            return {'error': 'rating is required and must be an integer'}, 400
        if not (1 <= data['rating'] <= 5):
            return {'error': 'rating must be between 1 and 5'}, 400
        if 'place_id' not in data or not data['place_id']:
            return {'error': 'place_id is required'}, 400

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

@api.route('/<string:review_id>')
@api.param('review_id', 'The review identifier')
class ReviewResource(Resource):
    def get(self, review_id):
        """Get a review by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        return review.to_dict()
    
    @jwt_required()
    @api.expect(review_model)
    @api.doc(security='Bearer Auth')
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
        return updated.to_dict()
    
    @jwt_required()
    @api.doc(security='Bearer Auth')
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
