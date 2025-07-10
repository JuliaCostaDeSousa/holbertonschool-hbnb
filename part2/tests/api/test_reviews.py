import pytest
import uuid

@pytest.fixture
def admin_auth_headers(client):
    # Création admin user
    client.post("/api/v1/users/", json={
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@example.com",
        "password": "adminpass",
        "is_admin": False  # ignore côté API (sécurité)
    })

    from app.models.user import User
    from app.extensions import db

    # Mettre à jour l'user en base pour is_admin=True AVANT login
    user = User.query.filter_by(email="admin@example.com").first()
    user.is_admin = True
    db.session.commit()

    # Faire la requête login (création token)
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
def created_place(client, admin_auth_headers, place_owner):
    data = {
        "title": "Test Place",
        "description": "Beautiful ocean view",
        "price": 200.0,
        "latitude": 25.0,
        "longitude": 55.0,
        "owner_id": place_owner["id"]
    }
    resp = client.post("/api/v1/places/", json=data, headers=admin_auth_headers)
    assert resp.status_code == 201
    return resp.json

@pytest.fixture
def created_review(client, normal_auth_headers, created_place):
    payload = {
        "text": "Super endroit !",
        "rating": 4,
        "place_id": created_place["id"]
    }
    resp = client.post("/api/v1/reviews/", json=payload, headers=normal_auth_headers)
    assert resp.status_code == 201
    return resp.json

@pytest.fixture
def another_user(client):
    resp = client.post("/api/v1/users/", json={
        "first_name": "Another",
        "last_name": "User",
        "email": f"another_{uuid.uuid4().hex[:6]}@example.com",
        "password": "anotherpass"
    })
    assert resp.status_code == 201
    return resp.json

@pytest.fixture
def another_auth_headers(client, another_user):
    resp = client.post("/api/v1/auth/login", json={
        "email": another_user["email"],
        "password": "anotherpass"
    })
    token = resp.json["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def another_review(client, another_auth_headers, created_place):
    payload = {
        "text": "Review d'un autre user",
        "rating": 3,
        "place_id": created_place["id"]
    }
    resp = client.post("/api/v1/reviews/", json=payload, headers=another_auth_headers)
    assert resp.status_code == 201
    return resp.json


# --- Tests API reviews ---

def test_create_review(client, normal_auth_headers, created_place):
    payload = {
        "text": "Très bon endroit",
        "rating": 5,
        "place_id": created_place["id"]
    }
    resp = client.post("/api/v1/reviews/", json=payload, headers=normal_auth_headers)
    assert resp.status_code == 201
    assert "id" in resp.json
    assert resp.json["text"] == payload["text"]
    assert resp.json["rating"] == payload["rating"]

def test_create_review_own_place(client, normal_auth_headers, created_place, place_owner):
    # Utilisateur normal qui est propriétaire du lieu
    # On force la création d’une review pour son propre lieu
    # Le test doit échouer (400)
    # Pour cela, on doit s'assurer que l'user normal a le même id que owner
    # Par défaut normal_user et place_owner sont différents, donc on recrée un token pour owner
    resp_login = client.post("/api/v1/auth/login", json={
        "email": place_owner["email"],
        "password": "ownerpass"
    })
    token = resp_login.json["access_token"]
    headers_owner = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "text": "Avis interdit",
        "rating": 4,
        "place_id": created_place["id"]
    }
    resp = client.post("/api/v1/reviews/", json=payload, headers=headers_owner)
    assert resp.status_code == 400
    assert "cannot review your own place" in resp.json["error"].lower()

def test_create_review_invalid_rating(client, normal_auth_headers, created_place):
    payload = {
        "text": "Note invalide",
        "rating": 6,
        "place_id": created_place["id"]
    }
    resp = client.post("/api/v1/reviews/", json=payload, headers=normal_auth_headers)
    assert resp.status_code == 400
    assert "rating must be between 1 and 5" in resp.json["error"].lower()

def test_create_review_place_not_found(client, normal_auth_headers):
    payload = {
        "text": "Lieu inconnu",
        "rating": 3,
        "place_id": "non-existent-id"
    }
    resp = client.post("/api/v1/reviews/", json=payload, headers=normal_auth_headers)
    assert resp.status_code == 404
    assert "place not found" in resp.json["error"].lower()

def test_create_review_duplicate(client, normal_auth_headers, created_place, created_review):
    payload = {
        "text": "2ème review",
        "rating": 4,
        "place_id": created_place["id"]
    }
    resp = client.post("/api/v1/reviews/", json=payload, headers=normal_auth_headers)
    assert resp.status_code == 400
    assert "already reviewed" in resp.json["error"].lower()

def test_get_review_by_id(client, normal_auth_headers, created_review):
    review_id = created_review["id"]
    resp = client.get(f"/api/v1/reviews/{review_id}")
    assert resp.status_code == 200
    assert resp.json["id"] == review_id

def test_get_review_not_found(client):
    resp = client.get("/api/v1/reviews/non-existent-id")
    assert resp.status_code == 404
    assert "not found" in resp.json["error"].lower()

def test_update_review(client, normal_auth_headers, created_review):
    review_id = created_review["id"]
    new_data = {"text": "Modifié", "rating": 2, "place_id": created_review["place_id"]}
    resp = client.put(f"/api/v1/reviews/{review_id}", json=new_data, headers=normal_auth_headers)
    assert resp.status_code == 200
    assert resp.json["text"] == new_data["text"]
    assert resp.json["rating"] == new_data["rating"]

def test_update_review_not_found(client, normal_auth_headers):
    resp = client.put("/api/v1/reviews/non-existent-id", json={"text": "test", "rating": 3, "place_id": "fake"}, headers=normal_auth_headers)
    assert resp.status_code == 404
    assert "not found" in resp.json["error"].lower()

def test_update_review_forbidden(client, admin_auth_headers, normal_auth_headers, another_review):
    review_id = another_review["id"]
    new_data = {"text": "Admin modifie", "rating": 4, "place_id": another_review["place_id"]}
    # Admin peut modifier
    resp_admin = client.put(f"/api/v1/reviews/{review_id}", json=new_data, headers=admin_auth_headers)
    assert resp_admin.status_code == 200
    assert resp_admin.json["text"] == new_data["text"]

    # Normal user ne peut pas modifier review d'un autre user
    resp_user = client.put(f"/api/v1/reviews/{review_id}", json=new_data, headers=normal_auth_headers)
    assert resp_user.status_code == 403
    assert "forbidden" in resp_user.json["error"].lower()

def test_update_review_forbidden_user(client, normal_auth_headers, another_review):
    review_id = another_review["id"]
    new_data = {"text": "User lambda modifie review d'un autre", "rating": 4, "place_id": another_review["place_id"]}
    resp = client.put(f"/api/v1/reviews/{review_id}", json=new_data, headers=normal_auth_headers)
    assert resp.status_code == 403
    assert "forbidden" in resp.json["error"].lower()

def test_delete_review(client, normal_auth_headers, created_review):
    review_id = created_review["id"]
    resp = client.delete(f"/api/v1/reviews/{review_id}", headers=normal_auth_headers)
    assert resp.status_code == 200
    assert "deleted" in resp.json["message"].lower()

def test_delete_review_not_found(client, normal_auth_headers):
    resp = client.delete("/api/v1/reviews/non-existent-id", headers=normal_auth_headers)
    assert resp.status_code == 404
    assert "not found" in resp.json["error"].lower()

def test_delete_review_forbidden_user(client, normal_auth_headers, another_review):
    review_id = another_review["id"]
    resp = client.delete(f"/api/v1/reviews/{review_id}", headers=normal_auth_headers)
    assert resp.status_code == 403
    assert "forbidden" in resp.json["error"].lower()

def test_list_reviews(client):
    resp = client.get("/api/v1/reviews/")
    assert resp.status_code == 200
    assert isinstance(resp.json, list)

# Tests complémentaires

def test_create_review_empty_text(client, normal_auth_headers, created_place):
    payload = {
        "text": "",
        "rating": 3,
        "place_id": created_place["id"]
    }
    resp = client.post("/api/v1/reviews/", json=payload, headers=normal_auth_headers)
    assert resp.status_code == 400  # ici on attend un rejet
    assert "error" in resp.json

def test_create_review_rating_too_low(client, normal_auth_headers, created_place):
    payload = {
        "text": "Rating trop bas",
        "rating": 0,
        "place_id": created_place["id"]
    }
    resp = client.post("/api/v1/reviews/", json=payload, headers=normal_auth_headers)
    assert resp.status_code == 400

def test_update_review_invalid_rating(client, normal_auth_headers, created_review):
    review_id = created_review["id"]
    new_data = {"text": "Note invalide", "rating": -1, "place_id": created_review["place_id"]}
    resp = client.put(f"/api/v1/reviews/{review_id}", json=new_data, headers=normal_auth_headers)
    assert resp.status_code == 400

def test_update_review_missing_text(client, normal_auth_headers, created_review):
    review_id = created_review["id"]
    new_data = {"rating": 3, "place_id": created_review["place_id"]}
    resp = client.put(f"/api/v1/reviews/{review_id}", json=new_data, headers=normal_auth_headers)
    # Si tu as une validation stricte, le champ text manquant peut déclencher une erreur
    # Sinon la mise à jour peut se faire partiellement
    # Ajuste selon ta logique métier
    assert resp.status_code in (200, 400)

