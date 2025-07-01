#!/usr/bin/python3

from app.models.base_model import BaseModel
from app.services import facade


class Place(BaseModel):
    def __init__(self, title, price, latitude, longitude, owner_id, description=""):
        super().__init__()

        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner_id = owner_id

        self.reviews = []
        self.amenities = []

        if not isinstance(self.title, str):
            raise TypeError("Title must be a string")
        if not self.title or len(self.title) > 100:
            raise ValueError("Title is required and must be at most 100 characters")

        if not isinstance(self.description, str):
            raise TypeError("Description must be a string")
        if self.description == "":
            raise ValueError("Description is required")

        if not isinstance(self.price, float):
            raise TypeError("Price must be a float number")
        if self.price < 0:
            raise ValueError("Price must be a positive number")

        if not isinstance(self.latitude, float):
            raise TypeError("Latitude must be a float")
        if not (-90.0 <= self.latitude <= 90.0):
            raise ValueError("Latitude must be between -90.0 and 90.0")

        if not isinstance(self.longitude, float):
            raise TypeError("Longitude must be a float")
        if not (-180.0 <= self.longitude <= 180.0):
            raise ValueError("Longitude must be between -180.0 and 180.0")

        if not isinstance(self.owner_id, str):
            raise TypeError("Owner must be an instance of User")

    def add_review(self, review):
        self.reviews.append(review)

    def delete_review(self, review):
        if review in self.reviews:
            self.reviews.remove(review)

    def add_amenity(self, amenity):
        self.amenities.append(amenity)

    def delete_amenity(self, amenity):
        if amenity in self.amenities:
            self.amenities.remove(amenity)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "owner_id": self.owner_id,
            "amenities": [facade.get_amenity(a).to_dict() for a in self.amenities] #parcours les ID a = id
        }
