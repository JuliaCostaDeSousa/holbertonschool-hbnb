from app.models.base_model import BaseModel
from app.models.place import Place
from app.models.user import User


class Review(BaseModel):
    def __init__(self, text, rating, place, user):
        super().__init__()
        self.text = text
        self.rating = rating
        self.place = place
        self.user = user
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value):
        if not isinstance(value, str):
            raise TypeError("text must be a string")
        if not value.strip():
            raise ValueError("text is required and cannot be empty")
        self._text = value
        self.save()

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        if not isinstance(value, int):
            raise TypeError("rating must be an integer")
        if not (1 <= value <= 5):
            raise ValueError("rating must be between 1 and 5")
        self._rating = value
        self.save()

    @property
    def place(self):
        return self._place

    @place.setter
    def place(self, value):
        if not isinstance(value, Place):
            raise ValueError("place must be a place instance")
        self._place = value
        self.save()

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        if not isinstance(value, User):
            raise ValueError("user must be a user instance")
        self._user = value
        self.save()

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "rating": self.rating,
            "place_id": self.place.id,
            "user_id": self.user.id
        }
