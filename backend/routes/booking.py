from database import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(50), unique=True, nullable=False)  # SRTA-XXXXXX
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True)
    
    # Pickup details
    pickup_address = db.Column(db.String(255), nullable=False)
    pickup_latitude = db.Column(db.Float, nullable=False)
    pickup_longitude = db.Column(db.Float, nullable=False)
    pickup_city = db.Column(db.String(100), nullable=True)
    
    # Drop details
    drop_address = db.Column(db.String(255), nullable=False)
    drop_latitude = db.Column(db.Float, nullable=False)
    drop_longitude = db.Column(db.Float, nullable=False)
    drop_city = db.Column(db.String(100), nullable=True)
    
    # Goods details
    goods_type = db.Column(db.String(100), nullable=False)  # cement, furniture, electronics, etc
    weight_kg = db.Column(db.Integer, nullable=True)
    volume_cubic_ft = db.Column(db.Integer, nullable=True)
    goods_image = db.Column(db.String(255), nullable=True)
    special_instructions = db.Column(db.Text, nullable=True)
    
    # Trip details
    distance_km = db.Column(db.Float, nullable=False)
    estimated_fare = db.Column(db.Float, nullable=False)
    final_fare = db.Column(db.Float, nullable=True)
    admin_commission = db.Column(db.Float, nullable=True)
    driver_earning = db.Column(db.Float, nullable=True)
    
    # Schedule
    scheduled_date = db.Column(db.DateTime, nullable=False)
    pickup_time = db.Column(db.DateTime, nullable=True)
    drop_time = db.Column(db.DateTime, nullable=True)
    
    # Status tracking
    status = db.Column(db.String(20), default='pending')  
    # pending, confirmed, driver_assigned, driver_reached, ongoing, completed, cancelled
    
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, paid, partial
    payment_method = db.Column(db.String(20), nullable=True)  # online, cash, partial
    razorpay_order_id = db.Column(db.String(100), nullable=True)
    razorpay_payment_id = db.Column(db.String(100), nullable=True)
    
    # Ratings
    customer_rating = db.Column(db.Integer, nullable=True)  # 1-5
    customer_feedback = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'customer_id': self.customer_id,
            'driver_id': self.driver_id,
            'pickup': {
                'address': self.pickup_address,
                'latitude': self.pickup_latitude,
                'longitude': self.pickup_longitude,
                'city': self.pickup_city
            },
            'drop': {
                'address': self.drop_address,
                'latitude': self.drop_latitude,
                'longitude': self.drop_longitude,
                'city': self.drop_city
            },
            'goods': {
                'type': self.goods_type,
                'weight_kg': self.weight_kg,
                'volume_cubic_ft': self.volume_cubic_ft,
                'image': self.goods_image,
                'special_instructions': self.special_instructions
            },
            'distance_km': self.distance_km,
            'estimated_fare': self.estimated_fare,
            'final_fare': self.final_fare,
            'admin_commission': self.admin_commission,
            'driver_earning': self.driver_earning,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'pickup_time': self.pickup_time.isoformat() if self.pickup_time else None,
            'drop_time': self.drop_time.isoformat() if self.drop_time else None,
            'status': self.status,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'customer_rating': self.customer_rating,
            'customer_feedback': self.customer_feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Booking {self.booking_id}>'
