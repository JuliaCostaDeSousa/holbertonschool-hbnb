# tests/api/test_reviews_api.py

import pytest
from app import create_app
from flask.testing import FlaskClient
from app.models.user import User
from app.models.place import Place
from app.services.facade import HBnBFacade

facade = HBnBFacade()

# Create a Flask client in testing mode

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# --- Tests for Amenities API ---

@pytest.fixture
def setup_user_place():
    user = User(first_name="John", last_name="Smith", email="john@example.com")
    place = Place(title="Cabin", description="Nice cabin", price=100, latitude=45.0, longitude=5.0, owner=user)
    facade.user_repo.add(user)
    facade.place_repo.add(place)
    return user, place

def test_create_review_success(client: FlaskClient, setup_user_place):
    user, place = setup_user_place
    review_data = {
        "text": "Amazing stay!",
        "rating": 5,
        "user_id": user.id,
        "place_id": place.id
    }
    response = client.post('/api/v1/reviews/', json=review_data)
    assert response.status_code == 201
    assert "id" in response.json
    assert response.json["text"] == "Amazing stay!"

def test_create_review_missing_field(client: FlaskClient):
    response = client.post('/api/v1/reviews/', json={"text": "Good"})
    assert response.status_code == 400
    assert "error" in response.json

def test_create_review_invalid_rating_type(client: FlaskClient, setup_user_place):
    user, place = setup_user_place
    response = client.post('/api/v1/reviews/', json={
        "text": "Nice",
        "rating": "five",
        "user_id": user.id,
        "place_id": place.id
    })
    assert response.status_code == 400
    assert "must be an integer" in response.json["error"]

def test_get_all_reviews(client: FlaskClient, setup_user_place):
    user, place = setup_user_place
    client.post('/api/v1/reviews/', json={
        "text": "Nice!",
        "rating": 4,
        "user_id": user.id,
        "place_id": place.id
    })
    response = client.get('/api/v1/reviews/')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_review_by_id(client: FlaskClient, setup_user_place):
    user, place = setup_user_place
    post_resp = client.post('/api/v1/reviews/', json={
        "text": "Very clean",
        "rating": 5,
        "user_id": user.id,
        "place_id": place.id
    })
    review_id = post_resp.json["id"]
    get_resp = client.get(f'/api/v1/reviews/{review_id}')
    assert get_resp.status_code == 200
    assert get_resp.json["text"] == "Very clean"

def test_put_review_success(client: FlaskClient, setup_user_place):
    user, place = setup_user_place
    post_resp = client.post('/api/v1/reviews/', json={
        "text": "Good",
        "rating": 3,
        "user_id": user.id,
        "place_id": place.id
    })
    review_id = post_resp.json["id"]

    put_resp = client.put(f'/api/v1/reviews/{review_id}', json={
        "text": "Updated review",
        "rating": 4,
        "user_id": user.id,
        "place_id": place.id
    })
    assert put_resp.status_code == 200

    updated = client.get(f'/api/v1/reviews/{review_id}')
    assert updated.json["text"] == "Updated review"
    assert updated.json["rating"] == 4

def test_put_review_not_found(client: FlaskClient, setup_user_place):
    user, place = setup_user_place
    response = client.put('/api/v1/reviews/nonexistent-id', json={
        "text": "Test",
        "rating": 4,
        "user_id": user.id,
        "place_id": place.id
    })
    assert response.status_code == 404

def test_delete_review_success(client: FlaskClient, setup_user_place):
    user, place = setup_user_place
    post_resp = client.post('/api/v1/reviews/', json={
        "text": "To be deleted",
        "rating": 3,
        "user_id": user.id,
        "place_id": place.id
    })
    review_id = post_resp.json["id"]

    delete_resp = client.delete(f'/api/v1/reviews/{review_id}')
    assert delete_resp.status_code == 200

    get_resp = client.get(f'/api/v1/reviews/{review_id}')
    assert get_resp.status_code == 404

def test_get_reviews_by_place(client: FlaskClient, setup_user_place):
    user, place = setup_user_place
    client.post('/api/v1/reviews/', json={
        "text": "Place review",
        "rating": 5,
        "user_id": user.id,
        "place_id": place.id
    })
    resp = client.get(f'/api/v1/reviews/places/{place.id}/reviews')
    assert resp.status_code == 200
    assert isinstance(resp.json, list)
    assert any(r["place_id"] == place.id for r in resp.json)
