from .basemodel import BaseModel
from app.extensions import db
from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint
from .associations import place_amenity


class Place(BaseModel):
    __tablename__ = 'places'

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String, nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    owner = db.relationship('User', backref=db.backref('places'), lazy=True)
    amenities = db.relationship('Amenity', secondary=place_amenity, lazy='subquery',
                           backref=db.backref('places', lazy=True))

    __table_args__ = (
        CheckConstraint('price > 0', name='price_positive'),
        CheckConstraint('latitude > -90 AND latitude < 90', name='latitude_range'),
        CheckConstraint('longitude > -180 AND longitude < 180', name='longitude_range'),
    )

    @validates('title')
    def validates_title(self, key, value):
        if not value:
            raise ValueError("{} cannot be empty".format(key))
        if not isinstance(value, str):
            raise TypeError("{} must be a string".format(key))
        super().is_max_length('title', value, 100)
        return value.strip()
    
    @validates('description')
    def validates_description(self, key, value):
        if value is not None:
            if not isinstance(value, str):
                raise TypeError("{} must be a string".format(key))
            if value.strip() == "":
                raise ValueError("{} cannot be empty".format(key))
            return value.strip()
        return None

    @validates('price')
    def validates_price(self, key, value):
        if not isinstance(value, (int, float)):
            raise TypeError("{} must be a number".format(key))
        if value <= 0:
            raise ValueError("{} must be positive.".format(key))
        return float(value)

    @validates('latitude')
    def validates_latitude(self, key, value):
        if not isinstance(value, (float, int)):
            raise TypeError("{} must be a number".format(key))
        super().is_between("{}".format(key), value, -90.0, 90.0)
        return float(value)
    
    @validates('longitude')
    def validates_longitude(self, key, value):
        if not isinstance(value, (int, float)):
            raise TypeError("{} must be a number".format(key))
        super().is_between("{}".format(key), value, -180, 180)
        return float(value)

    def add_review(self, review):
        """Add a review to the place."""
        self.reviews.append(review)
    
    def delete_review(self, review):
        """Add an amenity to the place."""
        self.reviews.remove(review)

    def add_amenity(self, amenity):
        """Add an amenity to the place."""
        self.amenities.append(amenity)
    
    def delete_amenity(self, amenity):
        """Delete an amenity to the place."""
        self.amenities.remove(amenity)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner_id': self.owner.id
        }
    
    def to_dict_list(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner': self.owner.to_dict(),
            'amenities': [amenity.to_dict() for amenity in self.amenities],
            'reviews': [review.to_dict() for review in self.reviews]
        }
