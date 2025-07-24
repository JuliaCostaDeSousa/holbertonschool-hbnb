import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
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
    user = User(first_name="Alice", last_name="Smith", email="alice@example.com")
    user.hash_password("securepassword")
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def place(session, user):
    place = Place(title="Nice place", description="Clean and quiet", price=99.99, latitude=48.85, longitude=2.35, owner=user)
    session.add(place)
    session.commit()
    return place

@pytest.fixture
def review_data(user, place):
    return {
        "text": "Great location, clean and comfy.",
        "rating": 5,
        "user": user,
        "place": place
    }

# === TESTS ===

def test_valid_review_creation(session, review_data):
    review = Review(**review_data)
    session.add(review)
    session.commit()
    assert review.id is not None
    assert review.text == "Great location, clean and comfy."
    assert review.rating == 5
    assert review.user is not None
    assert review.place is not None

@pytest.mark.parametrize("value,error", [
    (None, TypeError),
    (123, TypeError),
])
def test_invalid_text(session, user, place, value, error):
    with pytest.raises(error):
        review = Review(text=value, rating=4, owner=user, place=place)
        session.add(review)
        session.commit()

@pytest.mark.parametrize("value,error", [
    ("bad", TypeError),
    (10, ValueError),
    (0, ValueError),
])
def test_invalid_rating(session, user, place, value, error):
    with pytest.raises(error):
        review = Review(text="Correct", rating=value, user=user, place=place)
        session.add(review)
        session.commit()

def test_review_update(session, review_data):
    review = Review(**review_data)
    session.add(review)
    session.commit()

    review.update({"text": "Actually, it was just okay.", "rating": 3})
    session.commit()

    assert review.text == "Actually, it was just okay."
    assert review.rating == 3

def test_review_deletion(session, user, place):
    review = Review(text="Test review", rating=5, user=user, place=place)
    session.add(review)
    session.commit()

    review_id = review.id
    assert session.query(Review).filter_by(id=review_id).first() is not None

    session.delete(review)
    session.commit()

    deleted_review = session.query(Review).filter_by(id=review_id).first()
    assert deleted_review is None
