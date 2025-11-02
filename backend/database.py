from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db():
    """Initialize database tables"""
    db.create_all()
    print("Database tables created successfully!")

# Helper function to serialize SQLAlchemy objects
def to_dict(obj):
    """Convert SQLAlchemy object to dictionary"""
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
