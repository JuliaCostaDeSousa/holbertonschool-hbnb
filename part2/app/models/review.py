from .basemodel import BaseModel
from app.extensions import db
from sqlalchemy.orm import validates

class Review(BaseModel):
    __tablename__ = 'reviews'
	
    text = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    place = db.relationship('Place', backref=db.backref('reviews'), lazy=True)
    user = db.relationship('User', backref=db.backref('reviews'), lazy=True)


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
