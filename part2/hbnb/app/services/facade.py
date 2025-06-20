from app.persistence.repository import InMemoryRepository

class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    def create_amenity(self, amenity_data):
        from app.models.amenity import Amenity
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
        from app.models.review import Review
        from app.models.place import Place
        from app.models.user import User

        user = self.user_repo.get_by_attribute('id', review_data['user_id'])
        if user is None:
            raise ValueError("User not found")

        place = self.place_repo.get_by_attribute('id', review_data['place_id'])
        if place is None:
            raise ValueError("Place not found")

        new_review = Review(
            text=review_data['text'],
            rating=review_data['rating'],
            place=place,
            user=user
        )

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
        from app.models.place import Place
        from app.models.user import User

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

    def create_user(self, user_data):
        from app.models.user import User
        user = User(**user_data)
        self.user_repo.add(user)
        return user.to_dict()

    def get_user(self, user_id):
        user = self.user_repo.get(user_id)
        if user is None:
            raise ValueError("User not found")
        return user.to_dict()

    def get_user_by_email(self, email):
        user = self.user_repo.get_by_attribute("email", email)
        if user is None:
            raise ValueError("User not found")
        return user.to_dict()

    def get_all_users(self):
        return [u.to_dict() for u in self.user_repo.get_all()]

    def create_place(self, place_data):
        from app.models.place import Place
        amenity_ids = place_data.pop("amenities", [])
        place = Place(**place_data)
        for amenity_id in amenity_ids:
            amenity = self.amenity_repo.get(amenity_id)
            if amenity:
                place.amenities.append(amenity)
        self.place_repo.add(place)
        return place.to_dict()

    def get_place(self, place_id):
        place = self.place_repo.get(place_id)
        if place is None:
            raise ValueError("Place not found")
        return place.to_dict()

    def get_all_places(self):
        return [p.to_dict() for p in self.place_repo.get_all()]

    def update_place(self, place_id, place_data):
        self.place_repo.update(place_id, place_data)
        return self.place_repo.get(place_id).to_dict()

    def delete_place(self, place_id):
        self.place_repo.delete(place_id)
