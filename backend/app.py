from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from database import db, init_db
from config import Config
import os

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend/out', static_url_path='')
app.config.from_object(Config)

# Initialize extensions
CORS(app)
jwt = JWTManager(app)
db.init_app(app)

# Import routes
from routes.auth import auth_bp
from routes.booking import booking_bp
from routes.driver import driver_bp
from routes.admin import admin_bp
from routes.payment import payment_bp

# Register blueprints with /api prefix
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(booking_bp, url_prefix='/api/booking')
app.register_blueprint(driver_bp, url_prefix='/api/driver')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(payment_bp, url_prefix='/api/payment')

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# API root endpoint
@app.route('/api')
def api_root():
    return jsonify({
        'message': 'Sri Ramalingeshvara Transport Agency API',
        'version': '1.0',
        'status': 'running'
    })

# Health check endpoint
@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'}), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Create database tables
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
