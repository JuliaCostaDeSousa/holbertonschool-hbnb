from flask.testing import FlaskClient
import pytest
from app.services import facade

@pytest.fixture
def setup_user_and_amenities():
    from app.models.user import User
    from app.models.amenity import Amenity
    import uuid

    user = User(first_name="Alice", last_name="Wonders", email=f"alice_{uuid.uuid4()}@example.com")
    amenity1 = Amenity(name="WiFi")
    amenity2 = Amenity(name="Pool")

    facade.user_repo.add(user)
    facade.amenity_repo.add(amenity1)
    facade.amenity_repo.add(amenity2)

    return user, [amenity1, amenity2]


def test_create_place_success(client: FlaskClient, setup_user_and_amenities):
    user, amenities = setup_user_and_amenities
    place_data = {
        "title": "Sunny Villa",
        "description": "A nice place by the beach",
        "price": 150.0,
        "latitude": 36.5,
        "longitude": -5.9,
        "owner_id": user.id,
        "amenities": [a.id for a in amenities]
    }

    response = client.post("/api/v1/places/", json=place_data)
    print(response.json)
    assert response.status_code == 201
    data = response.json
    assert data["title"] == "Sunny Villa"
    assert data["owner"]["email"] == user.email
    assert len(data["amenities"]) == 2


def test_get_all_places(client: FlaskClient, setup_user_and_amenities):
    user, amenities = setup_user_and_amenities
    client.post("/api/v1/places/", json={
        "title": "Mountain Cabin",
        "description": "Great view",
        "price": 90.0,
        "latitude": 44.1,
        "longitude": 6.5,
        "owner_id": user.id,
        "amenities": [a.id for a in amenities]
    })

    response = client.get("/api/v1/places/")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) >= 1


def test_get_place_by_id(client: FlaskClient, setup_user_and_amenities):
    user, amenities = setup_user_and_amenities
    resp = client.post("/api/v1/places/", json={
        "title": "Forest Hut",
        "description": "Secluded spot",
        "price": 75.0,
        "latitude": 47.1,
        "longitude": 3.5,
        "owner_id": user.id,
        "amenities": [a.id for a in amenities]
    })
    place_id = resp.json["id"]

    get_resp = client.get(f"/api/v1/places/{place_id}")
    assert get_resp.status_code == 200
    assert get_resp.json["id"] == place_id


def test_update_place_success(client: FlaskClient, setup_user_and_amenities):
    user, amenities = setup_user_and_amenities
    post_resp = client.post("/api/v1/places/", json={
        "title": "Tiny Home",
        "description": "Cozy",
        "price": 50.0,
        "latitude": 50.0,
        "longitude": 2.0,
        "owner_id": user.id,
        "amenities": [a.id for a in amenities]
    })
    place_id = post_resp.json["id"]

    update_resp = client.put(f"/api/v1/places/{place_id}", json={
        "title": "Updated Home",
        "description": "Updated description",
        "price": 60.0,
        "latitude": 50.0,
        "longitude": 2.0,
        "owner_id": user.id,
        "amenities": [a.id for a in amenities]
    })
    assert update_resp.status_code == 200
    assert update_resp.json["title"] == "Updated Home"


def test_get_place_not_found(client: FlaskClient):
    response = client.get("/api/v1/places/nonexistent-id")
    assert response.status_code == 404
    assert "error" in response.json


def test_update_place_not_found(client: FlaskClient):
    response = client.put("/api/v1/places/nonexistent-id", json={
        "title": "Nowhere",
        "description": "This should fail",
        "price": 99.0,
        "latitude": 0.0,
        "longitude": 0.0,
        "owner_id": "fake-owner-id",
        "amenities": []
    })
    assert response.status_code == 404
    assert "error" in response.json
