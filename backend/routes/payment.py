from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.booking import Booking
from database import db
import razorpay
from config import Config

payment_bp = Blueprint('payment', __name__)

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(Config.RAZORPAY_KEY_ID, Config.RAZORPAY_KEY_SECRET))

@payment_bp.route('/create-order', methods=['POST'])
@jwt_required()
def create_payment_order():
    """Create Razorpay order for a booking"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if 'booking_id' not in data:
            return jsonify({'error': 'Booking ID required'}), 400
        
        booking = Booking.query.get(data['booking_id'])
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Check if user is the customer
        if booking.customer_id != current_user['id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if already paid
        if booking.payment_status == 'paid':
            return jsonify({'error': 'Booking already paid'}), 400
        
        # Determine amount (full or partial)
        payment_type = data.get('payment_type', 'full')  # full, partial
        
        if payment_type == 'partial':
            # Pay 50% advance
            amount = booking.estimated_fare * 0.5
        else:
            amount = booking.estimated_fare
        
        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': int(amount * 100),  # Amount in paise
            'currency': 'INR',
            'receipt': f'booking_{booking.booking_id}',
            'notes': {
                'booking_id': str(booking.id),
                'customer_id': str(booking.customer_id),
                'payment_type': payment_type
            }
        })
        
        # Save order ID
        booking.razorpay_order_id = razorpay_order['id']
        db.session.commit()
        
        return jsonify({
            'order_id': razorpay_order['id'],
            'amount': amount,
            'currency': 'INR',
            'booking_id': booking.booking_id,
            'razorpay_key': Config.RAZORPAY_KEY_ID
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_payment():
    """Verify Razorpay payment signature"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        required_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing payment verification fields'}), 400
        
        # Verify signature
        try:
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })
        except razorpay.errors.SignatureVerificationError:
            return jsonify({'error': 'Invalid payment signature'}), 400
        
        # Find booking
        booking = Booking.query.filter_by(razorpay_order_id=data['razorpay_order_id']).first()
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Check authorization
        if booking.customer_id != current_user['id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Update payment status
        booking.razorpay_payment_id = data['razorpay_payment_id']
        
        # Get payment details to determine if full or partial
        payment = razorpay_client.payment.fetch(data['razorpay_payment_id'])
        amount_paid = payment['amount'] / 100  # Convert paise to rupees
        
        if amount_paid >= booking.estimated_fare:
            booking.payment_status = 'paid'
            booking.payment_method = 'online'
        else:
            booking.payment_status = 'partial'
            booking.payment_method = 'partial'
        
        # Confirm booking if it was pending
        if booking.status == 'pending':
            booking.status = 'confirmed'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment verified successfully',
            'booking': booking.to_dict(),
            'payment_status': booking.payment_status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/webhook', methods=['POST'])
def payment_webhook():
    """Handle Razorpay webhooks"""
    try:
        # Verify webhook signature
        webhook_signature = request.headers.get('X-Razorpay-Signature')
        webhook_secret = Config.RAZORPAY_KEY_SECRET
        
        # Razorpay will verify this
        razorpay_client.utility.verify_webhook_signature(
            request.get_data().decode('utf-8'),
            webhook_signature,
            webhook_secret
        )
        
        data = request.get_json()
        event = data['event']
        
        if event == 'payment.captured':
            # Payment successful
            payment_entity = data['payload']['payment']['entity']
            order_id = payment_entity['order_id']
            
            booking = Booking.query.filter_by(razorpay_order_id=order_id).first()
            if booking:
                booking.razorpay_payment_id = payment_entity['id']
                booking.payment_status = 'paid'
                booking.status = 'confirmed'
                db.session.commit()
        
        elif event == 'payment.failed':
            # Payment failed
            payment_entity = data['payload']['payment']['entity']
            order_id = payment_entity['order_id']
            
            booking = Booking.query.filter_by(razorpay_order_id=order_id).first()
            if booking:
                # Keep booking as pending, customer can retry
                pass
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/refund', methods=['POST'])
@jwt_required()
def refund_payment():
    """Initiate refund for a cancelled booking (admin only)"""
    try:
        current_user = get_jwt_identity()
        
        # Check if admin
        from models.user import User
        user = User.query.get(current_user['id'])
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        if 'booking_id' not in data:
            return jsonify({'error': 'Booking ID required'}), 400
        
        booking = Booking.query.get(data['booking_id'])
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        if booking.status != 'cancelled':
            return jsonify({'error': 'Only cancelled bookings can be refunded'}), 400
        
        if not booking.razorpay_payment_id:
            return jsonify({'error': 'No payment found for this booking'}), 400
        
        # Get payment amount
        payment = razorpay_client.payment.fetch(booking.razorpay_payment_id)
        amount = payment['amount']
        
        # Create refund
        refund_amount = data.get('amount', amount)  # Full or partial refund
        
        refund = razorpay_client.payment.refund(
            booking.razorpay_payment_id,
            {
                'amount': refund_amount,
                'speed': 'normal',
                'notes': {
                    'reason': data.get('reason', 'Booking cancelled')
                }
            }
        )
        
        booking.payment_status = 'refunded'
        db.session.commit()
        
        return jsonify({
            'message': 'Refund initiated successfully',
            'refund_id': refund['id'],
            'amount': refund_amount / 100,
            'status': refund['status']
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/cash-payment', methods=['POST'])
@jwt_required()
def mark_cash_payment():
    """Mark booking as cash payment (admin confirms after delivery)"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Check if admin
        from models.user import User
        user = User.query.get(current_user['id'])
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        if 'booking_id' not in data:
            return jsonify({'error': 'Booking ID required'}), 400
        
        booking = Booking.query.get(data['booking_id'])
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        if booking.status != 'completed':
            return jsonify({'error': 'Booking must be completed first'}), 400
        
        # Mark as cash payment
        booking.payment_status = 'paid'
        booking.payment_method = 'cash'
        
        # If final fare not set, use estimated
        if not booking.final_fare:
            booking.final_fare = data.get('final_fare', booking.estimated_fare)
        
        # Calculate commission
        from config import Config
        commission = booking.final_fare * (Config.ADMIN_COMMISSION_PERCENTAGE / 100)
        commission = max(Config.MIN_COMMISSION, min(commission, Config.MAX_COMMISSION))
        
        booking.admin_commission = commission
        booking.driver_earning = booking.final_fare - commission
        
        # Update driver earnings
        if booking.driver_id:
            from models.driver import Driver
            driver = Driver.query.get(booking.driver_id)
            driver.total_earnings += booking.driver_earning
            driver.wallet_balance += booking.driver_earning
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cash payment recorded successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
