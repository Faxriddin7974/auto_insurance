from datetime import datetime
from pathlib import Path

import flask

from config import CAR_INDEX, TOP_CARS
from database import get_db_connection, get_model_factors
from models import ValidationError
from utils import calculate_quote, normalize_car_photo_path, save_uploaded_car_photo

cars_bp = flask.Blueprint("cars", __name__)


@cars_bp.get("/car-data")
def car_data():
    current_year = datetime.now().year
    db_path = Path(flask.current_app.root_path) / "users.db"
    return flask.jsonify(
        {
            "cars": TOP_CARS,
            "year_min": 1980,
            "year_max": current_year + 1,
            "current_year": current_year,
            "model_factors": get_model_factors(db_path),
        }
    )


@cars_bp.post("/api/car-photo")
def upload_car_photo():
    file_storage = flask.request.files.get("photo")
    if not file_storage:
        return flask.jsonify({"error": "Rasm faylini tanlang."}), 400

    try:
        car_upload_dir = Path(flask.current_app.static_folder) / "uploads" / "cars"
        photo_path = save_uploaded_car_photo(file_storage, car_upload_dir)
    except ValidationError as exc:
        return flask.jsonify({"error": str(exc)}), 400

    return flask.jsonify({"message": "Rasm yuklandi.", "photo_path": photo_path})


@cars_bp.post("/calculate")
def calculate():
    db_path = Path(flask.current_app.root_path) / "users.db"
    payload = flask.request.get_json(silent=True)
    try:
        _, quote = calculate_quote(payload, db_path)
        return flask.jsonify(quote)
    except ValidationError as exc:
        return flask.jsonify({"error": str(exc)}), 400
    except Exception:
        return flask.jsonify({"error": "Serverda kutilmagan xatolik yuz berdi."}), 500
