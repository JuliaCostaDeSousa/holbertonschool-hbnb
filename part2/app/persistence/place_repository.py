from app.models.place import Place
from app.persistence.repository import SQLAlchemyRepository
from app.extensions import db
from app.models.review import Review

class PlaceRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Place)
