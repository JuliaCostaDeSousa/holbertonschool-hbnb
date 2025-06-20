import pytest
from flask.testing import FlaskClient
import uuid

@pytest.fixture
def user_data():
    return {
        "first_name": "Alice",
        "last_name": "Doe",
        "email": "alice@example.com"
    }

def test_create_user_success(client: FlaskClient, user_data):
    response = client.post('/api/v1/users/', json=user_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data["first_name"] == user_data["first_name"]
    assert data["email"] == user_data["email"]

def test_create_user_duplicate_email(client: FlaskClient, user_data):
    client.post('/api/v1/users/', json=user_data)
    response = client.post('/api/v1/users/', json=user_data)
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_get_all_users(client: FlaskClient, user_data):
    client.post('/api/v1/users/', json=user_data)
    response = client.get('/api/v1/users/')
    assert response.status_code == 200
    users = response.get_json()
    assert isinstance(users, list)
    assert any(u["email"] == user_data["email"] for u in users)

def test_get_user_by_id(client: FlaskClient):
    email = f"alice_{uuid.uuid4()}@example.com"
    user_data = {
        "first_name": "Alice",
        "last_name": "Doe",
        "email": email
    }

    post_resp = client.post('/api/v1/users/', json=user_data)
    assert post_resp.status_code == 201
    user_id = post_resp.get_json()["id"]

    get_resp = client.get(f'/api/v1/users/{user_id}')
    assert get_resp.status_code == 200
    fetched_user = get_resp.get_json()
    assert fetched_user["id"] == user_id
    assert fetched_user["email"] == email

def test_get_user_not_found(client: FlaskClient):
    response = client.get('/api/v1/users/invalid-id')
    assert response.status_code == 404

def test_update_user_success(client: FlaskClient):
    email = f"alice_{uuid.uuid4()}@example.com"
    user_data = {
        "first_name": "Alice",
        "last_name": "Doe",
        "email": email
    }

    post_resp = client.post('/api/v1/users/', json=user_data)
    assert post_resp.status_code == 201
    user_id = post_resp.get_json()["id"]

    update_data = {
        "first_name": "Alicia",
        "last_name": "Doe",
        "email": email
    }

    put_resp = client.put(f'/api/v1/users/{user_id}', json=update_data)
    assert put_resp.status_code == 200
    updated_user = put_resp.get_json()
    assert updated_user["first_name"] == "Alicia"
    assert updated_user["last_name"] == "Doe"
    assert updated_user["email"] == email

def test_update_user_not_found(client: FlaskClient):
    update_data = {
        "first_name": "Ghost",
        "last_name": "User",
        "email": "ghost@example.com"
    }
    response = client.put('/api/v1/users/nonexistent-id', json=update_data)
    assert response.status_code == 404
