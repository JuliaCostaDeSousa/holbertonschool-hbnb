-- Insert data for admin user
INSERT INTO users (id, email, first_name, last_name, password, is_admin)
VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'admin@hbnb.io',
    'Admin',
    'HBnB',
    '$2b$12$wHTbB2lfTqqVZbEN/1Jgfe9zqgsv0rUZr58AeC8/rYcHJhQ7nMLcC',
    TRUE
);

-- Insert data for amenity
INSERT INTO amenities (id, name)
VALUES 
    (UUID(), 'WiFi'),
    (UUID(), 'Swimming Pool'),
    (UUID(), 'Air Conditioning');