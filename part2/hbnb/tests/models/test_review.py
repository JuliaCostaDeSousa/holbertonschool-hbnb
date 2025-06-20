import pytest
from app.models.review import Review
from app.models.user import User
from app.models.place import Place
from app.services import facade

@pytest.fixture
def setup_valid_user_and_place():
    user = User(first_name="Alice", last_name="Doe", email="alice@example.com")
    place = Place(title="Chalet", description="Cozy", price=120.0, latitude=45.0, longitude=5.0, owner=user)
    facade.user_repo.add(user)
    facade.place_repo.add(place)
    return user, place

def test_review_creation_valid(setup_valid_user_and_place):
    user, place = setup_valid_user_and_place
    r = Review(text="Great place!", rating=5, place=place, user=user)
    assert r.text == "Great place!"
    assert r.rating == 5
    assert r.place.id == place.id
    assert r.user.id == user.id
    assert r.created_at is not None
    assert r.updated_at is not None

def test_review_invalid_text_type(setup_valid_user_and_place):
    user, place = setup_valid_user_and_place
    with pytest.raises(TypeError):
        Review(text=123, rating=4, place=place, user=user)

def test_review_empty_text(setup_valid_user_and_place):
    user, place = setup_valid_user_and_place
    with pytest.raises(ValueError):
        Review(text="   ", rating=4, place=place, user=user)

def test_review_invalid_rating_type(setup_valid_user_and_place):
    user, place = setup_valid_user_and_place
    with pytest.raises(TypeError):
        Review(text="Nice", rating="5", place=place, user=user)

def test_review_rating_out_of_bounds(setup_valid_user_and_place):
    user, place = setup_valid_user_and_place
    with pytest.raises(ValueError):
        Review(text="Okay", rating=6, place=place, user=user)

def test_review_invalid_place(setup_valid_user_and_place):
    user, _ = setup_valid_user_and_place
    fake_place = Place(title="Ghost", description="None", price=10.0, latitude=0, longitude=0, owner=user)
    with pytest.raises(ValueError):
        Review(text="Nope", rating=2, place=fake_place, user=user)

def test_review_invalid_user(setup_valid_user_and_place):
    _, place = setup_valid_user_and_place
    fake_user = "not_a_user"
    with pytest.raises(ValueError):
        Review(text="Hmmm", rating=3, place=place, user=fake_user)

def test_review_setter_updates_timestamp(setup_valid_user_and_place):
    user, place = setup_valid_user_and_place
    r = Review(text="Great place!", rating=5, place=place, user=user)
    before = r.updated_at
    r.text = "Amazing!"
    assert r.text == "Amazing!"
    assert r.updated_at > before
