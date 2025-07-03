from .basemodel import BaseModel
from .place import Place
from .user import User
from app.extensions import db
from sqlalchemy.orm import validates

class Review(BaseModel):
    __tablename__ = 'reviews'
	
    id = db.Column(db.String(36), primary_key=True, nullable=False, unique=True)
    text = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

	
    @validates('text')
    def validates_text(self, key, value):
        if not value:
            raise ValueError("{} cannot be empty".format(key))
        if not isinstance(value, str):
            raise TypeError("{} must be a string".format(key))
        return value.strip()

    @validates('rating')
    def validates_rating(self, key, value):
        if not isinstance(value, int):
            raise TypeError("{} must be an integer".format(key))
        super().is_between('Rating', value, 1, 6)
        return value

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'rating': self.rating,
            'place_id': self.place.id,
            'user_id': self.user.id
        }
