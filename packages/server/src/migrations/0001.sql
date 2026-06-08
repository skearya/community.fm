PRAGMA user_version = 1;

CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  lastfm_username TEXT NOT NULL,
  lastfm_session TEXT NOT NULL
);
