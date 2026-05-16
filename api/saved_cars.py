from datetime import datetime
from pathlib import Path

import flask

from api.auth import require_user
from config import CAR_INDEX
from database import get_db_connection
from models import ValidationError, validate_vehicle_selection

saved_cars_bp = flask.Blueprint("saved_cars", __name__)


def _build_saved_car_title(model_id: str, year: int, engine_cc: int) -> str:
    model_name = CAR_INDEX.get(model_id, {"name": {"uz": model_id}})["name"]["uz"]
    return f"{model_name} - {year} - {engine_cc} sm3"


@saved_cars_bp.get("/saved-cars")
def list_saved_cars():
    db_path = Path(flask.current_app.root_path) / "users.db"
    user, error = require_user(db_path)
    if error:
        return error

    with get_db_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT id, model_id, engine_cc, vehicle_year, title, created_at
            FROM saved_cars
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user["id"],),
        ).fetchall()

    items = [
        {
            "id": row["id"],
            "model_id": row["model_id"],
            "engine_cc": row["engine_cc"],
            "year": row["vehicle_year"],
            "title": row["title"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return flask.jsonify({"items": items})


@saved_cars_bp.post("/saved-cars")
def create_saved_car():
    db_path = Path(flask.current_app.root_path) / "users.db"
    user, error = require_user(db_path)
    if error:
        return error

    payload = flask.request.get_json(silent=True) or {}
    model_id = str(payload.get("model_id", "")).strip().lower()

    try:
        engine_cc = int(payload.get("engine"))
        year = int(payload.get("year"))
        validate_vehicle_selection(model_id=model_id, engine_cc=engine_cc, year=year)
    except (TypeError, ValueError) as exc:
        return flask.jsonify({"error": "Saqlash uchun yuborilgan ma'lumot noto'g'ri."}), 400
    except ValidationError as exc:
        return flask.jsonify({"error": str(exc)}), 400

    title = _build_saved_car_title(model_id, year, engine_cc)

    with get_db_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO saved_cars (user_id, model_id, engine_cc, vehicle_year, title, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user["id"], model_id, engine_cc, year, title, datetime.utcnow().isoformat()),
        )
        connection.commit()

    return flask.jsonify(
        {
            "message": "Mashina saqlandi.",
            "item": {
                "id": cursor.lastrowid,
                "model_id": model_id,
                "engine_cc": engine_cc,
                "year": year,
                "title": title,
            },
        }
    )


@saved_cars_bp.delete("/saved-cars/<int:saved_id>")
def delete_saved_car(saved_id: int):
    db_path = Path(flask.current_app.root_path) / "users.db"
    user, error = require_user(db_path)
    if error:
        return error

    with get_db_connection(db_path) as connection:
        cursor = connection.execute(
            "DELETE FROM saved_cars WHERE id = ? AND user_id = ?",
            (saved_id, user["id"]),
        )
        connection.commit()

    if cursor.rowcount == 0:
        return flask.jsonify({"error": "Saqlangan mashina topilmadi."}), 404

    return flask.jsonify({"message": "Saqlangan mashina o'chirildi."})
