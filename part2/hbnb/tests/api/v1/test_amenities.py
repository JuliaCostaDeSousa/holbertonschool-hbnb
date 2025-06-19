import pytest
from app import create_app
from flask.testing import FlaskClient

# Create a Flask client in testing mode

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# --- Tests for Amenities API ---

def test_create_amenity_success(client: FlaskClient):
    response = client.post('/api/v1/amenities/', json={'name': 'Wi-Fi'})
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['name'] == 'Wi-Fi'

def test_create_amenity_missing_name(client: FlaskClient):
    response = client.post('/api/v1/amenities/', json={})
    assert response.status_code == 400
    assert 'error' in response.json
    assert "required" in response.json["error"]

def test_create_amenity_invalid_type(client: FlaskClient):
    response = client.post('/api/v1/amenities/', json={"name": 123})
    assert response.status_code == 400
    assert "must be a string" in response.json["error"]

def test_get_all_amenities(client: FlaskClient):
    client.post('/api/v1/amenities/', json={'name': 'Pool'})
    response = client.get('/api/v1/amenities/')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert any('name' in amenity for amenity in response.json)

def test_put_amenity_success(client: FlaskClient):
    post_resp = client.post('/api/v1/amenities/', json={'name': 'Sauna'})
    amenity_id = post_resp.json['id']
    
    put_resp = client.put(f'/api/v1/amenities/{amenity_id}', json={'name': 'Hammam'})
    assert put_resp.status_code == 200
    
    get_resp = client.get(f'/api/v1/amenities/{amenity_id}')
    assert get_resp.json['name'] == 'Hammam'

def test_put_amenity_not_found(client: FlaskClient):
    response = client.put('/api/v1/amenities/invalid-id', json={"name": "Jacuzzi"})
    assert response.status_code == 404
    assert "not found" in response.json["error"].lower()

def test_get_amenity_by_id(client: FlaskClient):
    post_resp = client.post('/api/v1/amenities/', json={'name': 'Terrace'})
    amenity_id = post_resp.json['id']

    get_resp = client.get(f'/api/v1/amenities/{amenity_id}')
    assert get_resp.status_code == 200
    assert get_resp.json['name'] == 'Terrace'
