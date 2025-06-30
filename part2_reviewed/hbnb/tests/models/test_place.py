import pytest
from app.models.place import Place
from app.models.user import User
from app.models.amenity import Amenity
from app.models.review import Review

@pytest.fixture
def user():
    return User(first_name="Alice", last_name="Wonders", email="alice@example.com")

@pytest.fixture
def place(user):
    return Place(
        title="Beach House",
        description="Beautiful ocean view",
        price=200.0,
        latitude=25.0,
        longitude=55.0,
        owner=user
    )

def test_valid_place_creation(place):
    assert place.title == "Beach House"
    assert place.owner.email == "alice@example.com"
    assert place.latitude == 25.0
    assert place.longitude == 55.0
    assert isinstance(place.reviews, list)
    assert isinstance(place.amenities, list)

@pytest.mark.parametrize("field,value,error", [
    ("title", 123, TypeError),
    ("title", "", ValueError),
    ("description", 456, TypeError),
    ("description", "", ValueError),
    ("price", "100", TypeError),
    ("price", -10.0, ValueError),
    ("latitude", "45N", TypeError),
    ("latitude", -200.0, ValueError),
    ("longitude", [], TypeError),
    ("longitude", -300.0, ValueError),
    ("owner", "not_user", TypeError),
])
def test_invalid_place_inputs(field, value, error, user):
    kwargs = {
        "title": "Valid",
        "description": "Valid desc",
        "price": 100.0,
        "latitude": 0.0,
        "longitude": 0.0,
        "owner": user
    }
    kwargs[field] = value
    with pytest.raises(error):
        Place(**kwargs)

def test_add_and_remove_review(place):
    review = Review(text="Cool spot", rating=5, user=place.owner, place=place)
    place.add_review(review)
    assert review in place.reviews
    place.delete_review(review)
    assert review not in place.reviews

def test_add_and_remove_amenity(place):
    amenity = Amenity(name="Pool")
    place.add_amenity(amenity)
    assert amenity in place.amenities
    place.delete_amenity(amenity)
    assert amenity not in place.amenities
