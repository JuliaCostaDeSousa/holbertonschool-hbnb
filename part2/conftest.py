import pytest
from app import create_app
from app.extensions import db as _db
from flask_jwt_extended import create_access_token
from app.models.user import User
import uuid


@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JWT_SECRET_KEY": "testing-secret"
    })

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Creates a new database for the test."""
    with app.app_context():
        yield _db
        _db.session.rollback()


@pytest.fixture()
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture()
def test_user(db):
    """Create a test user in the DB and return it."""
    user = User(
        id=str(uuid.uuid4()),
        first_name="Test",
        last_name="User",
        email="test@example.com",
        password="hashedpassword",  # Remplace si hash requis
        is_admin=False
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def auth_header(test_user):
    """Return a header with a valid JWT for test_user."""
    token = create_access_token(identity=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}
