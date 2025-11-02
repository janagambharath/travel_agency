from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
from database import db
import firebase_admin
from firebase_admin import auth, credentials
import os

auth_bp = Blueprint('auth', __name__)

# Initialize Firebase Admin (do this once)
try:
    cred = credentials.Certificate('firebase-credentials.json')
    firebase_admin.initialize_app(cred)
except:
    print("Firebase credentials not found. OTP will not work.")

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user (customer or driver)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['phone', 'name', 'role']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(phone=data['phone']).first()
        if existing_user:
            return jsonify({'error': 'Phone number already registered'}), 400
        
        # Validate role
        if data['role'] not in ['customer', 'driver']:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Create new user
        user = User(
            phone=data['phone'],
            name=data['name'],
            email=data.get('email'),
            role=data['role'],
            language=data.get('language', 'en'),
            firebase_uid=data.get('firebase_uid')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate JWT token
        access_token = create_access_token(identity={
            'id': user.id,
            'phone': user.phone,
            'role': user.role
        })
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with phone (OTP verification handled by Firebase on frontend)"""
    try:
        data = request.get_json()
        
        if 'phone' not in data:
            return jsonify({'error': 'Phone number required'}), 400
        
        # Find user by phone
        user = User.query.filter_by(phone=data['phone']).first()
        
        if not user:
            return jsonify({'error': 'User not found. Please register first.'}), 404
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Generate JWT token
        access_token = create_access_token(identity={
            'id': user.id,
            'phone': user.phone,
            'role': user.role
        })
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify Firebase OTP token"""
    try:
        data = request.get_json()
        
        if 'id_token' not in data:
            return jsonify({'error': 'ID token required'}), 400
        
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(data['id_token'])
        phone = decoded_token.get('phone_number')
        firebase_uid = decoded_token.get('uid')
        
        # Find or create user
        user = User.query.filter_by(phone=phone).first()
        
        if user:
            # Update firebase_uid if not set
            if not user.firebase_uid:
                user.firebase_uid = firebase_uid
                user.is_verified = True
                db.session.commit()
        else:
            # Create new user
            user = User(
                phone=phone,
                name=data.get('name', 'User'),
                role=data.get('role', 'customer'),
                firebase_uid=firebase_uid,
                is_verified=True
            )
            db.session.add(user)
            db.session.commit()
        
        # Generate JWT token
        access_token = create_access_token(identity={
            'id': user.id,
            'phone': user.phone,
            'role': user.role
        })
        
        return jsonify({
            'message': 'OTP verified successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'OTP verification failed: {str(e)}'}), 401

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user = get_jwt_identity()
        user = User.query.get(current_user['id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user = get_jwt_identity()
        user = User.query.get(current_user['id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'language' in data:
            user.language = data['language']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-language', methods=['POST'])
@jwt_required()
def change_language():
    """Change user language preference"""
    try:
        current_user = get_jwt_identity()
        user = User.query.get(current_user['id'])
        
        data = request.get_json()
        
        if 'language' not in data:
            return jsonify({'error': 'Language required'}), 400
        
        if data['language'] not in ['en', 'te']:
            return jsonify({'error': 'Invalid language. Use "en" or "te"'}), 400
        
        user.language = data['language']
        db.session.commit()
        
        return jsonify({
            'message': 'Language updated successfully',
            'language': user.language
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
