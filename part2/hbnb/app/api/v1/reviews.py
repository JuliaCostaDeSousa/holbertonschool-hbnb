from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('reviews', description='Review operations')

review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})


def review_to_dict(review):
    return {
        'id': review.id,
        'text': review.text,
        'rating': review.rating,
        'user': {
            'id': review.user.id,
            'first_name': review.user.first_name,
            'last_name': review.user.last_name,
            'email': review.user.email
        },
        'place': {
            'id': review.place.id,
            'title': review.place.title,
            'description': review.place.description,
            'price': review.place.price
        }
    }


@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model, validate=True)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Create a new review"""
        review_data = api.payload

        for field in ['text', 'rating', 'user_id', 'place_id']:
            if field not in review_data:
                return {'error': f'"{field}" is required'}, 400

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
            return review_to_dict(new_review), 201
        except ValueError as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Get all reviews"""
        reviews = facade.get_all_reviews()
        return [review_to_dict(r) for r in reviews], 200


@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get a review by its ID"""
        try:
            review = facade.get_review(review_id)
            return review_to_dict(review), 200
        except ValueError as e:
            return {'error': str(e)}, 404

    @api.expect(review_model, validate=True)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    def put(self, review_id):
        """Update an existing review"""
        review_data = api.payload

        try:
            _ = facade.get_review(review_id)
        except ValueError as e:
            return {'error': str(e)}, 404

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
            return review_to_dict(updated_review), 200
        except ValueError as e:
            return {'error': str(e)}, 400

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review by ID"""
        try:
            facade.delete_review(review_id)
            return {'message': 'Review deleted successfully'}, 200
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
            return [review_to_dict(r) for r in reviews], 200
        except ValueError as e:
            return {'error': str(e)}, 404
