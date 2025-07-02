from app.models.user import User
from app.persistence.repository import SQLAlchemyRepository

class UserRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(User)

    def get_user_by_email(self, email):
        return self.model.query.filter_by(email=email).first()
    
    def reset_password(self, user, new_password):
        if not isinstance(user, User):
            raise TypeError("Expected a User instance")

        if not new_password or not new_password.strip():
            raise ValueError("Password cannot be empty")

        user.hash_password(new_password)
        self.update(user)
