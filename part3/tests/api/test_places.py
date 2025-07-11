import pytest
import uuid

@pytest.fixture
def admin_auth_headers(client):
    client.post("/api/v1/users/", json={
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@example.com",
        "password": "adminpass",
        "is_admin": True
    })
    from app.models.user import User
    from app.extensions import db
    user = User.query.filter_by(email="admin@example.com").first()
    user.is_admin = True
    db.session.commit()

    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@example.com",
        "password": "adminpass"
    })
    token = resp.json["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def normal_user(client):
    resp = client.post("/api/v1/users/", json={
        "first_name": "Normal",
        "last_name": "User",
        "email": f"user_{uuid.uuid4().hex[:6]}@example.com",
        "password": "userpass"
    })
    assert resp.status_code == 201
    return resp.json

@pytest.fixture
def place_owner(client):
    resp = client.post("/api/v1/users/", json={
        "first_name": "Owner",
        "last_name": "User",
        "email": f"owner_{uuid.uuid4().hex[:6]}@example.com",
        "password": "ownerpass"
    })
    assert resp.status_code == 201
    return resp.json

@pytest.fixture
def normal_auth_headers(client, normal_user):
    resp = client.post("/api/v1/auth/login", json={
        "email": normal_user["email"],
        "password": "userpass"
    })
    token = resp.json["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def owner_auth_headers(client, place_owner):
    resp = client.post("/api/v1/auth/login", json={
        "email": place_owner["email"],
        "password": "ownerpass"
    })
    token = resp.json["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def created_place(client, owner_auth_headers, place_owner):
    data = {
        "title": "Test Place",
        "description": "Nice place",
        "price": 150.0,
        "latitude": 48.8566,
        "longitude": 2.3522,
        "owner_id": place_owner["id"],
        "amenities": []
    }
    resp = client.post("/api/v1/places/", json=data, headers=owner_auth_headers)
    assert resp.status_code == 201
    return resp.json

def test_list_places(client, created_place):
    resp = client.get("/api/v1/places/")
    assert resp.status_code == 200
    assert isinstance(resp.json, list)
    assert any(p["id"] == created_place["id"] for p in resp.json)

def test_get_place(client, created_place):
    place_id = created_place["id"]
    resp = client.get(f"/api/v1/places/{place_id}")
    assert resp.status_code == 200
    assert resp.json["id"] == place_id

def test_get_place_not_found(client):
    resp = client.get("/api/v1/places/non-existent-id")
    assert resp.status_code == 404
    assert "not found" in resp.json["error"].lower()

def test_create_place_unauthorized(client, created_place):
    # Try to create place without auth
    data = {
        "title": "Unauthorized Place",
        "description": "No token",
        "price": 100,
        "latitude": 0,
        "longitude": 0,
        "owner_id": created_place["owner_id"],
        "amenities": []
    }
    resp = client.post("/api/v1/places/", json=data)
    assert resp.status_code == 401

def test_create_place(client, owner_auth_headers, place_owner):
    data = {
        "title": "New Place",
        "description": "Created by owner",
        "price": 120,
        "latitude": 40,
        "longitude": -74,
        "owner_id": place_owner["id"],
        "amenities": []
    }
    resp = client.post("/api/v1/places/", json=data, headers=owner_auth_headers)
    assert resp.status_code == 201
    assert resp.json["title"] == data["title"]
    assert resp.json["owner_id"] == place_owner["id"]

def test_update_place_owner(client, owner_auth_headers, created_place):
    place_id = created_place["id"]
    update_data = {
        "title": "Updated Title",
        "description": created_place["description"],
        "price": created_place["price"],
        "latitude": created_place["latitude"],
        "longitude": created_place["longitude"],
        "owner_id": created_place["owner_id"],
        "amenities": created_place.get("amenities", [])
    }
    resp = client.put(f"/api/v1/places/{place_id}", json=update_data, headers=owner_auth_headers)
    assert resp.status_code == 200
    assert resp.json["title"] == "Updated Title"

def test_update_place_forbidden(client, normal_auth_headers, created_place):
    place_id = created_place["id"]
    update_data = {
        "title": "Trying to update",
        "description": created_place["description"],
        "price": created_place["price"],
        "latitude": created_place["latitude"],
        "longitude": created_place["longitude"],
        "owner_id": created_place["owner_id"],
        "amenities": created_place.get("amenities", [])
    }
    resp = client.put(f"/api/v1/places/{place_id}", json=update_data, headers=normal_auth_headers)
    assert resp.status_code == 403

def test_update_place_admin(client, admin_auth_headers, created_place):
    place_id = created_place["id"]
    update_data = {
        "title": "Admin Updated Title",
        "description": created_place["description"],
        "price": created_place["price"],
        "latitude": created_place["latitude"],
        "longitude": created_place["longitude"],
        "owner_id": created_place["owner_id"],
        "amenities": created_place.get("amenities", [])
    }
    resp = client.put(f"/api/v1/places/{place_id}", json=update_data, headers=admin_auth_headers)
    assert resp.status_code == 200
    assert resp.json["title"] == "Admin Updated Title"

def test_delete_place_owner(client, owner_auth_headers, created_place):
    place_id = created_place["id"]
    resp = client.delete(f"/api/v1/places/{place_id}", headers=owner_auth_headers)
    assert resp.status_code == 204 or resp.status_code == 200  # selon ton API

def test_delete_place_forbidden(client, normal_auth_headers, created_place):
    place_id = created_place["id"]
    resp = client.delete(f"/api/v1/places/{place_id}", headers=normal_auth_headers)
    assert resp.status_code == 403

def test_delete_place_admin(client, admin_auth_headers, created_place):
    # Recreate place for this test, if needed
    data = {
        "title": "Place for Admin Delete",
        "description": "Admin deletes",
        "price": 123,
        "latitude": 10,
        "longitude": 10,
        "owner_id": created_place["owner_id"],
        "amenities": []
    }
    resp = client.post("/api/v1/places/", json=data, headers=admin_auth_headers)
    assert resp.status_code == 201
    place_id = resp.json["id"]

    resp = client.delete(f"/api/v1/places/{place_id}", headers=admin_auth_headers)
    assert resp.status_code == 204 or resp.status_code == 200

def test_delete_place_not_found(client, admin_auth_headers):
    resp = client.delete("/api/v1/places/non-existent-id", headers=admin_auth_headers)
    assert resp.status_code == 404
