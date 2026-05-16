from datetime import datetime
from pathlib import Path

import flask

from config import CAR_INDEX, ORDER_STATUSES, REVIEW_STATUSES
from database import get_db_connection, get_model_factors, get_settings_map
from api.auth import require_admin

admin_bp = flask.Blueprint("admin", __name__)


@admin_bp.get("/data")
def admin_data():
    db_path = Path(flask.current_app.root_path) / "users.db"
    _, error = require_admin(db_path)
    if error:
        return error

    settings = get_settings_map(db_path)
    factors = get_model_factors(db_path)
    with get_db_connection(db_path) as connection:
        orders_total = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        orders_paid = connection.execute("SELECT COUNT(*) FROM orders WHERE status = 'paid'").fetchone()[0]
        users_total = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        leads_total = connection.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        reviews_total = connection.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
        reviews_pending = connection.execute("SELECT COUNT(*) FROM reviews WHERE status = 'pending'").fetchone()[0]

    return flask.jsonify(
        {
            "settings": settings,
            "model_factors": factors,
            "stats": {
                "orders_total": orders_total,
                "orders_paid": orders_paid,
                "users_total": users_total,
                "leads_total": leads_total,
                "reviews_total": reviews_total,
                "reviews_pending": reviews_pending,
            },
        }
    )


@admin_bp.get("/leads")
def admin_leads():
    db_path = Path(flask.current_app.root_path) / "users.db"
    _, error = require_admin(db_path)
    if error:
        return error

    with get_db_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT l.id, l.full_name, l.contact, l.message, l.created_at, u.email AS user_email
            FROM leads l
            LEFT JOIN users u ON u.id = l.user_id
            ORDER BY l.id DESC
            LIMIT 50
            """
        ).fetchall()

    items = [
        {
            "id": row["id"],
            "full_name": row["full_name"],
            "contact": row["contact"],
            "message": row["message"],
            "created_at": row["created_at"],
            "user_email": row["user_email"],
        }
        for row in rows
    ]
    return flask.jsonify({"items": items})


@admin_bp.get("/reviews")
def admin_reviews():
    db_path = Path(flask.current_app.root_path) / "users.db"
    _, error = require_admin(db_path)
    if error:
        return error

    with get_db_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT r.id, r.rating, r.message, r.status, r.created_at, u.full_name, u.email
            FROM reviews r
            JOIN users u ON u.id = r.user_id
            ORDER BY r.id DESC
            LIMIT 50
            """
        ).fetchall()

    items = [
        {
            "id": row["id"],
            "rating": row["rating"],
            "message": row["message"],
            "status": row["status"],
            "created_at": row["created_at"],
            "full_name": row["full_name"],
            "email": row["email"],
        }
        for row in rows
    ]
    return flask.jsonify({"items": items})


@admin_bp.get("/orders")
def admin_orders():
    db_path = Path(flask.current_app.root_path) / "users.db"
    _, error = require_admin(db_path)
    if error:
        return error

    with get_db_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT o.id, o.model_id, o.engine_cc, o.vehicle_year, o.package, o.rating, o.no_claim_years,
                   o.price, o.monthly, o.car_photo_path, o.status, o.created_at,
                   u.full_name, u.email
            FROM orders o
            JOIN users u ON u.id = o.user_id
            ORDER BY o.id DESC
            LIMIT 50
            """
        ).fetchall()

    items = [
        {
            "id": row["id"],
            "model_id": row["model_id"],
            "model_name": CAR_INDEX.get(row["model_id"], {"name": {"uz": row["model_id"]}})["name"]["uz"],
            "engine_cc": row["engine_cc"],
            "year": row["vehicle_year"],
            "package": row["package"],
            "rating": row["rating"],
            "no_claim_years": row["no_claim_years"],
            "price": row["price"],
            "monthly": row["monthly"],
            "car_photo_path": row["car_photo_path"],
            "status": row["status"],
            "created_at": row["created_at"],
            "full_name": row["full_name"],
            "email": row["email"],
        }
        for row in rows
    ]
    return flask.jsonify({"items": items})


@admin_bp.post("/model-factor")
def update_model_factor():
    db_path = Path(flask.current_app.root_path) / "users.db"
    _, error = require_admin(db_path)
    if error:
        return error

    payload = flask.request.get_json(silent=True) or {}
    model_id = str(payload.get("model_id", "")).strip().lower()
    try:
        factor = float(payload.get("factor"))
    except (TypeError, ValueError):
        return flask.jsonify({"error": "Koeffitsient son bo'lishi kerak."}), 400

    if model_id not in CAR_INDEX:
        return flask.jsonify({"error": "Model topilmadi."}), 404
    if factor < 0.5 or factor > 2.5:
        return flask.jsonify({"error": "Koeffitsient 0.5 va 2.5 oralig'ida bo'lishi kerak."}), 400

    with get_db_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO model_factors (model_id, factor, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(model_id) DO UPDATE SET factor = excluded.factor, updated_at = excluded.updated_at
            """,
            (model_id, factor, datetime.utcnow().isoformat()),
        )
        connection.commit()

    return flask.jsonify({"message": "Model koeffitsienti yangilandi."})


@admin_bp.post("/settings")
def update_admin_settings():
    db_path = Path(flask.current_app.root_path) / "users.db"
    _, error = require_admin(db_path)
    if error:
        return error

    payload = flask.request.get_json(silent=True) or {}
    bot_token = str(payload.get("telegram_bot_token", "")).strip()
    chat_id = str(payload.get("telegram_chat_id", "")).strip()

    with get_db_connection(db_path) as connection:
        connection.execute(
            "INSERT INTO app_settings (key, value) VALUES ('telegram_bot_token', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (bot_token,),
        )
        connection.execute(
            "INSERT INTO app_settings (key, value) VALUES ('telegram_chat_id', ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (chat_id,),
        )
        connection.commit()

    return flask.jsonify({"message": "Admin sozlamalari saqlandi."})


@admin_bp.post("/orders/<int:order_id>/status")
def update_order_status(order_id: int):
    db_path = Path(flask.current_app.root_path) / "users.db"
    _, error = require_admin(db_path)
    if error:
        return error

    payload = flask.request.get_json(silent=True) or {}
    status = str(payload.get("status", "")).strip().lower()
    if status not in ORDER_STATUSES:
        return flask.jsonify({"error": "Status noto'g'ri."}), 400

    with get_db_connection(db_path) as connection:
        cursor = connection.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        connection.commit()

    if cursor.rowcount == 0:
        return flask.jsonify({"error": "Buyurtma topilmadi."}), 404

    return flask.jsonify({"message": "Buyurtma statusi yangilandi."})


@admin_bp.post("/reviews/<int:review_id>/status")
def update_review_status(review_id: int):
    db_path = Path(flask.current_app.root_path) / "users.db"
    _, error = require_admin(db_path)
    if error:
        return error

    payload = flask.request.get_json(silent=True) or {}
    status = str(payload.get("status", "")).strip().lower()
    if status not in REVIEW_STATUSES:
        return flask.jsonify({"error": "Status noto'g'ri."}), 400

    with get_db_connection(db_path) as connection:
        cursor = connection.execute("UPDATE reviews SET status = ? WHERE id = ?", (status, review_id))
        connection.commit()

    if cursor.rowcount == 0:
        return flask.jsonify({"error": "Review topilmadi."}), 404

    return flask.jsonify({"message": "Review statusi yangilandi."})
