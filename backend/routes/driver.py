from database import db
from datetime import datetime

class Driver(db.Model):
    __tablename__ = 'drivers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    license_photo = db.Column(db.String(255), nullable=True)
    id_proof_type = db.Column(db.String(50), nullable=True)  # aadhar, pan, etc
    id_proof_number = db.Column(db.String(50), nullable=True)
    id_proof_photo = db.Column(db.String(255), nullable=True)
    service_area = db.Column(db.String(100), nullable=True)  # Hyderabad, Warangal, etc
    status = db.Column(db.String(20), default='offline')  # available, busy, offline
    is_verified = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0.0)
    total_trips = db.Column(db.Integer, default=0)
    total_earnings = db.Column(db.Float, default=0.0)
    wallet_balance = db.Column(db.Float, default=0.0)
    current_latitude = db.Column(db.Float, nullable=True)
    current_longitude = db.Column(db.Float, nullable=True)
    last_location_update = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicles = db.relationship('Vehicle', backref='driver', lazy=True)
    assigned_bookings = db.relationship('Booking', backref='driver', lazy=True, foreign_keys='Booking.driver_id')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'license_number': self.license_number,
            'service_area': self.service_area,
            'status': self.status,
            'is_verified': self.is_verified,
            'rating': self.rating,
            'total_trips': self.total_trips,
            'total_earnings': self.total_earnings,
            'wallet_balance': self.wallet_balance,
            'current_location': {
                'latitude': self.current_latitude,
                'longitude': self.current_longitude
            } if self.current_latitude and self.current_longitude else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Driver {self.license_number}>'
