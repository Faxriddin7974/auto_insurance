from datetime import datetime
from pathlib import Path

import flask

from config import REVIEW_STATUSES
from database import get_db_connection
from api.auth import require_user

reviews_bp = flask.Blueprint("reviews", __name__)


@reviews_bp.get("")
def api_reviews_list():
    db_path = Path(flask.current_app.root_path) / "users.db"
    from api.auth import current_user
    user = current_user(db_path)
    with get_db_connection(db_path) as connection:
        if user:
            rows = connection.execute(
                """
                SELECT r.id, r.rating, r.message, r.status, r.created_at, u.full_name
                FROM reviews r
                JOIN users u ON u.id = r.user_id
                WHERE r.status = 'approved' OR r.user_id = ?
                ORDER BY r.created_at DESC
                LIMIT 50
                """,
                (int(user["id"]),),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT r.id, r.rating, r.message, r.status, r.created_at, u.full_name
                FROM reviews r
                JOIN users u ON u.id = r.user_id
                WHERE r.status = 'approved'
                ORDER BY r.created_at DESC
                LIMIT 50
                """
            ).fetchall()

    items = [
        {
            "id": row["id"],
            "author": row["full_name"],
            "rating": row["rating"],
            "message": row["message"],
            "status": row["status"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return flask.jsonify({"items": items})


@reviews_bp.post("")
def api_reviews_create():
    db_path = Path(flask.current_app.root_path) / "users.db"
    user, error = require_user(db_path)
    if error:
        return error

    payload = flask.request.get_json(silent=True) or {}
    try:
        rating = int(payload.get("rating"))
    except (TypeError, ValueError):
        return flask.jsonify({"error": "Reyting noto'g'ri."}), 400
    message = str(payload.get("message", "")).strip()

    if rating < 1 or rating > 5:
        return flask.jsonify({"error": "Reyting 1 dan 5 gacha bo'lishi kerak."}), 400
    if len(message) < 10:
        return flask.jsonify({"error": "Fikr kamida 10 ta belgidan iborat bo'lishi kerak."}), 400

    created_at = datetime.utcnow().isoformat()
    with get_db_connection(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO reviews (user_id, rating, message, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
            (int(user["id"]), rating, message, created_at),
        )
        connection.commit()

    return flask.jsonify(
        {
            "message": "Fikringiz qabul qilindi. Admin tasdiqlaganidan so'ng saytda ko'rinadi.",
            "review": {"id": cursor.lastrowid, "rating": rating, "message": message, "status": "pending", "created_at": created_at},
        }
    )
