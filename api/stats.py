from pathlib import Path

import flask

from database import get_db_connection

stats_bp = flask.Blueprint("stats", __name__)


@stats_bp.get("/stats")
def get_stats():
    db_path = Path(flask.current_app.root_path) / "users.db"
    
    with get_db_connection(db_path) as connection:
        users_total = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        orders_total = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        orders_paid = connection.execute("SELECT COUNT(*) FROM orders WHERE status = 'paid'").fetchone()[0]
    
    success_percentage = round((orders_paid / orders_total * 100), 1) if orders_total > 0 else 0
    
    return flask.jsonify({
        "users": users_total,
        "paid_orders": orders_paid,
        "total_orders": orders_total,
        "success_percentage": success_percentage,
    })
