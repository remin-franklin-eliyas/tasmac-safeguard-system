from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from config import Config
from database import init_db

# Import blueprints
from routes.users import users_bp
from routes.transactions import transactions_bp
from routes.incidents import incidents_bp
from routes.analytics import analytics_bp


# --------------------
# App initialization
# --------------------
app = Flask(__name__)
app.config.from_object(Config)

# Ensure SECRET_KEY is set
app.config["SECRET_KEY"] = Config.SECRET_KEY


# --------------------
# CORS (Allow Vercel + others)
# --------------------
CORS(
    app,
    supports_credentials=True
)


# --------------------
# SocketIO (Railway-safe)
# --------------------
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="eventlet",   # IMPORTANT for Gunicorn
    ping_timeout=60,
    ping_interval=25
)

# Make socketio accessible globally
app.socketio = socketio


# --------------------
# Database initialization
# (CRITICAL: runs under Gunicorn)
# --------------------
with app.app_context():
    init_db()


# --------------------
# Register blueprints
# --------------------
app.register_blueprint(users_bp, url_prefix="/api/users")
app.register_blueprint(transactions_bp, url_prefix="/api/transactions")
app.register_blueprint(incidents_bp, url_prefix="/api/incidents")
app.register_blueprint(analytics_bp, url_prefix="/api/analytics")


# --------------------
# Routes
# --------------------
@app.route("/")
def home():
    return jsonify({
        "message": "TASMAC SafeGuard System API",
        "version": "1.0.0",
        "websocket": "enabled",
        "endpoints": {
            "users": "/api/users",
            "transactions": "/api/transactions",
            "incidents": "/api/incidents",
            "analytics": "/api/analytics"
        }
    })


@app.route("/api/health")
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": str(__import__("datetime").datetime.utcnow())
    })


# --------------------
# WebSocket events
# --------------------
@socketio.on("connect")
def handle_connect():
    print("🔌 Client connected")
    emit("connection_response", {
        "data": "Connected to TASMAC SafeGuard System"
    })


@socketio.on("disconnect")
def handle_disconnect():
    print("❌ Client disconnected")


# --------------------
# Broadcast helpers
# --------------------
def broadcast_transaction(transaction_data):
    socketio.emit("new_transaction", transaction_data)


def broadcast_alert(alert_data):
    socketio.emit("new_alert", alert_data)


def broadcast_approval_request(request_data):
    socketio.emit("approval_request", request_data)


# Attach helpers to app
app.broadcast_transaction = broadcast_transaction
app.broadcast_alert = broadcast_alert
app.broadcast_approval_request = broadcast_approval_request


# --------------------
# Error handlers
# --------------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    # TEMPORARILY verbose — helps Railway debugging
    return jsonify({
        "error": "Internal server error",
        "details": str(error)
    }), 500


# --------------------
# Local dev only
# --------------------
if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5001))
    print("🚀 Starting TASMAC SafeGuard API (local)")
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=False
    )
