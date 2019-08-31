SET SQL_MODE='ALLOW_INVALID_DATES';
CREATE TABLE races (
race_ID VARCHAR(500) PRIMARY KEY,
venue_name VARCHAR(500) ,
race_time TIMESTAMP,
number_starters INTEGER,
class VARCHAR(500),
prize VARCHAR(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
distance VARCHAR(500),
going_description VARCHAR(500),
race_added_timestamp TIMESTAMP)