# ___HBnB Project___
## ___Project Structure___
```
.
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       ├── places.py
│   │       ├── reviews.py
│   │       └── amenities.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── user.py
│   │   ├── place.py
│   │   ├── review.py
│   │   ├── amenity.py
│   │   └── engine/
│   │       ├── __init__.py
│   │       ├── file_storage.py
│   │       └── db_storage.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── facade.py
│   │   ├── user_service.py        
│   │   └── place_service.py         
│   └── persistence/
│       ├── __init__.py
│       ├── repository.py
│       └── user_repository.py       
├── run.py
├── config.py
├── requirements.txt
└── README.md

```
## ___Installing Dependencies___
To install the required packages, run the following command in your terminal:
```bash
pip install -r requirements.txt
```
## ___Business Logic Layer___
The business logic layer is responsible for enforcing the business rules that govern the platform's operation. It is independent of the API (Flask) and database layers, allowing for greater modularity, testability, and code clarity.
### ___Entities and their responsibilities___
#### __User__
Represents an individual registered on the platform.
_Attributes:_
- `id` (str): Unique identifier.
- `first_name` (str): First name (required, max. 50 characters).
- `last_name` (str): Last name (required, max. 50 characters).
- `email` (str): Unique and valid email address.
- `is_admin` (bool): Admin role (default: False).
- `created_at` / `updated_at` (datetime)
_Responsibilities:_
- Manage identity data.
- Verify email uniqueness and validity.
- Identify administrator users.
- Be associated with created locations and
reviews.
_Example of use:_
```python
user = User(
    id="u001",
    first_name="Ping",
    last_name="Pong",
    email="alice@example.com"
)
print(user.email)        # cesar@example.com
print(user.is_admin)     # False
```
#### __Place__
Represents a property available for booking.
_Attributes:_
- `id` (str): Unique identifier.
- `title` (str): Title (required, max. 100 characters).
- `description` (str): Description of the property.
- `price` (float): Price per night (positive).
- `latitude` / `longitude` (float): Geographic coordinates.
- `owner` (User): Owner user.
- `created_at` / `updated_at` (datetime)
_Responsibilities:_
- Validate geographic coordinates and price.
- Be associated with a valid owner.
- Be listed, filtered, or rated.
_Example of use:_
```python
place = Place(
    id="p002",
    title="villa in Monaco",
    description="Ideal for a weekend.",
    price=520.0,
    latitude=78.8676,
    longitude=7.3432,
    owner=user
)
print(place.title)       # villa in Monaco
print(place.price)       # 520.0
```
#### __Review__
Represents a user's rating of a place.
_Attributes:_
- `id` (str): Unique identifier.
- `text` (str): Content (required).
- `rating` (int): Rating between 1 and 5.
- `place` (Place): Location concerned.
- `user` (User): Author of the review.
- `created_at` / `updated_at` (datetime)
_Responsibilities:_
- Validate that the rating is between 1 and 5.
- Be connected to an existing user and place.
- Contribute to a place's reputation.
_Example of use:_
```python
review = Review(
    id="r001",
    text="Very expensive.",
    rating=3,
    place=place,
    user=user
)
print(review.rating)         # 5
print(review.place.title)    # villa in Monaco
```
#### __Amenity__
Represents an item of equipment or service associated with a location (e.g., Wi-Fi, Parking, Pool).
_Attributes:_
- `id` (str): Unique identifier.
- `name` (str): Name of the item (required, max. 50 characters).
- `created_at` / `updated_at` (datetime)
_Responsibilities:_
- Be linked to one or more locations.
- Allows filtering of locations by equipment.
_Example of use:_
```python
wifi = Amenity(id="b566", name="Wi-Fi")
print(wifi.name)  # Wi-Fi
#Alcinoe Romanelli
#Julia Coscadesousa
