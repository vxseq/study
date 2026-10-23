"""Простая миграция для SQLite: python migrate.py."""

import os
import sqlite3
from pathlib import Path


DB_URL = os.getenv("DATABASE_URL", "sqlite:///./dashboard.db")


def main():
    if not DB_URL.startswith("sqlite:///"):
        raise SystemExit("Миграция поддерживает только SQLite")

    path = DB_URL.removeprefix("sqlite:///")
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as connection:
        connection.execute("PRAGMA foreign_keys=ON")
        script = (Path(__file__).parent / "migrations/001_initial.sql").read_text(
            encoding="utf-8"
        )
        connection.executescript(script)

        # При обновлении самой ранней версии проекта добавляем новые поля.
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(tasks)")
        }
        if "deadline" not in columns:
            connection.execute("ALTER TABLE tasks ADD COLUMN deadline DATETIME")
        if "user_id" not in columns:
            connection.execute("ALTER TABLE tasks ADD COLUMN user_id INTEGER REFERENCES users(id)")
        connection.commit()
    print("Структура базы данных готова.")


if __name__ == "__main__":
    main()
