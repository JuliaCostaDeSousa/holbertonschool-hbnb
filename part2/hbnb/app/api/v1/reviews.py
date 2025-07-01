from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('reviews', description='Review operations')

# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new review"""
        review_data = api.payload

        if not review_data or 'text' not in review_data:
            return {'error': '"text" is required'}, 400
        if 'rating' not in review_data:
            return {'error': '"rating" is required'}, 400
        if 'user_id' not in review_data:
            return {'error': '"user_id" is required'}, 400
        if 'place_id' not in review_data:
            return {'error': '"place_id" is required'}, 400
        
        if not isinstance(review_data['text'], str):
            return {'error': '"text" must be a string'}, 400
        if not isinstance(review_data['rating'], int):
            return {'error': '"rating" must be an integer'}, 400
        if not isinstance(review_data['user_id'], str):
            return {'error': '"user_id" must be a string'}, 400
        if not isinstance(review_data['place_id'], str):
            return {'error': '"place_id" must be a string'}, 400
        
        if not (1 <= review_data['rating'] <= 5):
            return {'error': '"rating" must be between 1 and 5'}, 400

        try:
            
            new_review = facade.create_review(review_data)
            return new_review, 201

        except ValueError as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Retrieve a list of all reviews"""
        reviews = facade.get_all_reviews()
        return reviews, 200

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID"""
        try:
            review = facade.get_review(review_id)
            return review, 200
        except ValueError as e:
            return {'error': str(e)}, 404

    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    def put(self, review_id):
        review_data = api.payload

        if not review_data:
            return {'error': 'Review does not exist'}, 404
        if 'text' not in review_data:
            return {'error': '"text" is required'}, 400
        if 'rating' not in review_data:
            return {'error': '"rating" is required'}, 400
        if 'user_id' not in review_data:
            return {'error': '"user_id" is required'}, 400
        if 'place_id' not in review_data:
            return {'error': '"place_id" is required'}, 400

        if not isinstance(review_data['text'], str):
            return {'error': '"text" must be a string'}, 400
        if not isinstance(review_data['rating'], int):
            return {'error': '"rating" must be an integer'}, 400
        if not isinstance(review_data['user_id'], str):
            return {'error': '"user_id" must be a string'}, 400
        if not isinstance(review_data['place_id'], str):
            return {'error': '"place_id" must be a string'}, 400

        if not (1 <= review_data['rating'] <= 5):
            return {'error': '"rating" must be between 1 and 5'}, 400

        try:
            updated_review = facade.update_review(review_id, review_data)
            return {"message": "Review updated successfully"}, 200
        except ValueError as e:
            if str(e) == "Review not found":
                return {'error': str(e)}, 404
            return {'error': str(e)}, 400

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review"""
        try:
            facade.delete_review(review_id)
            return {"message": "Review deleted successfully"}, 200
        except ValueError as e:
            return {'error': str(e)}, 404

@api.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get all reviews for a specific place"""
        try:
            reviews = facade.get_reviews_by_place(place_id)
            return reviews, 200
        except ValueError as e:
            return {'error': str(e)}, 404
