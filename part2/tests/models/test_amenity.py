import pytest
from app import create_app
from app.extensions import db as _db
from app.models.amenity import Amenity
from sqlalchemy.orm import scoped_session, sessionmaker

# === FIXTURES ===

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
def amenity_data():
    return {"name": "Wi-Fi"}

# === TESTS ===

def test_valid_amenity_creation(session, amenity_data):
    amenity = Amenity(**amenity_data)
    session.add(amenity)
    session.commit()
    assert amenity.id is not None
    assert amenity.name == "Wi-Fi"

@pytest.mark.parametrize("value,error", [
    (123, TypeError),
    (None, TypeError),
])
def test_invalid_amenity_name(session, value, error):
    with pytest.raises(error):
        amenity = Amenity(name=value)
        session.add(amenity)
        session.commit()

def test_update_amenity(session):
    amenity = Amenity(name="Wi-Fi")
    session.add(amenity)
    session.commit()

    # Mise à jour
    amenity.update({"name": "Fast Wi-Fi"})
    session.commit()

    updated = session.query(Amenity).get(amenity.id)
    assert updated.name == "Fast Wi-Fi"

def test_delete_amenity(session):
    amenity = Amenity(name="Jacuzzi")
    session.add(amenity)
    session.commit()

    session.delete(amenity)
    session.commit()

    deleted = session.query(Amenity).get(amenity.id)
    assert deleted is None
