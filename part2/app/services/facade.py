from app.persistence.user_repository import UserRepository
from app.persistence.place_repository import PlaceRepository
from app.persistence.amenity_repository import AmenityRepository
from app.persistence.review_repository import ReviewRepository
from app.extensions import db

from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review

class HBnBFacade:
    def __init__(self):
        self.user_repo = UserRepository()
        self.amenity_repo = AmenityRepository()
        self.place_repo = PlaceRepository()
        self.review_repo = ReviewRepository()

    # USER
    def create_user(self, user_data):
        password = user_data.pop("password")
        user = User(**user_data)
        user.hash_password(password)
        self.user_repo.add(user)
        return user
    
    def get_users(self):
        return self.user_repo.get_all()

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)
    
    def update_user(self, user_id, user_data):
        user = self.user_repo.get(user_id)
        if not user:
            return None
        if "password" in user_data:
            user.hash_password(user_data.pop("password"))
        for key, value in user_data.items():
            setattr(user, key, value)
            db.session.commit()
        return user
    
    def delete_user(self, user_id):
        self.user_repo.delete(user_id)

    # AMENITY
    def create_amenity(self, amenity_data):
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
        title = place_data.get("title", "")
        if not isinstance(title, str) or title.strip() == "":
            raise ValueError("title must not be empty")

        price = place_data.get("price")
        if not isinstance(price, (int, float)):
            raise ValueError("price must be a number")

        latitude = place_data.get("latitude")
        if not isinstance(latitude, (int, float)):
            raise ValueError("latitude must be a number")

        longitude = place_data.get("longitude")
        if not isinstance(longitude, (int, float)):
            raise ValueError("longitude must be a number")

        owner_id = place_data.get("owner_id", "")
        if not isinstance(owner_id, str) or owner_id.strip() == "":
            raise ValueError("owner_id is required and must not be empty")

        del place_data['owner_id']
        user = self.user_repo.get_by_attribute('id', owner_id)
        if not user:
            raise ValueError("Invalid owner_id")

        place_data['owner'] = user

        amenities_data = place_data.pop("amenities", [])
        amenities_obj = []
        for a in amenities_data:
            amenity = self.get_amenity(a["id"])
            if not amenity:
                raise ValueError("Invalid amenity id")
            amenities_obj.append(amenity)

        place = Place(**place_data)
        self.place_repo.add(place)
        user.add_place(place)
        for amenity in amenities_obj:
            place.add_amenity(amenity)

        return place


    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        return self.place_repo.update(place_id, place_data)

    def user_already_reviewed_place(self, user_id, place_id):
        return self.place_repo.already_reviewed_place(user_id, place_id)
    
    def delete_place(self, place_id):
        self.place_repo.delete(place_id)

    # REVIEWS
    def create_review(self, review_data):
        user = self.user_repo.get(review_data['user_id'])
        if not user:
            raise ValueError('Invalid input data')
        del review_data['user_id']
        review_data['user'] = user
        
        place = self.place_repo.get(review_data['place_id'])
        if not place:
            raise ValueError('Invalid input data')
        del review_data['place_id']
        review_data['place'] = place

        rating = review_data.get("rating")
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            raise ValueError("Rating must be an integer between 1 and 5")
        
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
        return self.review_repo.update(review_id, review_data)

    def delete_review(self, review_id):
        review = self.review_repo.get(review_id)
        
        user = self.user_repo.get(review.user.id)
        place = self.place_repo.get(review.place.id)

        user.delete_review(review)
        place.delete_review(review)
        self.review_repo.delete(review_id)
