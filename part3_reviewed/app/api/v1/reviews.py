from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.facade import facade

api = Namespace("Reviews", path="/api/v1/reviews", description="Operations related to reviews")

review_model = api.model("Review", {
    "id": fields.String(readonly=True),
    "text": fields.String(required=True),
    "rating": fields.Integer(required=True, min=1, max=5),
    "place_id": fields.String(required=True),
    "user_id": fields.String(readonly=True),
})

@api.route("/")
class ReviewListResource(Resource):
    @jwt_required()
    @api.expect(review_model)
    @api.response(201, "Review created")
    @api.response(400, "Invalid input or duplicate/own review")
    @api.response(403, "Forbidden")
    @api.response(404, "User or place not found")
    def post(self):
        """Create a new review (auth required)"""
        user_id = get_jwt_identity()
        user = facade.get_user(user_id)
        if not user:
            return {"error": "User not found"}, 404

        data = api.payload
        rating = data.get("rating")
        if not (1 <= rating <= 5):
            return {"error": "Rating must be between 1 and 5"}, 400

        data["user_id"] = user.id

        try:
            review = facade.create_review(data)
            return review.to_dict(), 201
        except LookupError as e:
            return {"error": str(e)}, 404
        except PermissionError as e:
            return {"error": str(e)}, 403
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": "Unexpected error: " + str(e)}, 500

    @api.response(200, "Success")
    def get(self):
        """List all reviews"""
        reviews = facade.get_all_reviews()
        return [r.to_dict() for r in reviews], 200


@api.route("/<string:review_id>")
@api.param("review_id", "The review identifier")
class ReviewResource(Resource):
    @api.response(200, "Success")
    @api.response(404, "Review not found")
    def get(self, review_id):
        """Get a single review by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {"error": "Review not found"}, 404
        return review.to_dict(), 200

    @jwt_required()
    @api.expect(review_model)
    @api.response(200, "Review updated")
    @api.response(400, "Invalid input")
    @api.response(403, "Forbidden")
    @api.response(404, "Review not found")
    def put(self, review_id):
        """Update a review (owner or admin only)"""
        user_id = get_jwt_identity()
        user = facade.get_user(user_id)
        if not user:
            return {"error": "User not found"}, 404

        data = api.payload
        try:
            updated = facade.update_review(review_id, data)
            return updated.to_dict(), 200
        except KeyError as e:
            return {"error": str(e)}, 404
        except PermissionError:
            return {"error": "forbidden"}, 403
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": "Unexpected error: " + str(e)}, 500

    @jwt_required()
    @api.response(200, "Review deleted")
    @api.response(403, "Forbidden")
    @api.response(404, "Review not found")
    def delete(self, review_id):
        """Delete a review (owner or admin only)"""
        user_id = get_jwt_identity()
        user = facade.get_user(user_id)
        if not user:
            return {"error": "User not found"}, 404

        try:
            facade.delete_review(review_id)
            return {"message": "Review deleted"}, 200
        except KeyError:
            return {"error": "Review not found"}, 404
        except PermissionError:
            return {"error": "forbidden"}, 403
        except Exception as e:
            return {"error": "Unexpected error: " + str(e)}, 500
