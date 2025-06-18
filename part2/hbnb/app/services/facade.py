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
        return  self.amenity_repo.get(amenity_id).to_dict()
