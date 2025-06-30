# __Test Log – Hbnb API__
This document records the performed API tests along with their outcomes.
---
## __Overview__
| Test # | Endpoint             | Method | Result  | Expected Response            | Actual Response | Failure Response          |
|--------|----------------------|--------|---------|------------------------------|-----------------|--------------------------|
| 1      | `/api/v1/users`      | POST   | Passed  | 201 Created                  | 201 OK          | 500 Internal Server Error |
| 2      | `/api/v1/users`      | POST   | Passed  | 400 (Invalid input)          | 400 OK          | 500 Internal Server Error |
| 3      | `/api/v1/users`      | POST   | Passed  | 409 (Email already exists)   | 409 OK          | 500 Internal Server Error |
| 4      | `/api/v1/users`      | GET    | Passed  | 200 OK                      | 200 OK          | 500 Internal Server Error |
| 5      | `/api/v1/users/<id>` | GET    | Passed  | 200 OK                      | 200 OK          | 500 Internal Server Error |
| 6      | `/api/v1/users/<id>` | GET    | Passed  | 404 (User not found)        | 404 OK          | 500 Internal Server Error |
| 7      | `/api/v1/users/<id>` | PUT    | Passed  | 200 OK                      | 200 OK          | 500 Internal Server Error |
| 8      | `/api/v1/users/<id>` | PUT    | Passed  | 400 (Invalid input)          | 400 OK          | 500 Internal Server Error |
| 9      | `/api/v1/users/<id>` | PUT    | Passed  | 404 (User not found)        | 404 OK          | 500 Internal Server Error |
| 10     | `/api/v1/users/<id>` | PUT    | Passed  | 409 (Email conflict)         | 409 OK          | 500 Internal Server Error |
| 11     | `/api/v1/places`     | POST   | Passed  | 201 Created                  | 201 OK          | 500 Internal Server Error |
| 12     | `/api/v1/places`     | POST   | Passed  | 400 (Invalid input)          | 400 OK          | 500 Internal Server Error |
| 13     | `/api/v1/places`     | POST   | Passed  | 404 (User not found)        | 404 OK          | 500 Internal Server Error |
| 14     | `/api/v1/places`     | GET    | Passed  | 200 OK                      | 200 OK          | 500 Internal Server Error |
| 15     | `/api/v1/places/<id>`| GET    | Passed  | 200 OK                      | 200 OK          | 500 Internal Server Error |
| 16     | `/api/v1/places/<id>`| GET    | Passed  | 404 (Place not found)       | 404 OK          | 500 Internal Server Error |
| 17     | `/api/v1/places/<id>`| PUT    | Passed  | 200 OK                      | 200 OK          | 500 Internal Server Error |
| 18     | `/api/v1/places/<id>`| PUT    | Passed  | 400 (Invalid input)          | 400 Bad Request | 500 Internal Server Error |
| 19     | `/api/v1/places/<id>`| PUT    | Passed  | 404 (Place not found)       | 404 OK          | 500 Internal Server Error |
| 20     | `/api/v1/amenities`  | POST   | Passed  | 201 Created                  | 201 OK          | 500 Internal Server Error |
| 21     | `/api/v1/amenities`  | POST   | Passed  | 400 (Invalid input)          | 400 OK          | 500 Internal Server Error |
| 22     | `/api/v1/amenities`  | GET    | Passed  | 200 OK                      | 200 OK          | 500 Internal Server Error |
| 23     | `/api/v1/amenities/<id>`| GET | Passed  | 200 OK                      | 200 OK          | 500 Internal Server Error |
| 24     | `/api/v1/amenities/<id>`| GET | Passed  | 404 (Amenity not found)     | 404 OK          | 500 Internal Server Error |
| 25     | `/api/v1/amenities/<id>`| PUT | Passed  | 200 OK                      | 200 OK          | 500 Internal Server Error |
| 26     | `/api/v1/amenities/<id>`| PUT | Passed  | 400 (Invalid input)          | 400 OK          | 500 Internal Server Error |
| 27     | `/api/v1/amenities/<id>`| PUT | Passed  | 404 (Amenity not found)     | 404 OK          | 500 Internal Server Error |
| 28     | `/api/v1/reviews`    | POST   | Passed  | 201 Created                  | 201 OK          | 500 Internal Server Error |
| 29     | `/api/v1/reviews`    | POST   | Passed  | 400 (Invalid input)          | 400 OK          | 500 Internal Server Error |
| 30     | `/api/v1/reviews`    | GET    | Passed  | 200 OK                      | 200 OK          | 500 Internal Server Error |
| 31     | `/api/v1/reviews/<id>`| GET   | Passed  | 200 OK                      | 200 OK          | 500 Internal Server Error |
| 32     | `/api/v1/reviews/<id>`| GET   | Passed  | 404 (Review not found)      | 404 OK          | 500 Internal Server Error |
| 33     | `/api/v1/reviews/<id>`| PUT   | Passed  | 200 OK                      | 200 OK          | 500 Internal Server Error |
| 34     | `/api/v1/reviews/<id>`| PUT   | Passed  | 400 (Invalid input)          | 400 OK          | 500 Internal Server Error |
| 35     | `/api/v1/reviews/<id>`| PUT   | Passed  | 404 (Review not found)      | 404 OK          | 500 Internal Server Error |
| 36     | `/api/v1/reviews/<id>`| DELETE| Passed  | 200 OK                      | 200 OK          | 500 Internal Server Error |
| 37     | `/api/v1/reviews/<id>`| DELETE| Passed  | 404 (Review not found)      | 404 OK          | 500 Internal Server Error |
---
## __Test Details__
### __Test 1__
- **Endpoint**: `/api/v1/users`
- **Method**: POST
- **Payload**:
```json
{
  "first_name": "Argon",
  "last_name": "Sword",
  "email": "test@mail.com",
  "password": "1234"
}
```
- Expected: 201 Created with returned user ID.
- Actual: 201 OK.
- Status: Succeeded.
### __Test 3__
- **Endpoint**: `/api/v1/reviews/<id>`
- **Method**: DELETE
- Expected: 200 OK.
- Actual: 200 OK.
- Status: Succeeded.
### __Test 4__
- **Endpoint**: `/api/v1/reviews/<id>`
- **Method**: PUT
- **Payload**:
```json
{
  "text": "",
  "rating": 4
}
```
- Expected: 400 Bad request (Invalid input data).
- Actual: 400 Bad request.
- Status: Succeeded.
### __Test 6__
- **Endpoint**: `/api/v1/users/<id>`
- **Method**: GET
- Expected: 404 Not found (User not found).
- Actual: 404 OK.
- Status: Succeeded.
### __Test 7__
- **Endpoint**: `/api/v1/users/<id>`
- **Method**: PUT
- **Payload**:
```json
{
  "first_name": "Amy",
  "last_name": "Shasse",
  "email": "test@mail.com",
}
```
- Expected: 200 OK with returned user ID.
- Actual: 200 OK.
- Status: Succeeded.
### __Test 8__
- **Endpoint**: `/api/v1/users/<id>`
- **Method**: PUT
- **Payload**:
```json
{
  "first_name": "",
  "last_name": "Shasse",
  "email": "test@mail.com",
}
```
- Expected: 400 Bad request (Invalid input data).
- Actual: 400 OK.
- Status: Succeeded.
### __Test 11__
- **Endpoint**: `/api/v1/places`
- **Method**: POST
- **Payload**:
```json
{
  "title": "Cozy Appart",
  "description": "Good",
  "price": 100.0,
  "latitude": 37.7749,
  "longitude": -122.4194,
  "owner_id": <id>
}
```
- Expected: 201 Created with returned place ID.
- Actual: 201 OK.
- Status: Succeeded.
### __Test 13__
- **Endpoint**: `/api/v1/places`
- **Method**: POST
- **Payload**:
```json
{
  "title": "Cozy Appart",
  "description": "Good",
  "price": 100.0,
  "latitude": 37.7749,
  "longitude": -122.4194,
  "owner_id": <id>
}
```
- Expected: 404 Not found (Place not found).
- Actual: 404 OK.
- Status: Succeeded.
### __Test 15__
- **Endpoint**: `/api/v1/places`
- **Method**: GET
- Expected: 200 OK with returned place list.
- Actual: 200 OK.
- Status: Succeeded.
### __Test 18__
- **Endpoint**: `/api/v1/places/<id>`
- **Method**: PUT
- **Payload**:
```json
{
  "title": "Cozy Appart",
  "description": "Good",
  "price": "0.0",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "owner_id": <user_id>
}
```
- Expected: 400 Bad request (Invalid input data).
- Actual: 400 Bad request.
- Status: Succeeded.
### __Test 20__
- **Endpoint**: `/api/v1/amenities`
- **Method**: POST
- **Payload**:
```json
{
  "name": "Wi-Fi"
}
```
- Expected: 201 Created with returned amenity ID.
- Actual: 201 OK.
- Status: Succeeded.
### __Test 24__
- **Endpoint**: `/api/v1/amenities/<id>`
- **Method**: GET
- Expected: 404 Not found (Amenity not found).
- Actual: 404 OK.
- Status: Succeeded.
### __Test 27__
- **Endpoint**: `/api/v1/amenities/<id>`
- **Method**: PUT
- **Payload**:
```json
{
  "name": ""
}
```
- Expected: 400 Bad request (Invalid input data).
- Actual: 400 Bad request.
- Status: Succeeded.
### __Test 28__
- **Endpoint**: `/api/v1/reviews`
- **Method**: POST
- **Payload**:
```json
{
  "text": "Great place to stay!",
  "rating": 5,
  "user_id": <id>,
  "place_id": <id>
}
```
- Expected: 201 Created with returned review ID.
- Actual: 201 OK.
- Status: Succeeded.
### __Test 32__
- **Endpoint**: `/api/v1/reviews/<id>`
- **Method**: GET
- Expected: 404 Not found (Review not found).
- Actual: 404 OK.
- Status: Succeeded.
### __Test 35__
- **Endpoint**: `/api/v1/users`
- **Method**: GET
- Expected: 200 OK with returned user list.
- Actual: 200 OK.
- Status: Succeeded.
### __Test 36__
- **Endpoint**: `/api/v1/users`
- **Method**: POST
- **Payload**:
```json
{
  "first_name": "Joe",
  "last_name": "Doe",
  "email": "testmail.com",
  "password": "1234"
}
```
- Expected: 409 Conflict (Email already registered).
- Actual: 409 Conflict.
- Status: Succeeded.









