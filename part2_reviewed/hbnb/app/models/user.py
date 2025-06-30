#!/usr/bin/python3

from app.models.base_model import BaseModel
import re


class User(BaseModel):
    def __init__(self, first_name, last_name, email, is_admin=False):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.places = []

        if not isinstance(first_name, str):
            raise TypeError("First name is required")
        if first_name == "" or len(first_name) > 50:
            raise ValueError("First name is required and must be at most 50 characters")

        if not isinstance(last_name, str):
            raise TypeError("Last name is required")
        if last_name == "" or len(last_name) > 50:
            raise ValueError("Last name is required and must be at most 50 characters")
        
        if not isinstance(is_admin, bool):
            raise TypeError("Is_admin must be boolean type")

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, new_email):
        if not isinstance(new_email, str):
            raise TypeError("email must be strings")
        self.__email = self.verified_email(new_email)

    def __str__(self):
        return f"first_name: {self.first_name}\n last_name: {self.last_name}\n email: {self.email}"

    def add_place(self, place):
        self.places.append(place)

    def delete_place(self, place):
        self.places.remove(place)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
        }

    @staticmethod
    def verified_email(email):
        extensions = ['com', 'fr', 'net', 'org']
        pattern = r'^[^@\s]+@[^@\s]+\.(%s)$' % '|'.join(extensions)
        if re.match(pattern, email, re.IGNORECASE):
            return email
        raise ValueError("Invalid email format")
