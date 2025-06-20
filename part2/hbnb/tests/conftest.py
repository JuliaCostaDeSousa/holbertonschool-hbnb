# conftest.py
import pytest
from app import create_app
from app.models.user import User
from app.models.place import Place
from app.models.amenity import Amenity
from app.services import facade
import uuid

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def setup_user_place():
    user = User(first_name="John", last_name="Doe", email="john@example.com")
    place = Place(
        title="Test Place",
        description="Nice place",
        price=100.0,
        latitude=48.85,
        longitude=2.35,
        owner=user
    )

    facade.user_repo.add(user)
    facade.place_repo.add(place)

    return user, place

@pytest.fixture
def user_data():
    return {
        "first_name": "Alice",
        "last_name": "Doe",
        "email": f"alice_{uuid.uuid4()}@example.com"
    }

@pytest.fixture
def setup_user_and_amenities():
    user = User(first_name="Bob", last_name="Builder", email=f"bob_{uuid.uuid4()}@example.com")
    amenity1 = Amenity(name="Wi-Fi")
    amenity2 = Amenity(name="Pool")

    facade.user_repo.add(user)
    print("Added user with ID:", user.id)
    print("user found in repo:", facade.user_repo.get(user.id))
    facade.amenity_repo.add(amenity1)
    facade.amenity_repo.add(amenity2)

    assert facade.user_repo.get(user.id) is not None
    return user, [amenity1, amenity2]

@pytest.fixture
def facade():
    from app.services import facade as _facade
    return _facade