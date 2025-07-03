from .basemodel import BaseModel
from app.extensions import db
from sqlalchemy.orm import validates


class Amenity(BaseModel):
    __tablename__ = 'amenities'

    id = db.Column(db.String(36), primary_key=True, nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)

    @validates('name')
    def validates_name(self, key, value):
        if not isinstance(value, str):
            raise TypeError("Name must be a string")
        if not value:
            raise ValueError("Name cannot be empty")
        super().is_max_length('Name', value, 50)
        return value.strip()

    def update(self, data):
        return super().update(data)
	
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
