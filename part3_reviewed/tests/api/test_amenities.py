import pytest

### ---------- Fixtures ----------

@pytest.fixture
def amenity_payload():
    return {"name": "Sauna"}

@pytest.fixture
def auth_headers(client):
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

    response = client.post("/api/v1/auth/login", json={
        "email": "admin@example.com",
        "password": "adminpass"
    })

    assert response.status_code == 200
    token = response.json["access_token"]
    return {"Authorization": f"Bearer {token}"}



import uuid

@pytest.fixture
def created_amenity(client, auth_headers):
    """Crée une amenity avec un nom unique"""
    unique_name = f"Grenier-{uuid.uuid4().hex[:6]}"
    response = client.post("/api/v1/amenities/", json={"name": unique_name}, headers=auth_headers)
    assert response.status_code == 201
    return response.json



### ---------- Tests ----------

def test_create_amenity(client, amenity_payload, auth_headers):
    response = client.post("/api/v1/amenities/", json=amenity_payload, headers=auth_headers)
    print("Create response:", response.status_code, response.json)

    assert response.status_code == 201
    assert "id" in response.json
    assert response.json["name"] == amenity_payload["name"]


def test_get_amenities(client):
    response = client.get("/api/v1/amenities/")
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_list_amenities(client):
    response = client.get("/api/v1/amenities/")
    assert response.status_code == 200
    print("Existing amenities:", response.json)


def test_get_amenity_by_id(client, created_amenity):
    amenity_id = created_amenity["id"]

    get_resp = client.get(f"/api/v1/amenities/{amenity_id}")
    assert get_resp.status_code == 200
    assert get_resp.json["id"] == amenity_id
    assert get_resp.json["name"] == created_amenity["name"]


def test_update_amenity(client, created_amenity, auth_headers):
    amenity_id = created_amenity["id"]
    new_name = f"NouveauNom-{uuid.uuid4().hex[:6]}"
    response = client.put(f"/api/v1/amenities/{amenity_id}", json={"name": new_name}, headers=auth_headers)
    print("Amenity created:", created_amenity)
    print("Trying to update ID:", created_amenity["id"])
    assert response.status_code == 200
    assert response.json["name"] == new_name


def test_delete_amenity(client, created_amenity, auth_headers):
    amenity_id = created_amenity["id"]

    delete_resp = client.delete(f"/api/v1/amenities/{amenity_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/api/v1/amenities/{amenity_id}")
    assert get_resp.status_code == 404
