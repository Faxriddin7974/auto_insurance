from datetime import datetime
from pathlib import Path

import flask

from database import get_db_connection
from api.auth import current_user

contact_bp = flask.Blueprint("contact", __name__)


@contact_bp.post("/contact")
def api_contact():
    db_path = Path(flask.current_app.root_path) / "users.db"
    payload = flask.request.get_json(silent=True) or {}
    full_name = str(payload.get("name", "")).strip()
    contact = str(payload.get("contact", "")).strip()
    message = str(payload.get("message", "")).strip()

    if len(full_name) < 2:
        return flask.jsonify({"error": "Ism kamida 2 ta belgidan iborat bo'lishi kerak."}), 400
    if len(contact) < 3:
        return flask.jsonify({"error": "Kontakt ma'lumotini kiriting."}), 400
    if len(message) < 10:
        return flask.jsonify({"error": "Xabar kamida 10 ta belgidan iborat bo'lishi kerak."}), 400

    user = current_user(db_path)
    user_id = int(user["id"]) if user else None
    created_at = datetime.utcnow().isoformat()

    with get_db_connection(db_path) as connection:
        connection.execute(
            "INSERT INTO leads (user_id, full_name, contact, message, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, full_name, contact, message, created_at),
        )
        connection.commit()

    return flask.jsonify({"message": "Xabaringiz qabul qilindi. Tez orada bog'lanamiz."})
