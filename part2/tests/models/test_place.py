import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity


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


@pytest.fixture(scope='function')
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()

    from sqlalchemy.orm import scoped_session, sessionmaker
    session_factory = sessionmaker(bind=connection)
    session = scoped_session(session_factory)
    db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def user(session):
    user = User(first_name="Alice", last_name="Wonders", email="alice@example.com", password="hashed")
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def place(session, user):
    place = Place(
        title="Beach House",
        description="Beautiful ocean view",
        price=200.0,
        latitude=25.0,
        longitude=55.0,
        owner_id=user.id
    )
    session.add(place)
    session.commit()
    return place


def test_valid_place_creation(place, user):
    assert place.title == "Beach House"
    assert place.owner.id == user.id
    assert place.latitude == 25.0
    assert place.longitude == 55.0
    assert isinstance(place.reviews, list)
    assert isinstance(place.amenities, list)


@pytest.mark.parametrize("field,value,error", [
    ("title", 123, TypeError),
    ("title", "", ValueError),
    ("description", 456, TypeError),
    ("description", "", ValueError),
    ("price", "100", TypeError),
    ("price", -10.0, ValueError),
    ("latitude", "45N", TypeError),
    ("latitude", -200.0, ValueError),
    ("longitude", [], TypeError),
    ("longitude", -300.0, ValueError),
])
def test_invalid_place_inputs(field, value, error, user):
    kwargs = {
        "title": "Valid",
        "description": "Valid desc",
        "price": 100.0,
        "latitude": 0.0,
        "longitude": 0.0,
        "owner_id": user.id
    }
    kwargs[field] = value
    with pytest.raises(error):
        place = Place(**kwargs)


def test_add_and_remove_review(place, session, user):
    review = Review(text="Cool spot", rating=5, user_id=user.id, place_id=place.id)
    session.add(review)
    session.commit()
    assert review in place.reviews
    place.delete_review(review)
    assert review not in place.reviews


def test_add_and_remove_amenity(place, session):
    amenity = Amenity(name="Pool")
    session.add(amenity)
    session.commit()
    place.add_amenity(amenity)
    assert amenity in place.amenities
    place.delete_amenity(amenity)
    assert amenity not in place.amenities
