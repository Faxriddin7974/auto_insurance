from flask import Flask
from .auth import auth_bp
from .cars import cars_bp
from .home import home_bp
from .orders import orders_bp
from .saved_cars import saved_cars_bp
from .reviews import reviews_bp
from .admin import admin_bp
from .contact import contact_bp
from .stats import stats_bp
from .chat import chat_bp


def register_blueprints(app: Flask):
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cars_bp, url_prefix="")
    app.register_blueprint(home_bp, url_prefix="")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(saved_cars_bp, url_prefix="")
    app.register_blueprint(reviews_bp, url_prefix="/api/reviews")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(contact_bp, url_prefix="/api")
    app.register_blueprint(stats_bp, url_prefix="/api")
    app.register_blueprint(chat_bp, url_prefix="")
