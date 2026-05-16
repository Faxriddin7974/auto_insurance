import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import flask
from werkzeug.security import check_password_hash, generate_password_hash

try:
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token as google_id_token
except ImportError:
    google_requests = None
    google_id_token = None

from config import GOOGLE_CLIENT_ID
from database import get_db_connection
from utils import validate_email

auth_bp = flask.Blueprint("auth", __name__)


def current_user(db_path: Path) -> dict | None:
    user_id = flask.session.get("user_id")
    if not user_id:
        return None
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        flask.session.clear()
        return None

    with get_db_connection(db_path) as connection:
        row = connection.execute(
            "SELECT id, full_name, email, is_admin FROM users WHERE id = ?",
            (user_id_int,),
        ).fetchone()

    if not row:
        flask.session.clear()
        return None

    user_data = {
        "id": row["id"],
        "name": row["full_name"],
        "email": row["email"],
        "is_admin": bool(row["is_admin"]),
    }

    if (
        flask.session.get("user_name") != user_data["name"]
        or flask.session.get("user_email") != user_data["email"]
        or bool(flask.session.get("is_admin", 0)) != user_data["is_admin"]
    ):
        set_session_user(user_data)

    return user_data


def set_session_user(user_data: dict) -> None:
    flask.session["user_id"] = int(user_data["id"])
    flask.session["user_name"] = str(user_data["name"])
    flask.session["user_email"] = str(user_data["email"])
    flask.session["is_admin"] = 1 if bool(user_data.get("is_admin")) else 0


def require_user(db_path: Path) -> tuple[dict | None, tuple[flask.Response, int] | None]:
    user = current_user(db_path)
    if not user:
        return None, (flask.jsonify({"error": "Avval tizimga kiring."}), 401)
    return user, None


def require_admin(db_path: Path) -> tuple[dict | None, tuple[flask.Response, int] | None]:
    user, error = require_user(db_path)
    if error:
        return None, error
    if not user or not user.get("is_admin"):
        return None, (flask.jsonify({"error": "Admin huquqi talab qilinadi."}), 403)
    return user, None


@auth_bp.get("/me")
def auth_me():
    from api.auth import current_user
    db_path = Path(flask.current_app.root_path) / "users.db"
    user = current_user(db_path)
    return flask.jsonify({"authenticated": bool(user), "user": user})


@auth_bp.post("/register")
def auth_register():
    db_path = Path(flask.current_app.root_path) / "users.db"
    payload = flask.request.get_json(silent=True) or {}
    full_name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))

    if len(full_name) < 2:
        return flask.jsonify({"error": "Ism kamida 2 ta belgidan iborat bo'lishi kerak."}), 400
    if not validate_email(email):
        return flask.jsonify({"error": "Email formati noto'g'ri."}), 400
    if len(password) < 6:
        return flask.jsonify({"error": "Parol kamida 6 ta belgidan iborat bo'lishi kerak."}), 400

    with get_db_connection(db_path) as connection:
        users_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        admin_count = connection.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1").fetchone()[0]
        is_admin = 1 if users_count == 0 or admin_count == 0 else 0
        try:
            cursor = connection.execute(
                "INSERT INTO users (full_name, email, password_hash, is_admin, created_at) VALUES (?, ?, ?, ?, ?)",
                (full_name, email, generate_password_hash(password), is_admin, datetime.utcnow().isoformat()),
            )
            connection.commit()
        except sqlite3.IntegrityError:
            return flask.jsonify({"error": "Bu email allaqachon ro'yxatdan o'tgan."}), 409

    user_data = {"id": cursor.lastrowid, "name": full_name, "email": email, "is_admin": bool(is_admin)}
    set_session_user(user_data)
    return flask.jsonify({"message": "Ro'yxatdan o'tish muvaffaqiyatli yakunlandi.", "user": user_data})


@auth_bp.post("/login")
def auth_login():
    db_path = Path(flask.current_app.root_path) / "users.db"
    payload = flask.request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))

    if not validate_email(email):
        return flask.jsonify({"error": "Email formati noto'g'ri."}), 400

    with get_db_connection(db_path) as connection:
        row = connection.execute(
            "SELECT id, full_name, email, password_hash, is_admin FROM users WHERE email = ?",
            (email,),
        ).fetchone()

    if not row or not check_password_hash(row["password_hash"], password):
        return flask.jsonify({"error": "Email yoki parol noto'g'ri."}), 401

    user_data = {
        "id": row["id"],
        "name": row["full_name"],
        "email": row["email"],
        "is_admin": bool(row["is_admin"]),
    }
    set_session_user(user_data)
    return flask.jsonify({"message": "Kirish muvaffaqiyatli amalga oshdi.", "user": user_data})


@auth_bp.post("/google-login")
def google_login():
    db_path = Path(flask.current_app.root_path) / "users.db"
    if not GOOGLE_CLIENT_ID:
        return flask.jsonify({"error": "Google login hali serverda sozlanmagan."}), 503
    if google_id_token is None or google_requests is None:
        return flask.jsonify({"error": "google-auth kutubxonasi o'rnatilmagan."}), 500

    payload = flask.request.get_json(silent=True) or {}
    credential = str(payload.get("credential") or flask.request.form.get("credential") or "").strip()
    if not credential:
        return flask.jsonify({"error": "Google credential topilmadi."}), 400

    try:
        idinfo = google_id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except ValueError:
        return flask.jsonify({"error": "Google ID tokenini tasdiqlab bo'lmadi."}), 401

    email = str(idinfo.get("email", "")).strip().lower()
    email_verified = bool(idinfo.get("email_verified"))
    google_sub = str(idinfo.get("sub", "")).strip()
    full_name = str(idinfo.get("name", "")).strip() or email

    if not email or not email_verified or not google_sub:
        return flask.jsonify({"error": "Google akkaunti ma'lumotlari yetarli emas."}), 400

    with get_db_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT id, full_name, email, is_admin
            FROM users
            WHERE google_sub = ? OR email = ?
            ORDER BY CASE WHEN google_sub = ? THEN 0 ELSE 1 END
            LIMIT 1
            """,
            (google_sub, email, google_sub),
        ).fetchone()

        if row:
            connection.execute(
                "UPDATE users SET full_name = ?, email = ?, google_sub = ? WHERE id = ?",
                (full_name, email, google_sub, row["id"]),
            )
            connection.commit()
            user_data = {
                "id": row["id"],
                "name": full_name,
                "email": email,
                "is_admin": bool(row["is_admin"]),
            }
        else:
            users_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            admin_count = connection.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1").fetchone()[0]
            is_admin = 1 if users_count == 0 or admin_count == 0 else 0
            cursor = connection.execute(
                """
                INSERT INTO users (full_name, email, password_hash, google_sub, is_admin, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    full_name,
                    email,
                    generate_password_hash(uuid4().hex),
                    google_sub,
                    is_admin,
                    datetime.utcnow().isoformat(),
                ),
            )
            connection.commit()
            user_data = {
                "id": cursor.lastrowid,
                "name": full_name,
                "email": email,
                "is_admin": bool(is_admin),
            }

    set_session_user(user_data)
    return flask.jsonify({"message": "Google orqali kirish muvaffaqiyatli amalga oshdi.", "user": user_data})


@auth_bp.post("/logout")
def auth_logout():
    flask.session.clear()
    return flask.jsonify({"message": "Chiqish bajarildi."})
