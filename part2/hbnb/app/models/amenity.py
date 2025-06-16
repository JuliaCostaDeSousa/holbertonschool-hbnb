from app.models.base_model import BaseModel

class Amenity(BaseModel):
    def __init__(self, name):
        super().__init__()
        self.name = name
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("name must be a string")
        if len(value) > 50:
            raise ValueError("name must be at most 50 characters long")
        if not value.strip():
            raise ValueError("name is required and cannot be empty")
        self._name = value
        self.save()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }
