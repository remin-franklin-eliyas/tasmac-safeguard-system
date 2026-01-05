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

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Enable CORS for frontend
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://localhost:3001"]}})

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://localhost:3001"])

# Store socketio instance globally for use in routes
app.socketio = socketio

# Register blueprints
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
app.register_blueprint(incidents_bp, url_prefix='/api/incidents')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

@app.route('/')
def home():
    """API root endpoint"""
    return jsonify({
        'message': 'TASMAC SafeGuard System API',
        'version': '1.0.0',
        'websocket': 'enabled',
        'endpoints': {
            'users': '/api/users',
            'transactions': '/api/transactions',
            'incidents': '/api/incidents',
            'analytics': '/api/analytics'
        }
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': str(__import__('datetime').datetime.now())
    })

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connection_response', {'data': 'Connected to TASMAC SafeGuard System'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Broadcast events (called from routes)
def broadcast_transaction(transaction_data):
    """Broadcast new transaction to all connected clients"""
    socketio.emit('new_transaction', transaction_data)

def broadcast_alert(alert_data):
    """Broadcast alert to all connected clients"""
    socketio.emit('new_alert', alert_data)

def broadcast_approval_request(request_data):
    """Broadcast approval request to organization dashboard"""
    socketio.emit('approval_request', request_data)

# Make broadcast functions available globally
app.broadcast_transaction = broadcast_transaction
app.broadcast_alert = broadcast_alert
app.broadcast_approval_request = broadcast_approval_request

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database on first run
    print("🚀 Starting TASMAC SafeGuard API with WebSocket...")
    init_db()
    print("✅ Database initialized")
    print("✅ WebSocket enabled")
    
    # Run Flask app with SocketIO
    import os
    port = int(os.environ.get('PORT', 5001))
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False  # Disable debug in production
    )