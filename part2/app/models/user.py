from .basemodel import BaseModel
import re
from app.extensions import db, bcrypt
from sqlalchemy.orm import validates
from app.extensions import db

class User(BaseModel):
    __tablename__ = 'users'

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    _password = db.Column("password", db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    @validates('first_name')
    def validates_first_name(self, key, value):
        if not isinstance(value, str):
            raise TypeError("{} must be a string".format(key))
        value = value.strip()
        if value == "":
            raise ValueError("{} must not be empty".format(key))
        return value

    @validates('last_name')
    def validates_last_name(self, key, value):
        if not isinstance(value, str):
            raise TypeError("{} must be a string".format(key))
        value = value.strip()
        if value == "":
            raise ValueError("{} must not be empty".format(key))
        return value

    @validates('email')
    def validates_email(self, key, value):
        if not isinstance(value, str):
            raise TypeError("{} must be a string".format(key))
        value = value.strip()
        if value == "":
            raise ValueError("{} must not be empty".format(key))
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email format")
        return value

    @validates('is_admin')
    def validates_is_admin(self, key, value):
        if not isinstance(value, bool):
            raise TypeError("{} must be a boolean".format(key))
        return value

    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, plaintext):
        if not plaintext:
            raise ValueError("Password must not be empty.")
        self._password = bcrypt.generate_password_hash(plaintext).decode('utf-8')

    def add_place(self, place):
        """Add a place."""
        self.places.append(place)

    def add_review(self, review):
        """Add an review to the place."""
        self.reviews.append(review)

    def delete_review(self, review):
        """Delete a review to the place."""
        self.reviews.remove(review)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
        }

    def hash_password(self, password):
        """Hashes the password before storing it."""
        self._password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        return bcrypt.check_password_hash(self._password, password)
