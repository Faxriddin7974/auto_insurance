import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from calculators import PremiumCalculator


class DatabaseManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def save_order(self, data: str) -> None:
        with self.get_connection() as conn:
            conn.execute("INSERT INTO orders (data, created_at) VALUES (?, ?)", (data, datetime.utcnow().isoformat()))
            conn.commit()

    def get_orders(self) -> List[str]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT data FROM orders ORDER BY id DESC LIMIT 10").fetchall()
        return [row["data"] for row in rows]


def get_db_connection(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def table_has_column(connection: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(row[1] == column_name for row in rows)


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                google_sub TEXT,
                is_admin INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        if not table_has_column(connection, "users", "is_admin"):
            connection.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0")
        if not table_has_column(connection, "users", "google_sub"):
            connection.execute("ALTER TABLE users ADD COLUMN google_sub TEXT")

        admin_count = connection.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1").fetchone()[0]
        if admin_count == 0:
            first_user = connection.execute("SELECT id FROM users ORDER BY id ASC LIMIT 1").fetchone()
            if first_user:
                connection.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (first_user[0],))

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                model_id TEXT NOT NULL,
                engine_cc INTEGER NOT NULL,
                vehicle_year INTEGER NOT NULL,
                package TEXT NOT NULL,
                rating TEXT NOT NULL,
                no_claim_years INTEGER NOT NULL,
                price INTEGER NOT NULL,
                monthly INTEGER NOT NULL,
                car_photo_path TEXT,
                status TEXT NOT NULL DEFAULT 'submitted',
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        if not table_has_column(connection, "orders", "car_photo_path"):
            connection.execute("ALTER TABLE orders ADD COLUMN car_photo_path TEXT")

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                model_id TEXT NOT NULL,
                engine_cc INTEGER NOT NULL,
                vehicle_year INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS model_factors (
                model_id TEXT PRIMARY KEY,
                factor REAL NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                full_name TEXT NOT NULL,
                contact TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                message TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        for key in ("telegram_bot_token", "telegram_chat_id"):
            connection.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES (?, ?)", (key, ""))

        now = datetime.utcnow().isoformat()
        for model_id, factor in PremiumCalculator.MODEL_FACTORS.items():
            connection.execute(
                "INSERT OR IGNORE INTO model_factors (model_id, factor, updated_at) VALUES (?, ?, ?)",
                (model_id, factor, now),
            )

        connection.commit()


def get_model_factors(db_path: Path) -> dict[str, float]:
    with get_db_connection(db_path) as connection:
        rows = connection.execute("SELECT model_id, factor FROM model_factors").fetchall()
    factors: dict[str, float] = {}
    for row in rows:
        try:
            factors[row["model_id"]] = float(row["factor"])
        except (TypeError, ValueError):
            continue
    return factors


def get_settings_map(db_path: Path) -> dict[str, str]:
    with get_db_connection(db_path) as connection:
        rows = connection.execute("SELECT key, value FROM app_settings").fetchall()
    return {row["key"]: row["value"] for row in rows}
