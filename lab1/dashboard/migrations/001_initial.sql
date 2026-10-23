-- Начальная схема SQLite. Создаёт таблицы при первом запуске.
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    status VARCHAR NOT NULL DEFAULT 'В сроке'
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    role VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR,
    status VARCHAR NOT NULL DEFAULT 'В работе',
    deadline DATETIME,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    user_id INTEGER REFERENCES users(id)
);
