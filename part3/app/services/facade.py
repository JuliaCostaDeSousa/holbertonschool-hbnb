# app/facade.py

from app.persistence.user_repository import UserRepository
from app.persistence.place_repository import PlaceRepository
from app.persistence.amenity_repository import AmenityRepository
from app.persistence.review_repository import ReviewRepository
from app.extensions import db
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review
from flask_jwt_extended import get_jwt_identity


class HBnBFacade:
    def __init__(self):
        self.user_repo = UserRepository()
        self.amenity_repo = AmenityRepository()
        self.place_repo = PlaceRepository()
        self.review_repo = ReviewRepository()

    # ========== USER ==========

    def create_user(self, user_data):
        if not user_data.get("email") or not user_data.get("password"):
            raise ValueError("Email and password are required.")
        if self.user_repo.get_by_attribute("email", user_data["email"]):
            raise ValueError("Email already exists.")

        password = user_data.pop("password")
        user = User(**user_data)
        user.hash_password(password)
        try:
            self.user_repo.add(user)
        except Exception:
            db.session.rollback()
            raise
        return user

    def get_users(self):
        return self.user_repo.get_all()

    def get_user(self, user_id):
        if not user_id:
            return None
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute("email", email)

    def update_user(self, user_id, user_data):
        user = self.get_user(user_id)
        if not user:
            raise ValueError("User not found.")

        protected_fields = ("email", "password", "is_admin")
        current_user_id = get_jwt_identity()
        current_user = self.get_user(current_user_id)
        if not current_user:
            raise PermissionError("forbidden")

        if not current_user.is_admin:
            for field in protected_fields:
                if field in user_data:
                    raise PermissionError("forbidden")

        try:
            self.user_repo.update(user_id, user_data)
        except Exception:
            db.session.rollback()
            raise
        return self.get_user(user_id)

    def delete_user(self, user_id):
        current_user_id = get_jwt_identity()
        current_user = self.get_user(current_user_id)
        if not current_user or (not current_user.is_admin and current_user.id != user_id):
            raise PermissionError("forbidden")

        try:
            self.user_repo.delete(user_id)
        except Exception:
            db.session.rollback()
            raise

    # ========== AMENITY ==========

    def create_amenity(self, amenity_data):
        name = amenity_data.get("name", "").strip()
        if not isinstance(name, str) or not name:
            raise ValueError("Amenity name must be a non-empty string.")
        amenity = Amenity(name=name)
        try:
            self.amenity_repo.add(amenity)
        except Exception:
            db.session.rollback()
            raise
        return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, data):
        try:
            return self.amenity_repo.update(amenity_id, data)
        except Exception:
            db.session.rollback()
            raise

    def delete_amenity(self, amenity_id):
        try:
            self.amenity_repo.delete(amenity_id)
        except Exception:
            db.session.rollback()
            raise

    # ========== PLACE ==========

    def create_place(self, place_data):
        user = self.get_user(place_data["owner_id"])
        if not user:
            raise ValueError("Invalid owner_id")

        amenities_ids = place_data.pop("amenities", [])
        place_data.pop("owner_id", None)
        place = Place(owner=user, **place_data)

        try:
            self.place_repo.add(place)
            db.session.flush()
            user.add_place(place)

            for amenity_id in amenities_ids:
                amenity = self.get_amenity(amenity_id)
                if not amenity:
                    raise KeyError(f"Amenity with id {amenity_id} not found")
                place.add_amenity(amenity)

            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        place = self.get_place(place_id)
        if not place:
            raise KeyError("Place not found")

        current_user_id = get_jwt_identity()
        current_user = self.get_user(current_user_id)
        if not current_user or (not current_user.is_admin and place.owner_id != current_user.id):
            raise PermissionError("forbidden")

        for field in ["owner", "owner_id", "id"]:
            place_data.pop(field, None)

        try:
            return self.place_repo.update(place_id, place_data)
        except Exception:
            db.session.rollback()
            raise

    def delete_place(self, place_id):
        place = self.get_place(place_id)
        if not place:
            raise KeyError("Place not found")

        current_user_id = get_jwt_identity()
        current_user = self.get_user(current_user_id)
        if not current_user or (not current_user.is_admin and place.owner_id != current_user.id):
            raise PermissionError("forbidden")

        try:
            self.place_repo.delete(place_id)
        except Exception:
            db.session.rollback()
            raise

    # ========== REVIEW ==========

    def create_review(self, review_data):
        user = self.get_user(review_data["user_id"])
        place = self.get_place(review_data["place_id"])

        if not user:
            raise LookupError("User not found")
        if not place:
            raise LookupError("Place not found")
        if place.owner_id == user.id:
            raise PermissionError("forbidden")
        if self.user_already_reviewed(user.id, place.id):
            raise ValueError("You have already reviewed this place")

        review = Review(**review_data)

        try:
            self.review_repo.add(review)
            db.session.flush()
            user.add_review(review)
            place.add_review(review)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        place = self.get_place(place_id)
        if not place:
            raise ValueError("Place not found")
        return place.reviews

    def update_review(self, review_id, review_data):
        review = self.get_review(review_id)
        if not review:
            raise KeyError("Review not found")

        current_user_id = get_jwt_identity()
        current_user = self.get_user(current_user_id)
        if not current_user or (not current_user.is_admin and review.user_id != current_user.id):
            raise PermissionError("forbidden")

        for field in ["user_id", "place_id"]:
            review_data.pop(field, None)

        rating = review_data.get("rating")
        if rating is not None and not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")

        try:
            return self.review_repo.update(review_id, review_data)
        except Exception:
            db.session.rollback()
            raise

    def delete_review(self, review_id):
        review = self.get_review(review_id)
        if not review:
            raise KeyError("Review not found")

        current_user_id = get_jwt_identity()
        current_user = self.get_user(current_user_id)
        if not current_user or (not current_user.is_admin and review.user_id != current_user.id):
            raise PermissionError("forbidden")

        try:
            user = self.get_user(review.user_id)
            place = self.get_place(review.place_id)

            if user and review in user.reviews:
                user.delete_review(review)
            if place and review in place.reviews:
                place.delete_review(review)

            self.review_repo.delete(review_id)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def user_already_reviewed(self, user_id: str, place_id: str) -> bool:
        return self.review_repo.get_by_user_and_place(user_id, place_id) is not None


facade = HBnBFacade()
