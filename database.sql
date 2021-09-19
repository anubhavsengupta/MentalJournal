CREATE table users (id INTEGER, username TEXT, hash TEXT, PRIMARY KEY(id));
CREATE table journal (user_id INTEGER, mood INTEGER, number INTEGER, FOREIGN KEY (user_id) REFERENCES users(id));