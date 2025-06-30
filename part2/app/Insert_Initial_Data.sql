-- Admin user 
INSERT INTO "user" (id, first_name, last_name, email, password, is_admin)
VALUES (
  '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
  'Admin',
  'HBnB',
  'admin@hbnb.io',
  '$2b$12$R3mE0V9G3uMJjYVmoxbQXeW6O3A7fAXgFS2hEjGmkgN/O7W7qPcvS',
  TRUE
);

-- Amenities
INSERT INTO amenity (id, name) VALUES
  ('a6e61d3f-71dc-421e-94ce-95c3ad95a65b', 'WiFi'),
  ('21bdb6a2-b238-4a6e-bb1a-3e12d4308b9b', 'Swimming Pool'),
  ('4bbd70e3-c0f7-45d9-a943-c2aa2338f17f', 'Air Conditioning');
