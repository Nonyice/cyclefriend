CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE cycles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    last_period DATE,
    cycle_length INTEGER
);
