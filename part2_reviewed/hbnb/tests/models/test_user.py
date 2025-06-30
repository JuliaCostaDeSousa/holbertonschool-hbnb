import pytest
from app.models.user import User
from app.models.place import Place


@pytest.fixture
def user():
    return User(first_name="John", last_name="Doe", email="john@example.com")


def test_user_creation(user):
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john@example.com"
    assert user.is_admin is False
    assert isinstance(user.places, list)


@pytest.mark.parametrize("field,value,error", [
    ("first_name", 123, TypeError),
    ("first_name", "", ValueError),
    ("first_name", "A" * 51, ValueError),
    ("last_name", None, TypeError),
    ("last_name", "", ValueError),
    ("last_name", "B" * 51, ValueError),
    ("email", 999, TypeError),
    ("email", "invalidemail", ValueError),
    ("email", "test@invalid.xyz", ValueError),
    ("is_admin", "yes", TypeError),
])
def test_invalid_user_inputs(field, value, error):
    kwargs = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "is_admin": False
    }
    kwargs[field] = value
    with pytest.raises(error):
        User(**kwargs)


def test_user_email_validation():
    user = User("John", "Doe", "john@example.com")
    with pytest.raises(ValueError):
        user.email = "john@site.invalid"
    with pytest.raises(TypeError):
        user.email = 123


def test_add_and_remove_place(user):
    place = Place("Villa", 100.0, 40.0, 2.0, user, description="Nice place")
    user.add_place(place)
    assert place in user.places
    user.delete_place(place)
    assert place not in user.places


def test_user_to_dict(user):
    data = user.to_dict()
    assert data["id"] == user.id
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john@example.com"


def test_user_str(user):
    string = str(user)
    assert "first_name: John" in string
    assert "last_name: Doe" in string
    assert "email: john@example.com" in string
