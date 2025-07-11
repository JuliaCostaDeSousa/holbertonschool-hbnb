from .basemodel import BaseModel
import re
from app.extensions import db, bcrypt
from sqlalchemy.orm import validates

class User(BaseModel):
    __tablename__ = 'users'

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    _password = db.Column("password", db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, *args, password=None, **kwargs):
        super().__init__(*args, **kwargs)
        if password:
            self.hash_password(password)

    @validates('first_name')
    def validates_first_name(self, key, value):
        if not isinstance(value, str):
            raise TypeError(f"{key} must be a string")
        value = value.strip()
        if not value:
            raise ValueError(f"{key} must not be empty")
        return value

    @validates('last_name')
    def validates_last_name(self, key, value):
        if not isinstance(value, str):
            raise TypeError(f"{key} must be a string")
        value = value.strip()
        if not value:
            raise ValueError(f"{key} must not be empty")
        return value

    @validates('email')
    def validates_email(self, key, value):
        if not isinstance(value, str):
            raise TypeError(f"{key} must be a string")
        value = value.strip()
        if not value:
            raise ValueError(f"{key} must not be empty")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email format")
        return value

    @validates('is_admin')
    def validates_is_admin(self, key, value):
        if not isinstance(value, bool):
            raise TypeError(f"{key} must be a boolean")
        return value

    def hash_password(self, password):
        if not isinstance(password, str):
            raise TypeError("Password must be a string")
        password = password.strip()
        if not password:
            raise ValueError("Password must not be empty")
        self._password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self._password, password)

    def add_place(self, place):
        self.places.append(place)

    def add_review(self, review):
        self.reviews.append(review)

    def delete_review(self, review):
        self.reviews.remove(review)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
        }
