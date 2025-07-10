import pytest
from app.services import facade
from app import create_app
from app.extensions import db as _db
from app.models.user import User
from sqlalchemy.orm import scoped_session, sessionmaker

@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    yield _db
    _db.session.rollback()

@pytest.fixture(scope="function")
def session(db):
    """Crée une session isolée pour chaque test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    session_factory = sessionmaker(bind=connection)
    session = scoped_session(session_factory)
    db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def user(session):
    """Crée un utilisateur valide pour les tests."""
    user_data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "password": "securepassword"
    }
    user = facade.create_user(user_data)
    session.add(user)
    session.commit()
    return user


def test_valid_user_creation(user):
    assert user.id is not None
    assert user.first_name == "Alice"
    assert user.last_name == "Smith"
    assert user.email == "alice@example.com"
    assert user.is_admin is False


@pytest.mark.parametrize("field,value,error", [
    ("first_name", 123, TypeError),
    ("last_name", [], TypeError),
    ("email", "invalid_email", ValueError),
    ("email", 999, TypeError),
    ("is_admin", "yes", TypeError),
])
def test_invalid_user_inputs(field, value, error, session):
    kwargs = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "password": "securepassword"
    }
    kwargs[field] = value

    with pytest.raises(error):
        user = User(**kwargs)
        session.add(user)
        session.commit()


def test_password_hashing_and_verification(session):
    user_data = {
        "first_name": "Bob",
        "last_name": "Jones",
        "email": "bob@example.com",
        "password": "mypassword"
    }
    user = facade.create_user(user_data)
    session.add(user)
    session.commit()

    assert user._password != "mypassword"
    assert user.verify_password("mypassword") is True
    assert user.verify_password("wrongpass") is False
