from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.driver import Driver
from models.vehicle import Vehicle
from models.user import User
from database import db
from datetime import datetime
from utils.file_upload import save_file

driver_bp = Blueprint('driver', __name__)

@driver_bp.route('/register', methods=['POST'])
@jwt_required()
def register_driver():
    """Register as a driver (complete driver profile)"""
    try:
        current_user = get_jwt_identity()
        
        # Check if user is driver
        user = User.query.get(current_user['id'])
        if user.role != 'driver':
            return jsonify({'error': 'Only driver accounts can register as drivers'}), 403
        
        # Check if already registered
        existing_driver = Driver.query.filter_by(user_id=current_user['id']).first()
        if existing_driver:
            return jsonify({'error': 'Driver profile already exists'}), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'license_number' not in data:
            return jsonify({'error': 'License number required'}), 400
        
        # Create driver profile
        driver = Driver(
            user_id=current_user['id'],
            license_number=data['license_number'],
            id_proof_type=data.get('id_proof_type'),
            id_proof_number=data.get('id_proof_number'),
            service_area=data.get('service_area'),
            status='offline'
        )
        
        db.session.add(driver)
        db.session.commit()
        
        return jsonify({
            'message': 'Driver registered successfully. Awaiting verification.',
            'driver': driver.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@driver_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_driver_profile():
    """Get driver profile"""
    try:
        current_user = get_jwt_identity()
        
        driver = Driver.query.filter_by(user_id=current_user['id']).first()
        if not driver:
            return jsonify({'error': 'Driver profile not found'}), 404
        
        # Include user details
        user = User.query.get(current_user['id'])
        driver_dict = driver.to_dict()
        driver_dict['user'] = user.to_dict()
        
        # Include vehicles
        vehicles = Vehicle.query.filter_by(driver_id=driver.id).all()
        driver_dict['vehicles'] = [v.to_dict() for v in vehicles]
        
        return jsonify({'driver': driver_dict}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@driver_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_driver_profile():
    """Update driver profile"""
    try:
        current_user = get_jwt_identity()
        
        driver = Driver.query.filter_by(user_id=current_user['id']).first()
        if not driver:
            return jsonify({'error': 'Driver profile not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'service_area' in data:
            driver.service_area = data['service_area']
        if 'id_proof_type' in data:
            driver.id_proof_type = data['id_proof_type']
        if 'id_proof_number' in data:
            driver.id_proof_number = data['id_proof_number']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'driver': driver.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@driver_bp.route('/status', methods=['POST'])
@jwt_required()
def toggle_status():
    """Toggle driver availability status"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        driver = Driver.query.filter_by(user_id=current_user['id']).first()
        if not driver:
            return jsonify({'error': 'Driver profile not found'}), 404
        
        if not driver.is_verified:
            return jsonify({'error': 'Driver not verified yet'}), 403
        
        if 'status' not in data:
            return jsonify({'error': 'Status required'}), 400
        
        if data['status'] not in ['available', 'offline']:
            return jsonify({'error': 'Invalid status. Use "available" or "offline"'}), 400
        
        driver.status = data['status']
        db.session.commit()
        
        return jsonify({
            'message': f'Status updated to {data["status"]}',
            'status': driver.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@driver_bp.route('/location', methods=['POST'])
@jwt_required()
def update_location():
    """Update driver's current location"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        driver = Driver.query.filter_by(user_id=current_user['id']).first()
        if not driver:
            return jsonify({'error': 'Driver profile not found'}), 404
        
        if 'latitude' not in data or 'longitude' not in data:
            return jsonify({'error': 'Latitude and longitude required'}), 400
        
        driver.current_latitude = data['latitude']
        driver.current_longitude = data['longitude']
        driver.last_location_update = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Location updated successfully',
            'location': {
                'latitude': driver.current_latitude,
                'longitude': driver.current_longitude
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@driver_bp.route('/vehicle/add', methods=['POST'])
@jwt_required()
def add_vehicle():
    """Add a vehicle"""
    try:
        current_user = get_jwt_identity()
        
        driver = Driver.query.filter_by(user_id=current_user['id']).first()
        if not driver:
            return jsonify({'error': 'Driver profile not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['vehicle_number', 'vehicle_type', 'capacity_kg']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if vehicle already exists
        existing_vehicle = Vehicle.query.filter_by(vehicle_number=data['vehicle_number']).first()
        if existing_vehicle:
            return jsonify({'error': 'Vehicle number already registered'}), 400
        
        # Create vehicle
        vehicle = Vehicle(
            driver_id=driver.id,
            vehicle_number=data['vehicle_number'],
            vehicle_type=data['vehicle_type'],
            capacity_kg=data['capacity_kg'],
            capacity_cubic_ft=data.get('capacity_cubic_ft')
        )
        
        db.session.add(vehicle)
        db.session.commit()
        
        return jsonify({
            'message': 'Vehicle added successfully',
            'vehicle': vehicle.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@driver_bp.route('/vehicle/<int:vehicle_id>', methods=['PUT'])
@jwt_required()
def update_vehicle(vehicle_id):
    """Update vehicle details"""
    try:
        current_user = get_jwt_identity()
        
        driver = Driver.query.filter_by(user_id=current_user['id']).first()
        if not driver:
            return jsonify({'error': 'Driver profile not found'}), 404
        
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle or vehicle.driver_id != driver.id:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'vehicle_type' in data:
            vehicle.vehicle_type = data['vehicle_type']
        if 'capacity_kg' in data:
            vehicle.capacity_kg = data['capacity_kg']
        if 'capacity_cubic_ft' in data:
            vehicle.capacity_cubic_ft = data['capacity_cubic_ft']
        if 'is_active' in data:
            vehicle.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Vehicle updated successfully',
            'vehicle': vehicle.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@driver_bp.route('/vehicle/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
def delete_vehicle(vehicle_id):
    """Delete a vehicle"""
    try:
        current_user = get_jwt_identity()
        
        driver = Driver.query.filter_by(user_id=current_user['id']).first()
        if not driver:
            return jsonify({'error': 'Driver profile not found'}), 404
        
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle or vehicle.driver_id != driver.id:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        db.session.delete(vehicle)
        db.session.commit()
        
        return jsonify({'message': 'Vehicle deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@driver_bp.route('/earnings', methods=['GET'])
@jwt_required()
def get_earnings():
    """Get driver earnings summary"""
    try:
        current_user = get_jwt_identity()
        
        driver = Driver.query.filter_by(user_id=current_user['id']).first()
        if not driver:
            return jsonify({'error': 'Driver profile not found'}), 404
        
        from models.booking import Booking
        
        # Get completed bookings
        completed_bookings = Booking.query.filter_by(
            driver_id=driver.id,
            status='completed'
        ).all()
        
        # Calculate earnings
        total_earnings = sum(b.driver_earning or 0 for b in completed_bookings)
        total_trips = len(completed_bookings)
        
        # Recent earnings (last 10)
        recent_bookings = Booking.query.filter_by(
            driver_id=driver.id,
            status='completed'
        ).order_by(Booking.drop_time.desc()).limit(10).all()
        
        return jsonify({
            'total_earnings': total_earnings,
            'total_trips': total_trips,
            'wallet_balance': driver.wallet_balance,
            'average_rating': driver.rating,
            'recent_trips': [
                {
                    'booking_id': b.booking_id,
                    'date': b.drop_time.isoformat() if b.drop_time else None,
                    'earning': b.driver_earning,
                    'distance': b.distance_km
                } for b in recent_bookings
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@driver_bp.route('/list', methods=['GET'])
def list_drivers():
    """List all verified and available drivers (public endpoint)"""
    try:
        # Get query parameters
        status = request.args.get('status', 'available')
        service_area = request.args.get('service_area')
        
        query = Driver.query.filter_by(is_verified=True)
        
        if status:
            query = query.filter_by(status=status)
        
        if service_area:
            query = query.filter_by(service_area=service_area)
        
        drivers = query.all()
        
        drivers_list = []
        for driver in drivers:
            user = User.query.get(driver.user_id)
            driver_dict = driver.to_dict()
            driver_dict['name'] = user.name
            drivers_list.append(driver_dict)
        
        return jsonify({
            'drivers': drivers_list,
            'count': len(drivers_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
