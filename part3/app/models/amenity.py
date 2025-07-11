from .basemodel import BaseModel
from app.extensions import db
from sqlalchemy.orm import validates


class Amenity(BaseModel):
    __tablename__ = 'amenities'

    name = db.Column(db.String(50), nullable=False, unique=True)

    @validates('name')
    def validates_name(self, key, value):
        if not isinstance(value, str):
            raise TypeError("{} must be a string".format(key))
        value = value.strip()
        if value == "":
            raise ValueError("{} must not be empty".format(key))
        super().is_max_length('Name', value, 50)
        return value

    def update(self, data):
        return super().update(data)
	
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
