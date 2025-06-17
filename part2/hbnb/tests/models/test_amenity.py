import pytest
from app.models.amenity import Amenity

def test_amenity_creation_valid():
    a = Amenity(name="Wi-Fi")
    assert a.name == "Wi-Fi"
    assert isinstance(a.id, str)
    assert a.created_at is not None
    assert a.updated_at is not None

def test_amenity_invalid_type():
    with pytest.raises(TypeError):
        Amenity(name=123)

def test_amenity_name_too_long():
    with pytest.raises(ValueError):
        Amenity(name="x" * 51)

def test_amenity_empty_name():
    with pytest.raises(ValueError):
        Amenity(name="   ")

def test_amenity_setter_updates_timestamp():
    a = Amenity(name="Wi-Fi")
    before = a.updated_at
    a.name = "Parking"
    assert a.name == "Parking"
    assert a.updated_at > before
