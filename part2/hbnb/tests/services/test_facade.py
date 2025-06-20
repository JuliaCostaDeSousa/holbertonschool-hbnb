import pytest
from app.services.facade import HBnBFacade
from app.models.user import User
from app.models.place import Place
from app.models.amenity import Amenity
from app.models.review import Review

@pytest.fixture
def facade():
    return HBnBFacade()

@pytest.fixture
def user_and_place(facade):
    user = User(first_name="Alice", last_name="Doe", email="alice@example.com")
    place = Place(title="Villa", description="Nice", price=100.0, latitude=45.0, longitude=5.0, owner=user)
    facade.user_repo.add(user)
    facade.place_repo.add(place)
    return user, place

# Amenity tests

def test_facade_create_amenity(facade):
    amenity = facade.create_amenity({"name": "Wi-Fi"})
    assert amenity["name"] == "Wi-Fi"

def test_facade_get_amenity_not_found(facade):
    with pytest.raises(ValueError, match="Amenity not found"):
        facade.get_amenity("nonexistent-id")

def test_facade_update_amenity(facade):
    created = facade.create_amenity({"name": "Sauna"})
    updated = facade.update_amenity(created["id"], {"name": "Jacuzzi"})
    assert updated["name"] == "Jacuzzi"

def test_get_amenity_invalid_id(facade):
    with pytest.raises(ValueError):
        facade.get_amenity("non-existent-id")

def test_update_amenity_invalid_id(facade):
    with pytest.raises(ValueError):
        facade.update_amenity("wrong-id", {"name": "Pool"})

# Review tests

def test_facade_create_review(facade, user_and_place):
    user, place = user_and_place
    review = facade.create_review({
        "text": "Great stay!",
        "rating": 5,
        "user_id": user.id,
        "place_id": place.id
    })
    assert review["text"] == "Great stay!"

def test_facade_create_review_invalid_user(facade, user_and_place):
    _, place = user_and_place
    with pytest.raises(ValueError, match="User not found"):
        facade.create_review({
            "text": "Nice",
            "rating": 4,
            "user_id": "invalid",
            "place_id": place.id
        })

def test_facade_update_review(facade, user_and_place):
    user, place = user_and_place
    review = facade.create_review({
        "text": "Good",
        "rating": 3,
        "user_id": user.id,
        "place_id": place.id
    })
    updated = facade.update_review(review["id"], {
        "text": "Excellent",
        "rating": 5,
        "user_id": user.id,
        "place_id": place.id
    })
    assert updated["text"] == "Excellent"
    assert updated["rating"] == 5

def test_facade_delete_review(facade, user_and_place):
    user, place = user_and_place
    review = facade.create_review({
        "text": "To be deleted",
        "rating": 2,
        "user_id": user.id,
        "place_id": place.id
    })
    facade.delete_review(review["id"])
    with pytest.raises(ValueError, match="Review not found"):
        facade.get_review(review["id"])

def test_create_review_invalid_user(facade, user_and_place):
    _, place = user_and_place
    with pytest.raises(ValueError):
        facade.create_review({
            "text": "Good", "rating": 5,
            "user_id": "wrong-id", "place_id": place.id
        })

def test_create_review_invalid_place(facade, user_and_place):
    user, _ = user_and_place
    with pytest.raises(ValueError):
        facade.create_review({
            "text": "Good", "rating": 5,
            "user_id": user.id, "place_id": "wrong-id"
        })

def test_get_review_not_found(facade):
    with pytest.raises(ValueError):
        facade.get_review("missing-id")

def test_update_review_not_found(facade):
    with pytest.raises(ValueError):
        facade.update_review("no-id", {
            "text": "Edit", "rating": 3,
            "user_id": "u1", "place_id": "p1"
        })

def test_delete_review_not_found(facade):
    with pytest.raises(ValueError):
        facade.delete_review("not-found-id")

def test_get_reviews_by_place_not_found(facade):
    with pytest.raises(ValueError):
        facade.get_reviews_by_place("bad-place-id")
