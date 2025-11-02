from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.booking import Booking
from models.driver import Driver
from models.user import User
from database import db
from datetime import datetime
from utils.helpers import generate_booking_id
from utils.maps import calculate_distance, get_estimated_fare, get_nearby_drivers
from utils.file_upload import save_file
from config import Config

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/create', methods=['POST'])
@jwt_required()
def create_booking():
    """Create a new booking"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['pickup_address', 'pickup_latitude', 'pickup_longitude',
                          'drop_address', 'drop_latitude', 'drop_longitude',
                          'goods_type', 'scheduled_date']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Calculate distance
        distance = calculate_distance(
            data['pickup_latitude'], data['pickup_longitude'],
            data['drop_latitude'], data['drop_longitude']
        )
        
        # Calculate estimated fare
        estimated_fare = get_estimated_fare(distance)
        
        # Generate booking ID
        booking_id = generate_booking_id()
        
        # Create booking
        booking = Booking(
            booking_id=booking_id,
            customer_id=current_user['id'],
            pickup_address=data['pickup_address'],
            pickup_latitude=data['pickup_latitude'],
            pickup_longitude=data['pickup_longitude'],
            pickup_city=data.get('pickup_city'),
            drop_address=data['drop_address'],
            drop_latitude=data['drop_latitude'],
            drop_longitude=data['drop_longitude'],
            drop_city=data.get('drop_city'),
            goods_type=data['goods_type'],
            weight_kg=data.get('weight_kg'),
            volume_cubic_ft=data.get('volume_cubic_ft'),
            special_instructions=data.get('special_instructions'),
            distance_km=distance,
            estimated_fare=estimated_fare,
            scheduled_date=datetime.fromisoformat(data['scheduled_date'])
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Find nearby drivers
        nearby_drivers = get_nearby_drivers(
            data['pickup_latitude'],
            data['pickup_longitude'],
            radius_km=50
        )
        
        return jsonify({
            'message': 'Booking created successfully',
            'booking': booking.to_dict(),
            'nearby_drivers_count': len(nearby_drivers)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/my-bookings', methods=['GET'])
@jwt_required()
def get_my_bookings():
    """Get all bookings for current user"""
    try:
        current_user = get_jwt_identity()
        
        status = request.args.get('status')
        
        query = Booking.query.filter_by(customer_id=current_user['id'])
        
        if status:
            query = query.filter_by(status=status)
        
        bookings = query.order_by(Booking.created_at.desc()).all()
        
        bookings_list = []
        for booking in bookings:
            booking_dict = booking.to_dict()
            
            # Add driver info if assigned
            if booking.driver_id:
                driver = Driver.query.get(booking.driver_id)
                driver_user = User.query.get(driver.user_id)
                booking_dict['driver'] = {
                    'name': driver_user.name,
                    'phone': driver_user.phone,
                    'rating': driver.rating
                }
            
            bookings_list.append(booking_dict)
        
        return jsonify({
            'bookings': bookings_list,
            'count': len(bookings_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """Get booking details"""
    try:
        current_user = get_jwt_identity()
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Check authorization
        if booking.customer_id != current_user['id'] and current_user['role'] != 'admin':
            if current_user['role'] == 'driver':
                driver = Driver.query.filter_by(user_id=current_user['id']).first()
                if not driver or booking.driver_id != driver.id:
                    return jsonify({'error': 'Unauthorized'}), 403
            else:
                return jsonify({'error': 'Unauthorized'}), 403
        
        booking_dict = booking.to_dict()
        
        # Add customer info
        customer = User.query.get(booking.customer_id)
        booking_dict['customer'] = {
            'name': customer.name,
            'phone': customer.phone
        }
        
        # Add driver info if assigned
        if booking.driver_id:
            driver = Driver.query.get(booking.driver_id)
            driver_user = User.query.get(driver.user_id)
            booking_dict['driver'] = {
                'name': driver_user.name,
                'phone': driver_user.phone,
                'rating': driver.rating
            }
        
        return jsonify({'booking': booking_dict}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_booking(booking_id):
    """Cancel a booking"""
    try:
        current_user = get_jwt_identity()
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Check authorization
        if booking.customer_id != current_user['id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if can be cancelled
        if booking.status in ['completed', 'cancelled']:
            return jsonify({'error': 'Booking cannot be cancelled'}), 400
        
        data = request.get_json()
        
        booking.status = 'cancelled'
        
        # Free up driver if assigned
        if booking.driver_id:
            driver = Driver.query.get(booking.driver_id)
            if driver.status == 'busy':
                driver.status = 'available'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Booking cancelled successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/<int:booking_id>/rate', methods=['POST'])
@jwt_required()
def rate_booking(booking_id):
    """Rate a completed booking"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Check authorization
        if booking.customer_id != current_user['id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if booking.status != 'completed':
            return jsonify({'error': 'Can only rate completed bookings'}), 400
        
        if 'rating' not in data or not (1 <= data['rating'] <= 5):
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        booking.customer_rating = data['rating']
        booking.customer_feedback = data.get('feedback')
        
        # Update driver rating
        if booking.driver_id:
            driver = Driver.query.get(booking.driver_id)
            
            # Calculate new average rating
            total_rated_trips = Booking.query.filter_by(
                driver_id=driver.id,
                status='completed'
            ).filter(Booking.customer_rating.isnot(None)).count()
            
            if total_rated_trips > 0:
                avg_rating = db.session.query(
                    db.func.avg(Booking.customer_rating)
                ).filter_by(driver_id=driver.id, status='completed').scalar()
                
                driver.rating = round(avg_rating, 1)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Rating submitted successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/driver/available', methods=['GET'])
@jwt_required()
def get_available_bookings():
    """Get available bookings for drivers"""
    try:
        current_user = get_jwt_identity()
        
        # Check if user is driver
        driver = Driver.query.filter_by(user_id=current_user['id']).first()
        if not driver:
            return jsonify({'error': 'Driver profile not found'}), 404
        
        if not driver.is_verified:
            return jsonify({'error': 'Driver not verified'}), 403
        
        # Get pending bookings in driver's service area
        bookings = Booking.query.filter_by(status='pending').all()
        
        # Filter by distance from driver's current location
        available_bookings = []
        
        if driver.current_latitude and driver.current_longitude:
            for booking in bookings:
                distance = calculate_distance(
                    driver.current_latitude, driver.current_longitude,
                    booking.pickup_latitude, booking.pickup_longitude
                )
                
                if distance <= 50:  # Within 50km
                    booking_dict = booking.to_dict()
                    booking_dict['distance_from_driver'] = distance
                    
                    customer = User.query.get(booking.customer_id)
                    booking_dict['customer_name'] = customer.name
                    
                    available_bookings.append(booking_dict)
            
            # Sort by distance
            available_bookings.sort(key=lambda x: x['distance_from_driver'])
        
        return jsonify({
            'bookings': available_bookings,
            'count': len(available_bookings)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/<int:booking_id>/accept', methods=['POST'])
@jwt_required()
def accept_booking(booking_id):
    """Driver accepts a booking"""
    try:
        current_user = get_jwt_identity()
        
        driver = Driver.query.filter_by(user_id=current_user['id']).first()
        if not driver:
            return jsonify({'error': 'Driver profile not found'}), 404
        
        if not driver.is_verified:
            return jsonify({'error': 'Driver not verified'}), 403
        
        if driver.status != 'available':
            return jsonify({'error': 'Driver not available'}), 400
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        if booking.status != 'pending':
            return jsonify({'error': 'Booking already assigned'}), 400
        
        # Assign driver
        booking.driver_id = driver.id
        booking.status = 'driver_assigned'
        driver.status = 'busy'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Booking accepted successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/<int:booking_id>/update-status', methods=['POST'])
@jwt_required()
def update_booking_status(booking_id):
    """Update booking status"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'Status required'}), 400
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Check authorization
        if current_user['role'] == 'driver':
            driver = Driver.query.filter_by(user_id=current_user['id']).first()
            if not driver or booking.driver_id != driver.id:
                return jsonify({'error': 'Unauthorized'}), 403
        elif current_user['role'] != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Update status
        booking.status = data['status']
        
        # Update timestamps
        if data['status'] == 'driver_reached':
            booking.pickup_time = datetime.utcnow()
        elif data['status'] == 'completed':
            booking.drop_time = datetime.utcnow()
            
            # Update driver stats
            if booking.driver_id:
                driver = Driver.query.get(booking.driver_id)
                driver.total_trips += 1
                driver.status = 'available'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Status updated successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/upload-image', methods=['POST'])
@jwt_required()
def upload_goods_image():
    """Upload goods image"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file
        file_path = save_file(file, folder='goods')
        
        if not file_path:
            return jsonify({'error': 'Failed to save image'}), 500
        
        return jsonify({
            'message': 'Image uploaded successfully',
            'file_path': file_path
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
