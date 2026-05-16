from pathlib import Path

from flask import Flask, jsonify, redirect, render_template  # type: ignore[import]
from werkzeug.exceptions import RequestEntityTooLarge  # type: ignore[import]

from config import FLASK_SECRET_KEY, MAX_CONTENT_LENGTH, GOOGLE_CLIENT_ID
from database import init_db, get_db_connection
from api import register_blueprints
from api.auth import current_user

app = Flask(__name__)
app.config["SECRET_KEY"] = FLASK_SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

DB_PATH = Path(app.root_path) / "users.db"
CAR_UPLOAD_DIR = Path(app.static_folder) / "uploads" / "cars"

init_db(DB_PATH)
register_blueprints(app)


@app.context_processor
def inject_template_config():
    return {"google_client_id": GOOGLE_CLIENT_ID}


@app.errorhandler(RequestEntityTooLarge)
def handle_large_upload(_: RequestEntityTooLarge):
    return jsonify({"error": "Rasm hajmi 5 MB dan oshmasligi kerak."}), 413


@app.route("/")
def index():
    return render_template("main.html")


@app.get("/faq")
def faq():
    return render_template("faq.html")


@app.get("/packages")
def packages():
    return render_template("packages.html")


@app.get("/reviews")
def reviews_page():
    return render_template("reviews.html")


@app.get("/claim-guide")
def claim_guide():
    return render_template("claim_guide.html")


@app.get("/contact")
def contact_page():
    return render_template("contact.html")


@app.get("/home-insurance")
def home_insurance_page():
    return render_template("home_insurance.html")


@app.get("/payment/<int:order_id>")
def payment_page(order_id: int):
    user = current_user(DB_PATH)
    if not user:
        return redirect("/")
    
    from api.orders import get_order_if_accessible
    from config import CAR_INDEX
    
    row = get_order_if_accessible(order_id, user, DB_PATH)
    if not row:
        return redirect("/")

    model_name = CAR_INDEX.get(row["model_id"], {"name": {"uz": row["model_id"]}})["name"]["uz"]
    order = {key: row[key] for key in row.keys()}
    return render_template("payment.html", order=order, model_name=model_name)


@app.get("/admin")
def admin_page():
    from api.auth import require_admin
    _, error = require_admin(DB_PATH)
    if error:
        return redirect("/")
    return render_template("admin.html")


if __name__ == "__main__":
    app.run(debug=True)
