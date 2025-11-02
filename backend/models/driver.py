from database import db
from datetime import datetime

class Driver(db.Model):
    __tablename__ = 'drivers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # License and ID
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    license_photo = db.Column(db.String(255), nullable=True)
    license_expiry = db.Column(db.Date, nullable=True)
    
    id_proof_type = db.Column(db.String(50), nullable=True)  # Aadhar, PAN, Voter ID
    id_proof_number = db.Column(db.String(50), nullable=True)
    id_proof_photo = db.Column(db.String(255), nullable=True)
    
    # Service details
    service_area = db.Column(db.String(100), nullable=True)  # City/District
    status = db.Column(db.String(20), default='offline')  # available, busy, offline
    
    # Location tracking
    current_latitude = db.Column(db.Float, nullable=True)
    current_longitude = db.Column(db.Float, nullable=True)
    last_location_update = db.Column(db.DateTime, nullable=True)
    
    # Stats
    total_trips = db.Column(db.Integer, default=0)
    total_earnings = db.Column(db.Float, default=0.0)
    wallet_balance = db.Column(db.Float, default=0.0)
    rating = db.Column(db.Float, default=0.0)  # Average rating
    
    # Verification
    is_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    verified_by = db.Column(db.Integer, nullable=True)  # Admin user ID
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicles = db.relationship('Vehicle', backref='driver', lazy=True)
    bookings = db.relationship('Booking', backref='driver', lazy=True, foreign_keys='Booking.driver_id')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'license_number': self.license_number,
            'license_expiry': self.license_expiry.isoformat() if self.license_expiry else None,
            'id_proof_type': self.id_proof_type,
            'service_area': self.service_area,
            'status': self.status,
            'location': {
                'latitude': self.current_latitude,
                'longitude': self.current_longitude,
                'last_update': self.last_location_update.isoformat() if self.last_location_update else None
            },
            'stats': {
                'total_trips': self.total_trips,
                'total_earnings': self.total_earnings,
                'wallet_balance': self.wallet_balance,
                'rating': self.rating
            },
            'is_verified': self.is_verified,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Driver {self.license_number}>'
