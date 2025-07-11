from app.persistence.user_repository import UserRepository
from app.persistence.place_repository import PlaceRepository
from app.persistence.amenity_repository import AmenityRepository
from app.persistence.review_repository import ReviewRepository
from app.extensions import db
import uuid
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

    # USER
    def create_user(self, user_data):
        try:
            if not user_data.get('email') or not user_data.get('password'):
                raise ValueError("Email and password are required.")
            
            if self.user_repo.get_by_attribute('email', user_data['email']):
                raise ValueError("Email already exists.")
            
            password = user_data.pop('password')
            user = User(**user_data)
            user.hash_password(password)
            self.user_repo.add(user)
            return user
        except Exception as error:
            raise ValueError(f"User creation failed: {str(error)}")
    
    def get_users(self):
        return self.user_repo.get_all()

    def get_user(self, user_id):
        try:
            user = self.user_repo.get(user_id)
            if not user:
                raise ValueError("User not found.")
            return user
        except Exception as e:
            raise ValueError(f"Error fetching user: {str(e)}")

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)
        
    def update_user(self, user_id, user_data):
        current_user = get_jwt_identity()

        if not current_user['is_admin'] and current_user['id'] != user_id:
            raise PermissionError("Unauthorized action")

        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found.")
        
        self.user_repo.update(user_id, user_data)
        return self.get_user(user_id)

    
    def delete_user(self, user_id):
        self.user_repo.delete(user_id)

    # AMENITY
    def create_amenity(self, amenity_data):
        if not isinstance(amenity_data.get('name'), str) or not amenity_data.get('name').strip():
            raise ValueError("Amenity name must be a non-empty string.")
        
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity


    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        amenities = self.amenity_repo.get_all()
        return [a.to_dict() for a in amenities]

    def update_amenity(self, amenity_id, data):
        return self.amenity_repo.update(amenity_id, data)

    def delete_amenity(self, amenity_id):
        self.amenity_repo.delete(amenity_id)

    # PLACE
    def create_place(self, place_data):
        user = self.get_user(place_data['owner_id'])
        if not user:
            raise ValueError("Invalid owner_id")

        place_data.pop("owner_id", None)
        amenities_payload = place_data.pop("amenities", None)
        place = Place(owner=user, **place_data)
        self.place_repo.add(place)
        user.add_place(place)

        if amenities_payload:
            for item in amenities_payload:
                amenity = self.get_amenity(item["id"])
                if not amenity:
                    raise KeyError("Invalid amenity id")
                place.add_amenity(amenity)

        db.session.commit()

        return place


    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        place = self.place_repo.get(place_id)
        if not place:
            raise KeyError("Place not found")
        if not place.owner.is_admin and str(place.owner.id) != str(place_data['owner_id']):
            raise PermissionError("Unauthorized action")
        
        for protec_fields in ("owner", "owner_id", "id"):
            place_data.pop(protec_fields, None)

        return self.place_repo.update(place_id, place_data)

    def delete_place(self, place_id):
        self.place_repo.delete(place_id)

    # REVIEWS
    def create_review(self, review_data):
        user = self.user_repo.get(review_data['user_id'])
        if not user:
            raise ValueError('User not found')
        
        place = self.place_repo.get(review_data['place_id'])
        if not place:
            raise ValueError('Place not found')
        if place.owner.id == user.id:
            raise ValueError("You cannot review your own place")
        
        if self.user_already_reviewed_place(self, user.id, place.id):
            raise ValueError("You have already reviewed this place")
    
        review = Review(**review_data)
        self.review_repo.add(review)
        user.add_review(review)
        place.add_review(review)
        return review
        
    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError('Place not found')
        return place.reviews

    def update_review(self, review_id, review_data):
        review = self.review_repo.get(review_id)
        if not review:
            raise KeyError("Review not found")
        
        if not review.user.is_admin and str(review.user.id) != str(review_data['user']):
            raise PermissionError("Unauthorized action")
        review_data.pop("user_id", None)
        review_data.pop("place_id", None)

        return self.review_repo.update(review_id, review_data)

    def delete_review(self, review_id):
        review = self.review_repo.get(review_id)
        if not review:
            raise KeyError("Review not found")
        if not review.user.is_admin and str(review.user.id) != str(review['user']):
            raise PermissionError("Unauthorized action")
        user = self.user_repo.get(review.user.id)
        place = self.place_repo.get(review.place.id)

        user.delete_review(review)
        place.delete_review(review)
        self.review_repo.delete(review_id)
        
        db.session.delete(review)
        db.session.commit()

    def user_already_reviewed(self, user_id: str, place_id: str) -> bool:
        return self.review_repo.get_by_user_and_place(user_id, place_id) is not None
