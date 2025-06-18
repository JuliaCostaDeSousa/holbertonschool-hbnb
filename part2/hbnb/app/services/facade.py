from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity

class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    def create_amenity(self, amenity_data):
        new_amenity = Amenity(name=amenity_data['name'])
        self.amenity_repo.add(new_amenity)
        return new_amenity.to_dict()
    
    def get_amenity(self, amenity_id):
        amenity = self.amenity_repo.get_by_attribute('id', amenity_id)
        if amenity is None:
            raise ValueError("Amenity not found")
        return amenity.to_dict()

    def get_all_amenities(self):
        amenities = self.amenity_repo.get_all()
        return [amenity.to_dict() for amenity in amenities]

    def update_amenity(self, amenity_id, amenity_data):
        amenity = self.amenity_repo.get_by_attribute('id', amenity_id)
        if amenity is None:
            raise ValueError("Amenity not found")
        
        self.amenity_repo.update(amenity_id, amenity_data)
        return self.amenity_repo.get(amenity_id).to_dict()


    def create_review(self, review_data):
        user = self.user_repo.get_by_attribute('id', review_data['user_id'])
        if user is None:
            raise ValueError("User not found")

        place = self.place_repo.get_by_attribute('id', review_data['place_id'])
        if place is None:
            raise ValueError("Place not found")
        
        new_review = Review(text=review_data['text'],
                            rating=review_data['rating'],
                            place=place,
                            user=user)
        
        self.review_repo.add(new_review)
        return new_review.to_dict()

    def get_review(self, review_id):
        review = self.review_repo.get_by_attribute('id', review_id)
        if review is None:
            raise ValueError("Review not found")
        return review.to_dict()

    def get_all_reviews(self):
        reviews = self.review_repo.get_all()
        return [review.to_dict() for review in reviews]

    def get_reviews_by_place(self, place_id):
        place = self.place_repo.get_by_attribute('id', place_id)
        if place is None:
            raise ValueError("Place not found")

        all_reviews = self.review_repo.get_all()
        place_reviews = [review.to_dict() for review in all_reviews if review.place.id == place_id]
        return place_reviews

    def update_review(self, review_id, review_data):
        review = self.review_repo.get_by_attribute('id', review_id)
        if review is None:
            raise ValueError("Review not found")
        
        user = self.user_repo.get_by_attribute('id', review_data['user_id'])
        if user is None:
            raise ValueError("User not found")

        place = self.place_repo.get_by_attribute('id', review_data['place_id'])
        if place is None:
            raise ValueError("Place not found")
        
        update_data = {
            'text': review_data['text'],
            'rating': review_data['rating'],
            'place': place,
            'user': user
            }
        
        self.review_repo.update(review_id, update_data)
        return self.review_repo.get(review_id).to_dict()

    def delete_review(self, review_id):
        review = self.review_repo.get_by_attribute('id', review_id)
        if review is None:
            raise ValueError("Review not found")
        
        self.review_repo.delete(review_id)
