import json
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import flask

from config import CAR_INDEX, ORDER_STATUSES
from database import get_db_connection, get_settings_map
from models import ValidationError
from utils import (
    build_simple_pdf,
    calculate_quote,
    format_driver_rating_uz,
    format_order_status_uz,
    format_package_uz,
    normalize_car_photo_path,
)
from api.auth import current_user, require_user

orders_bp = flask.Blueprint("orders", __name__)


def get_order_if_accessible(order_id: int, user: dict, db_path: Path):
    with get_db_connection(db_path) as connection:
        if user.get("is_admin"):
            row = connection.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        else:
            row = connection.execute("SELECT * FROM orders WHERE id = ? AND user_id = ?", (order_id, user["id"])).fetchone()
    return row


@orders_bp.post("")
def create_order():
    db_path = Path(flask.current_app.root_path) / "users.db"
    user, error = require_user(db_path)
    if error:
        return error

    payload = flask.request.get_json(silent=True) or {}
    try:
        car_photo_path = normalize_car_photo_path(payload.get("car_photo_path"), flask.current_app.root_path)
        premium_input, quote = calculate_quote(payload, db_path)
    except ValidationError as exc:
        return flask.jsonify({"error": str(exc)}), 400

    with get_db_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO orders (
                user_id, model_id, engine_cc, vehicle_year, package, rating, no_claim_years,
                price, monthly, car_photo_path, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user["id"],
                premium_input.model_id,
                premium_input.engine_cc,
                premium_input.year,
                premium_input.package,
                premium_input.rating,
                premium_input.no_claim_years,
                int(quote["price"]),
                int(quote["monthly"]),
                car_photo_path,
                "submitted",
                datetime.utcnow().isoformat(),
            ),
        )
        connection.commit()

    return flask.jsonify(
        {
            "message": "Buyurtma yaratildi.",
            "order": {
                "id": cursor.lastrowid,
                "status": "submitted",
                "model_id": premium_input.model_id,
                "model_name": CAR_INDEX[premium_input.model_id]["name"]["uz"],
                "engine_cc": premium_input.engine_cc,
                "year": premium_input.year,
                "price": quote["price"],
                "monthly": quote["monthly"],
                "car_photo_path": car_photo_path,
            },
        }
    )


@orders_bp.get("")
def list_orders():
    db_path = Path(flask.current_app.root_path) / "users.db"
    user, error = require_user(db_path)
    if error:
        return error

    with get_db_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT id, model_id, engine_cc, vehicle_year, package, rating, no_claim_years,
                   price, monthly, car_photo_path, status, created_at
            FROM orders
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user["id"],),
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
        }
        for row in rows
    ]
    return flask.jsonify({"items": items})


@orders_bp.post("/<int:order_id>/pay")
def pay_order(order_id: int):
    db_path = Path(flask.current_app.root_path) / "users.db"
    user, error = require_user(db_path)
    if error:
        return error
    row = get_order_if_accessible(order_id, user, db_path)
    if not row:
        return flask.jsonify({"error": "Buyurtma topilmadi."}), 404

    if row["status"] == "paid":
        return flask.jsonify({"message": "Buyurtma allaqachon to'langan.", "status": "paid"})

    with get_db_connection(db_path) as connection:
        connection.execute("UPDATE orders SET status = 'paid' WHERE id = ?", (order_id,))
        connection.commit()

    return flask.jsonify({"message": "To'lov tasdiqlandi.", "status": "paid"})


@orders_bp.get("/<int:order_id>/pdf")
def order_pdf(order_id: int):
    db_path = Path(flask.current_app.root_path) / "users.db"
    user, error = require_user(db_path)
    if error:
        return error
    row = get_order_if_accessible(order_id, user, db_path)
    if not row:
        return flask.jsonify({"error": "Buyurtma topilmadi."}), 404

    model_name = CAR_INDEX.get(row["model_id"], {"name": {"uz": row["model_id"]}})["name"]["uz"]
    client_name = user["name"]
    client_email = user["email"]
    if row["user_id"] != user["id"]:
        with get_db_connection(db_path) as connection:
            owner_row = connection.execute(
                "SELECT full_name, email FROM users WHERE id = ?",
                (row["user_id"],),
            ).fetchone()
        if owner_row:
            client_name = owner_row["full_name"]
            client_email = owner_row["email"]

    lines = [
        "AvtoSugurta Pro - Buyurtma cheki",
        f"Buyurtma raqami: {row['id']}",
        f"Holati: {format_order_status_uz(row['status'])}",
        f"Sana: {row['created_at']}",
        f"Mijoz: {client_name} ({client_email})",
        f"Avtomobil: {model_name}",
        f"Dvigatel hajmi: {row['engine_cc']} sm3",
        f"Ishlab chiqarilgan yil: {row['vehicle_year']}",
        f"Paket: {format_package_uz(row['package'])}",
        f"Haydovchi toifasi: {format_driver_rating_uz(row['rating'])}",
        f"Avariyasiz yillar: {row['no_claim_years']}",
        f"Yillik sug'urta narxi: {row['price']} UZS",
        f"Oylik taxminiy to'lov: {row['monthly']} UZS",
        f"Mashina rasmi: {'Biriktirilgan' if row['car_photo_path'] else 'Yoq'}",
    ]
    pdf_bytes = build_simple_pdf(lines)
    return flask.Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=order_{order_id}.pdf"},
    )


@orders_bp.post("/<int:order_id>/send-telegram")
def send_order_to_telegram(order_id: int):
    db_path = Path(flask.current_app.root_path) / "users.db"
    user, error = require_user(db_path)
    if error:
        return error
    row = get_order_if_accessible(order_id, user, db_path)
    if not row:
        return flask.jsonify({"error": "Buyurtma topilmadi."}), 404

    settings = get_settings_map(db_path)
    bot_token = settings.get("telegram_bot_token", "").strip()
    chat_id = settings.get("telegram_chat_id", "").strip()
    if not bot_token or not chat_id:
        return flask.jsonify({"error": "Telegram token/chat_id admin panelda sozlanmagan."}), 400

    model_name = CAR_INDEX.get(row["model_id"], {"name": {"uz": row["model_id"]}})["name"]["uz"]
    message = (
        "Yangi buyurtma\n"
        f"Order ID: {row['id']}\n"
        f"Mijoz: {user['name']} ({user['email']})\n"
        f"Model: {model_name}\n"
        f"Dvigatel: {row['engine_cc']} sm3\n"
        f"Yil: {row['vehicle_year']}\n"
        f"Premium: {row['price']} UZS\n"
        f"Status: {row['status']}\n"
        f"Mashina rasmi: {'biriktirilgan' if row['car_photo_path'] else 'yoq'}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    req = urllib.request.Request(
        url,
        data=urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode("utf-8"),
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as exc:
        return flask.jsonify({"error": f"Telegramga yuborishda xatolik: {exc}"}), 502

    if not result.get("ok"):
        return flask.jsonify({"error": result.get("description", "Telegram API xatosi")}), 400

    return flask.jsonify({"message": "Buyurtma Telegramga yuborildi."})
