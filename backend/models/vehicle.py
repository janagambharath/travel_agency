from database import db
from datetime import datetime

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    vehicle_number = db.Column(db.String(50), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)  # DCM, Mini DCM, Large DCM
    capacity_kg = db.Column(db.Integer, nullable=False)  # Weight capacity
    capacity_cubic_ft = db.Column(db.Integer, nullable=True)  # Volume capacity
    vehicle_photo = db.Column(db.String(255), nullable=True)
    rc_book_photo = db.Column(db.String(255), nullable=True)
    insurance_photo = db.Column(db.String(255), nullable=True)
    insurance_expiry = db.Column(db.Date, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'driver_id': self.driver_id,
            'vehicle_number': self.vehicle_number,
            'vehicle_type': self.vehicle_type,
            'capacity_kg': self.capacity_kg,
            'capacity_cubic_ft': self.capacity_cubic_ft,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'insurance_expiry': self.insurance_expiry.isoformat() if self.insurance_expiry else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Vehicle {self.vehicle_number}>'
