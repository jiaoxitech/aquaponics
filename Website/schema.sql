CREATE TABLE sensor_log (sensor TEXT, timestamp DATE DEFAULT (datetime('now','localtime')), value TEXT);
CREATE INDEX sensor_idx ON sensor_log (sensor, timestamp);

CREATE TABLE admin (name TEXT, value TEXT);
INSERT INTO admin (name, value) VALUES ('admin_password', 'jiaoxi'), ('monitor_password','aquaponics');

CREATE TABLE admin_log (timestamp DATE DEFAULT (datetime('now','localtime')), entry TEXT);

CREATE TABLE relays (relay INT, status INT, timeOn INT, timeOff INT, allDay INT);
INSERT INTO relays (relay, status, timeOn, timeOff, allDay) VALUES (1, 0, 0, 0, 1), (2, 0, 8, 16, 0), (3, 0, 8, 16, 0), (4, 0, 8, 16, 0), (5, 0, 8, 16, 0), (6, 0, 8, 16, 0), (7, 0, 8, 16, 0), (8, 0, 8, 16, 0);
