import pytest
import uuid

### ---------- Fixtures ----------

@pytest.fixture
def user_payload():
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": f"testuser_{uuid.uuid4().hex[:6]}@example.com",
        "password": "TestPass123"
    }

@pytest.fixture
def auth_headers(client):
    # Création d'un admin user + login
    client.post("/api/v1/users/", json={
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@example.com",
        "password": "adminpass",
        "is_admin": True  # même si ignored côté API, on set en base ensuite
    })

    from app.models.user import User
    from app.extensions import db
    user = User.query.filter_by(email="admin@example.com").first()
    user.is_admin = True
    db.session.commit()

    response = client.post("/api/v1/auth/login", json={
        "email": "admin@example.com",
        "password": "adminpass"
    })

    assert response.status_code == 200
    token = response.json["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def created_user(client, auth_headers, user_payload):
    response = client.post("/api/v1/users/", json=user_payload, headers=auth_headers)
    assert response.status_code == 201
    return response.json


### ---------- Tests ----------

def test_create_user(client, user_payload):
    response = client.post("/api/v1/users/", json=user_payload)
    assert response.status_code == 201
    assert "id" in response.json
    assert response.json["email"] == user_payload["email"]

def test_create_user_duplicate_email(client, created_user):
    payload = {
        "first_name": "Dup",
        "last_name": "User",
        "email": created_user["email"],
        "password": "pass1234"
    }
    response = client.post("/api/v1/users/", json=payload)
    assert response.status_code == 400
    assert "error" in response.json

def test_list_users_admin(client, auth_headers):
    response = client.get("/api/v1/users/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert any("email" in u for u in response.json)

def test_list_users_forbidden(client):
    response = client.get("/api/v1/users/")
    assert response.status_code == 401  # pas de token

def test_get_user_self(client, created_user, auth_headers):
    user_id = created_user["id"]
    response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json["id"] == user_id

def test_get_user_forbidden(client, created_user):
    user_id = created_user["id"]
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 401  # pas de token

def test_update_user_self(client, created_user, auth_headers):
    user_id = created_user["id"]
    new_data = {"first_name": "UpdatedName", "last_name": "UpdatedLast", "email": created_user["email"], "password": "newpass123"}
    response = client.put(f"/api/v1/users/{user_id}", json=new_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json["first_name"] == "UpdatedName"

def test_delete_user_self(client, created_user, auth_headers):
    user_id = created_user["id"]
    response = client.delete(f"/api/v1/users/{user_id}", headers=auth_headers)
    assert response.status_code == 204

    # Vérifier que user n’existe plus
    get_resp = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
    assert get_resp.status_code == 404
