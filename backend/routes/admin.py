from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.driver import Driver
from models.vehicle import Vehicle
from models.booking import Booking
from database import db
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

def admin_required():
    """Decorator to check if user is admin"""
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    return None

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get admin dashboard statistics"""
    try:
        error = admin_required()
        if error:
            return error
        
        # Total counts
        total_customers = User.query.filter_by(role='customer').count()
        total_drivers = Driver.query.count()
        total_verified_drivers = Driver.query.filter_by(is_verified=True).count()
        total_bookings = Booking.query.count()
        
        # Status counts
        pending_bookings = Booking.query.filter_by(status='pending').count()
        ongoing_bookings = Booking.query.filter(
            Booking.status.in_(['driver_assigned', 'driver_reached', 'ongoing'])
        ).count()
        completed_bookings = Booking.query.filter_by(status='completed').count()
        
        # Driver status
        available_drivers = Driver.query.filter_by(status='available', is_verified=True).count()
        busy_drivers = Driver.query.filter_by(status='busy').count()
        
        # Revenue calculations
        completed = Booking.query.filter_by(status='completed').all()
        total_revenue = sum(b.final_fare or b.estimated_fare for b in completed)
        total_commission = sum(b.admin_commission or 0 for b in completed)
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_bookings = Booking.query.filter(Booking.created_at >= week_ago).count()
        recent_revenue = sum(
            b.final_fare or b.estimated_fare 
            for b in Booking.query.filter(
                Booking.created_at >= week_ago,
                Booking.status == 'completed'
            ).all()
        )
        
        # Top drivers by trips
        top_drivers = Driver.query.order_by(Driver.total_trips.desc()).limit(5).all()
        top_drivers_list = []
        for driver in top_drivers:
            user = User.query.get(driver.user_id)
            top_drivers_list.append({
                'name': user.name,
                'phone': user.phone,
                'total_trips': driver.total_trips,
                'rating': driver.rating,
                'earnings': driver.total_earnings
            })
        
        return jsonify({
            'overview': {
                'total_customers': total_customers,
                'total_drivers': total_drivers,
                'verified_drivers': total_verified_drivers,
                'total_bookings': total_bookings
            },
            'bookings': {
                'pending': pending_bookings,
                'ongoing': ongoing_bookings,
                'completed': completed_bookings
            },
            'drivers': {
                'available': available_drivers,
                'busy': busy_drivers,
                'offline': total_verified_drivers - available_drivers - busy_drivers
            },
            'revenue': {
                'total': round(total_revenue, 2),
                'commission': round(total_commission, 2),
                'driver_earnings': round(total_revenue - total_commission, 2)
            },
            'recent_activity': {
                'bookings_last_7_days': recent_bookings,
                'revenue_last_7_days': round(recent_revenue, 2)
            },
            'top_drivers': top_drivers_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/drivers/pending', methods=['GET'])
@jwt_required()
def get_pending_drivers():
    """Get list of drivers pending verification"""
    try:
        error = admin_required()
        if error:
            return error
        
        pending_drivers = Driver.query.filter_by(is_verified=False).all()
        
        drivers_list = []
        for driver in pending_drivers:
            user = User.query.get(driver.user_id)
            driver_dict = driver.to_dict()
            driver_dict['user'] = user.to_dict()
            
            # Include vehicles
            vehicles = Vehicle.query.filter_by(driver_id=driver.id).all()
            driver_dict['vehicles'] = [v.to_dict() for v in vehicles]
            
            drivers_list.append(driver_dict)
        
        return jsonify({
            'drivers': drivers_list,
            'count': len(drivers_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/drivers/<int:driver_id>/verify', methods=['POST'])
@jwt_required()
def verify_driver(driver_id):
    """Verify a driver"""
    try:
        error = admin_required()
        if error:
            return error
        
        driver = Driver.query.get(driver_id)
        if not driver:
            return jsonify({'error': 'Driver not found'}), 404
        
        data = request.get_json()
        
        driver.is_verified = data.get('is_verified', True)
        
        # Verify vehicles too
        if driver.is_verified:
            vehicles = Vehicle.query.filter_by(driver_id=driver.id).all()
            for vehicle in vehicles:
                vehicle.is_verified = True
        
        db.session.commit()
        
        return jsonify({
            'message': f'Driver {"verified" if driver.is_verified else "rejected"} successfully',
            'driver': driver.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/drivers', methods=['GET'])
@jwt_required()
def list_all_drivers():
    """List all drivers with filters"""
    try:
        error = admin_required()
        if error:
            return error
        
        # Get query parameters
        status = request.args.get('status')
        is_verified = request.args.get('is_verified')
        service_area = request.args.get('service_area')
        
        query = Driver.query
        
        if status:
            query = query.filter_by(status=status)
        if is_verified is not None:
            query = query.filter_by(is_verified=is_verified == 'true')
        if service_area:
            query = query.filter_by(service_area=service_area)
        
        drivers = query.all()
        
        drivers_list = []
        for driver in drivers:
            user = User.query.get(driver.user_id)
            driver_dict = driver.to_dict()
            driver_dict['user'] = user.to_dict()
            drivers_list.append(driver_dict)
        
        return jsonify({
            'drivers': drivers_list,
            'count': len(drivers_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/bookings', methods=['GET'])
@jwt_required()
def list_all_bookings():
    """List all bookings with filters"""
    try:
        error = admin_required()
        if error:
            return error
        
        # Get query parameters
        status = request.args.get('status')
        customer_id = request.args.get('customer_id', type=int)
        driver_id = request.args.get('driver_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = Booking.query
        
        if status:
            query = query.filter_by(status=status)
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        if driver_id:
            query = query.filter_by(driver_id=driver_id)
        if date_from:
            query = query.filter(Booking.created_at >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(Booking.created_at <= datetime.fromisoformat(date_to))
        
        bookings = query.order_by(Booking.created_at.desc()).all()
        
        bookings_list = []
        for booking in bookings:
            booking_dict = booking.to_dict()
            
            # Add customer and driver names
            customer = User.query.get(booking.customer_id)
            booking_dict['customer_name'] = customer.name
            
            if booking.driver_id:
                driver = Driver.query.get(booking.driver_id)
                driver_user = User.query.get(driver.user_id)
                booking_dict['driver_name'] = driver_user.name
            
            bookings_list.append(booking_dict)
        
        return jsonify({
            'bookings': bookings_list,
            'count': len(bookings_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/bookings/<int:booking_id>/assign', methods=['POST'])
@jwt_required()
def assign_driver_to_booking(booking_id):
    """Manually assign a driver to a booking"""
    try:
        error = admin_required()
        if error:
            return error
        
        data = request.get_json()
        
        if 'driver_id' not in data:
            return jsonify({'error': 'Driver ID required'}), 400
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        driver = Driver.query.get(data['driver_id'])
        if not driver:
            return jsonify({'error': 'Driver not found'}), 404
        
        if not driver.is_verified:
            return jsonify({'error': 'Driver not verified'}), 400
        
        if booking.status != 'pending':
            return jsonify({'error': 'Booking already assigned'}), 400
        
        # Assign driver
        booking.driver_id = driver.id
        booking.status = 'driver_assigned'
        driver.status = 'busy'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Driver assigned successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/bookings/<int:booking_id>/finalize', methods=['POST'])
@jwt_required()
def finalize_booking(booking_id):
    """Finalize booking with final fare and calculate commission"""
    try:
        error = admin_required()
        if error:
            return error
        
        data = request.get_json()
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        if booking.status != 'completed':
            return jsonify({'error': 'Booking must be completed first'}), 400
        
        # Set final fare (or use estimated if not provided)
        final_fare = data.get('final_fare', booking.estimated_fare)
        booking.final_fare = final_fare
        
        # Calculate commission
        from config import Config
        commission_rate = Config.ADMIN_COMMISSION_PERCENTAGE / 100
        commission = final_fare * commission_rate
        
        # Apply min/max limits
        commission = max(Config.MIN_COMMISSION, min(commission, Config.MAX_COMMISSION))
        
        booking.admin_commission = commission
        booking.driver_earning = final_fare - commission
        booking.payment_status = data.get('payment_status', 'paid')
        
        # Update driver earnings
        if booking.driver_id:
            driver = Driver.query.get(booking.driver_id)
            driver.total_earnings += booking.driver_earning
            driver.wallet_balance += booking.driver_earning
        
        db.session.commit()
        
        return jsonify({
            'message': 'Booking finalized successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@jwt_required()
def toggle_user_status(user_id):
    """Activate or deactivate a user"""
    try:
        error = admin_required()
        if error:
            return error
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        user.is_active = data.get('is_active', not user.is_active)
        
        db.session.commit()
        
        return jsonify({
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reports/revenue', methods=['GET'])
@jwt_required()
def revenue_report():
    """Generate revenue report"""
    try:
        error = admin_required()
        if error:
            return error
        
        # Get date range from query params
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = Booking.query.filter_by(status='completed')
        
        if date_from:
            query = query.filter(Booking.drop_time >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(Booking.drop_time <= datetime.fromisoformat(date_to))
        
        bookings = query.all()
        
        total_bookings = len(bookings)
        total_revenue = sum(b.final_fare or b.estimated_fare for b in bookings)
        total_commission = sum(b.admin_commission or 0 for b in bookings)
        total_driver_earnings = total_revenue - total_commission
        
        # Group by date
        daily_revenue = {}
        for booking in bookings:
            if booking.drop_time:
                date_key = booking.drop_time.date().isoformat()
                if date_key not in daily_revenue:
                    daily_revenue[date_key] = {
                        'bookings': 0,
                        'revenue': 0,
                        'commission': 0
                    }
                daily_revenue[date_key]['bookings'] += 1
                daily_revenue[date_key]['revenue'] += booking.final_fare or booking.estimated_fare
                daily_revenue[date_key]['commission'] += booking.admin_commission or 0
        
        return jsonify({
            'summary': {
                'total_bookings': total_bookings,
                'total_revenue': round(total_revenue, 2),
                'total_commission': round(total_commission, 2),
                'total_driver_earnings': round(total_driver_earnings, 2),
                'average_fare': round(total_revenue / total_bookings, 2) if total_bookings > 0 else 0
            },
            'daily_breakdown': daily_revenue
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
