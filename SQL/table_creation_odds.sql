CREATE TABLE odds (
race_ID VARCHAR(500) PRIMARY KEY,
horse_name VARCHAR(500) ,
bookmaker_id VARCHAR(500),
odds_decimal VARCHAR(500),
time_odds_captured TIMESTAMP,
odds_added_timestamp TIMESTAMP)