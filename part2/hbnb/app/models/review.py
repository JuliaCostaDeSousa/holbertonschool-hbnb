from app.models.base_model import BaseModel
from app.models.place import Place
from app.models.user import User
from app.services import facade


class Review(BaseModel):
    def __init__(self, text, rating, user, place):
        super().__init__()
        self.text = text
        self.rating = rating
        self.place = place
        self.user = user
    
    @property
    def text(self):
        return self.__text
    
    @text.setter
    def text(self, value):
        if not isinstance(value, str):
            raise TypeError("text must be a string")
        if not value.strip():
            raise ValueError("text is required and cannot be empty")
        self.__text = value
        self.save()

    @property
    def rating(self):
        return self.__rating

    @rating.setter
    def rating(self, value):
        if not isinstance(value, int):
            raise TypeError("rating must be an integer")
        if not (1 <= value <= 5):
            raise ValueError("rating must be between 1 and 5")
        self.__rating = value
        self.save()

    @property
    def place(self):
        return self.__place

    @place.setter
    def place(self, value):
        if not isinstance(value, Place):
            raise ValueError("place must be a place instance")
        self.__place = value
        self.save()

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, value):
        if not isinstance(value, User):
            raise ValueError("user must be a user instance")
        self.__user = value
        self.save()

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "rating": self.rating,
            "place_id": self.place.id,
            "user_id": self.user.id
        }
