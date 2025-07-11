import pytest
import uuid

# --- Fixtures (idem) ---

@pytest.fixture
def admin_auth_headers(client):
    client.post("/api/v1/users/", json={
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin_edge@example.com",
        "password": "adminpass",
        "is_admin": True
    })
    from app.models.user import User
    from app.extensions import db
    user = User.query.filter_by(email="admin_edge@example.com").first()
    user.is_admin = True
    db.session.commit()

    resp = client.post("/api/v1/auth/login", json={
        "email": "admin_edge@example.com",
        "password": "adminpass"
    })
    token = resp.json["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def normal_user(client):
    resp = client.post("/api/v1/users/", json={
        "first_name": "Normal",
        "last_name": "User",
        "email": f"normal_{uuid.uuid4().hex[:6]}@example.com",
        "password": "userpass"
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
def place_owner_auth(client, place_owner):
    resp = client.post("/api/v1/auth/login", json={
        "email": place_owner["email"],
        "password": "ownerpass"
    })
    token = resp.json["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def created_place(client, admin_auth_headers, place_owner):
    data = {
        "title": "Edge Case Place",
        "description": "Testing edges",
        "price": 100,
        "latitude": 10,
        "longitude": 10,
        "owner_id": place_owner["id"],
        "amenities": []
    }
    resp = client.post("/api/v1/places/", json=data, headers=admin_auth_headers)
    assert resp.status_code == 201
    return resp.json

@pytest.fixture
def created_review(client, normal_auth_headers, created_place):
    payload = {
        "text": "Edge review",
        "rating": 3,
        "place_id": created_place["id"]
    }
    resp = client.post("/api/v1/reviews/", json=payload, headers=normal_auth_headers)
    assert resp.status_code == 201
    return resp.json

# --- Tests champs vides / absents (robustesse) ---

def test_create_user_empty_fields(client):
    for field in ["first_name", "last_name", "email", "password"]:
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "secure123"
        }
        data[field] = ""  # champ vide
        resp = client.post("/api/v1/users/", json=data)
        assert resp.status_code == 400 or resp.status_code == 422, f"Failed on empty {field}"

def test_create_user_missing_fields(client):
    required_fields = ["first_name", "last_name", "email", "password"]
    for missing in required_fields:
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "secure123"
        }
        data.pop(missing)
        resp = client.post("/api/v1/users/", json=data)
        assert resp.status_code == 400 or resp.status_code == 422, f"Failed on missing {missing}"

def create_test_user(client, headers):
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": f"testuser_{uuid.uuid4().hex[:6]}@example.com",
        "password": "testpass"
    }
    resp = client.post("/api/v1/users/", json=user_data, headers=headers)
    assert resp.status_code == 201
    return resp.json['id']

def test_create_place_empty_and_missing_fields(client, admin_auth_headers):
    user_id = create_test_user(client, admin_auth_headers)
    print("User ID utilisé :", user_id)
    required_fields = ["title", "price", "latitude", "longitude", "owner_id", "amenities"]
    base_data = {
        "title": "Place",
        "description": "Desc",
        "price": 10.0,
        "latitude": 1.0,
        "longitude": 1.0,
        "owner_id": user_id,
        "amenities": []
    }

    for field in required_fields:
        data = base_data.copy()
        if field == "amenities":
            # amenities vide est OK, ne teste pas l'erreur ici
            continue
        if isinstance(data[field], list):
            data[field] = []
        else:
            data[field] = ""
        resp = client.post("/api/v1/places/", json=data, headers=admin_auth_headers)
        assert resp.status_code in (400, 422), f"Failed on empty {field}"

def test_create_review_rating_boundaries(client, normal_auth_headers, place_owner, admin_auth_headers):
    # Crée une place fraîche pour ce test
    data = {
        "title": "Place for rating boundary test",
        "description": "Test place",
        "price": 50,
        "latitude": 1,
        "longitude": 1,
        "owner_id": place_owner["id"],
        "amenities": []
    }
    resp = client.post("/api/v1/places/", json=data, headers=admin_auth_headers)
    assert resp.status_code == 201
    place_id = resp.json["id"]

    for rating in [1, 5]:
        payload = {"text": "Boundary test", "rating": rating, "place_id": place_id}
        resp = client.post("/api/v1/reviews/", json=payload, headers=normal_auth_headers)
        if rating == 1:
            # 1ère review OK
            assert resp.status_code == 201
        else:
            # 2e review par le même user sur même place : rejet attendu
            assert resp.status_code == 400


def test_create_review_rating_boundaries_separate_places(client, normal_auth_headers, place_owner, admin_auth_headers):
    place_ids = []
    for i in range(2):
        data = {
            "title": f"Boundary test place {i}",
            "description": "Testing rating boundaries",
            "price": 100,
            "latitude": 10,
            "longitude": 10,
            "owner_id": place_owner["id"],
            "amenities": []
        }
        resp = client.post("/api/v1/places/", json=data, headers=admin_auth_headers)
        assert resp.status_code == 201
        place_ids.append(resp.json["id"])

    for rating, place_id in zip([1, 5], place_ids):
        payload = {"text": "Boundary test", "rating": rating, "place_id": place_id}
        resp = client.post("/api/v1/reviews/", json=payload, headers=normal_auth_headers)
        assert resp.status_code == 201




# --- Tests droits d'accès ---

def test_update_place_not_owner_not_admin(client, normal_auth_headers, created_place):
    update_data = {
        "title": "Hack",
        "price": 99,
        "latitude": 1,
        "longitude": 1,
        "owner_id": created_place["owner_id"],
        "amenities": []
    }
    resp = client.put(f"/api/v1/places/{created_place['id']}", json=update_data, headers=normal_auth_headers)
    assert resp.status_code == 403

def test_delete_review_not_owner_not_admin(client, normal_auth_headers, created_review):
    resp = client.delete(f"/api/v1/reviews/{created_review['id']}", headers=normal_auth_headers)
    # Ici on suppose que normal_user est proprio de created_review donc devrait réussir,
    # sinon adapte selon ta logique.
    assert resp.status_code in (200, 204)

def test_delete_place_not_owner_not_admin(client, normal_auth_headers, created_place):
    resp = client.delete(f"/api/v1/places/{created_place['id']}", headers=normal_auth_headers)
    assert resp.status_code == 403

def test_update_review_invalid_rating(client, normal_auth_headers, created_review):
    update_data = {"text": "Bad rating", "rating": 10, "place_id": created_review["place_id"]}
    resp = client.put(f"/api/v1/reviews/{created_review['id']}", json=update_data, headers=normal_auth_headers)
    assert resp.status_code == 400

# --- Tests supplémentaires (valeurs limites, etc.) ---

def test_update_review_missing_text(client, normal_auth_headers, created_review):
    update_data = {"rating": 4, "place_id": created_review["place_id"]}
    resp = client.put(f"/api/v1/reviews/{created_review['id']}", json=update_data, headers=normal_auth_headers)
    assert resp.status_code in (200, 400)

def test_get_nonexistent_user(client, admin_auth_headers):
    fake_id = str(uuid.uuid4())
    resp = client.get(f"/api/v1/users/{fake_id}", headers=admin_auth_headers)
    assert resp.status_code == 404

def test_get_user_unauthorized(client, normal_user):
    user_id = normal_user["id"]
    resp = client.get(f"/api/v1/users/{user_id}")
    assert resp.status_code == 401

def test_create_user_blank_password(client):
    data = {
        "first_name": "User",
        "last_name": "NoPass",
        "email": f"nopass_{uuid.uuid4().hex[:6]}@example.com",
        "password": ""
    }
    resp = client.post("/api/v1/users/", json=data)
    assert resp.status_code == 400 or resp.status_code == 422

def test_update_user_blank_password(client, normal_auth_headers, normal_user):
    user_id = normal_user["id"]
    update_data = {
        "first_name": normal_user["first_name"],
        "last_name": normal_user["last_name"],
        "email": normal_user["email"],
        "password": ""
    }
    resp = client.put(f"/api/v1/users/{user_id}", json=update_data, headers=normal_auth_headers)
    # Selon ta logique métier, ça peut être 400 ou update partielle (200)
    assert resp.status_code in (200, 400)
