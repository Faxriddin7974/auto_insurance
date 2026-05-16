from datetime import datetime
from pathlib import Path

import flask

from config import HOME_CONSTRUCTION_TYPES, HOME_PROPERTY_TYPES, HOME_REGIONS, HOME_SECURITY_LEVELS
from calculators import HomePremiumCalculator
from models import HomePremiumInput, ValidationError

home_bp = flask.Blueprint("home", __name__)


@home_bp.get("/home-data")
def home_data():
    current_year = datetime.now().year
    return flask.jsonify(
        {
            "property_types": [{"id": item["id"], "name": item["name"]} for item in HOME_PROPERTY_TYPES],
            "construction_types": [{"id": item["id"], "name": item["name"]} for item in HOME_CONSTRUCTION_TYPES],
            "security_levels": [{"id": item["id"], "name": item["name"]} for item in HOME_SECURITY_LEVELS],
            "regions": [{"id": item["id"], "name": item["name"]} for item in HOME_REGIONS],
            "year_min": 1950,
            "year_max": current_year,
            "current_year": current_year,
        }
    )


@home_bp.post("/calculate-home")
def calculate_home():
    payload = flask.request.get_json(silent=True)
    try:
        home_input = HomePremiumInput.from_payload(payload)
        calculator = HomePremiumCalculator()
        quote = calculator.calculate(home_input)
        return flask.jsonify(quote)
    except ValidationError as exc:
        return flask.jsonify({"error": str(exc)}), 400
    except Exception:
        return flask.jsonify({"error": "Serverda kutilmagan xatolik yuz berdi."}), 500
